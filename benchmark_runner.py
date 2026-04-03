#!/usr/bin/env python3
"""
🛡️ Security Benchmark 专用扫描器
==================================
功能:
- 分批扫描大规模样本库
- 自动生成 Benchmark 报告
- 对比多个扫描器结果
- 支持断点续传
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

@dataclass
class BenchmarkResult:
    scanner_name: str
    total_samples: int
    malicious_count: int
    benign_count: int
    detection_rate: float
    scan_time_seconds: float
    avg_time_ms: float
    by_language: Dict
    timestamp: str

def find_sample_files(base_dir: str, batch_size: int = 100) -> List[List[str]]:
    """分批查找样本文件（支持标准和非标准扩展名）"""
    base_path = Path(base_dir)
    
    # 标准扩展名
    standard_exts = {'.py', '.js', '.sh', '.ps1', '.bat', '.cmd', '.vbs', '.lua', '.go'}
    
    # 非标准扩展名 (security-benchmark 特有)
    nonstandard_exts = {'.python', '.javascript', '.bash', '.shell', '.powershell'}
    
    all_files = []
    
    # 查找标准扩展名
    for ext in standard_exts:
        all_files.extend([str(f) for f in base_path.rglob(f"*{ext}")])
    
    # 查找非标准扩展名
    for ext in nonstandard_exts:
        all_files.extend([str(f) for f in base_path.rglob(f"*{ext}")])
        all_files.extend([str(f) for f in base_path.rglob(f"payload{ext}")])
    
    # 去重
    all_files = list(set(all_files))
    
    # 分批
    batches = []
    for i in range(0, len(all_files), batch_size):
        batches.append(all_files[i:i+batch_size])
    
    return batches, len(all_files)

def scan_with_scanner(scanner_name: str, sample_files: List[str], 
                     rules_dir: str, workers: int = 4) -> Dict:
    """使用指定扫描器扫描"""
    print(f"\n🔍 使用 {scanner_name} 扫描 {len(sample_files)} 个样本...")
    
    if scanner_name == "ultimate_v2":
        from ultimate_scanner_v2 import UltimateScannerV2
        scanner = UltimateScannerV2(rules_dir)
        
        start = time.perf_counter()
        results = []
        
        for file_path in sample_files:
            try:
                result = scanner.scan_file(file_path)
                results.append(result)
            except Exception as e:
                print(f"⚠️  扫描错误 {file_path}: {e}")
        
        total_time = time.perf_counter() - start
        
        malicious = sum(1 for r in results if r.is_malicious)
        by_language = {}
        for r in results:
            if r.language not in by_language:
                by_language[r.language] = {'total': 0, 'malicious': 0}
            by_language[r.language]['total'] += 1
            if r.is_malicious:
                by_language[r.language]['malicious'] += 1
        
        return {
            'scanner': scanner_name,
            'total': len(results),
            'malicious': malicious,
            'benign': len(results) - malicious,
            'detection_rate': malicious / len(results) if results else 0,
            'time': total_time,
            'avg_time': statistics.mean([r.scan_time_ms for r in results]) if results else 0,
            'by_language': by_language
        }
    
    elif scanner_name == "ultimate_v1":
        from ultimate_scanner import UltimateScanner
        scanner = UltimateScanner(rules_dir)
        
        start = time.perf_counter()
        results, total_time = scanner.scan_directory(
            Path(sample_files[0]).parent if sample_files else '.',
            workers=workers
        )
        
        malicious = sum(1 for r in results if r.is_malicious)
        return {
            'scanner': scanner_name,
            'total': len(results),
            'malicious': malicious,
            'benign': len(results) - malicious,
            'detection_rate': malicious / len(results) if results else 0,
            'time': total_time,
            'avg_time': statistics.mean([r.scan_time_ms for r in results]) if results else 0,
            'by_language': {}
        }
    
    return {}

def run_benchmark(base_dir: str, rules_dir: str, output_dir: str,
                 batch_size: int = 100, workers: int = 4,
                 scanners: List[str] = None):
    """运行完整 Benchmark"""
    if scanners is None:
        scanners = ['ultimate_v2', 'ultimate_v1']
    
    print("=" * 70)
    print("🛡️  Security Benchmark - 大规模样本扫描")
    print("=" * 70)
    print(f"📂 样本目录：{base_dir}")
    print(f"📚 规则目录：{rules_dir}")
    print(f"💾 输出目录：{output_dir}")
    print(f"📦 批次大小：{batch_size}")
    print(f"⚡ 并发数：{workers}")
    print()
    
    # 查找样本
    batches, total_files = find_sample_files(base_dir, batch_size)
    print(f"📊 发现 {total_files} 个样本文件，分为 {len(batches)} 批")
    print()
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 存储所有结果
    all_results = []
    batch_results = []
    
    # 逐批扫描
    for i, batch in enumerate(batches):
        print(f"\n{'='*70}")
        print(f"📦 批次 {i+1}/{len(batches)} - {len(batch)} 个样本")
        print(f"{'='*70}")
        
        batch_result = {
            'batch': i+1,
            'total_batches': len(batches),
            'samples': len(batch),
            'scanners': {}
        }
        
        # 对每个扫描器
        for scanner_name in scanners:
            try:
                result = scan_with_scanner(scanner_name, batch, rules_dir, workers)
                batch_result['scanners'][scanner_name] = result
                all_results.append({
                    'batch': i+1,
                    'scanner': scanner_name,
                    **result
                })
                
                # 显示结果
                print(f"\n  {scanner_name}:")
                print(f"    总样本：{result.get('total', 0)}")
                print(f"    恶意：{result.get('malicious', 0)}")
                print(f"    检测率：{result.get('detection_rate', 0)*100:.1f}%")
                print(f"    耗时：{result.get('time', 0):.3f}秒")
                
            except Exception as e:
                print(f"\n  ❌ {scanner_name} 失败：{e}")
                batch_result['scanners'][scanner_name] = {'error': str(e)}
        
        batch_results.append(batch_result)
        
        # 保存中间结果
        temp_file = output_path / f"batch_{i+1:03d}_result.json"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(batch_result, f, indent=2, ensure_ascii=False)
    
    # 生成总报告
    print("\n" + "=" * 70)
    print("📊 生成 Benchmark 总报告")
    print("=" * 70)
    
    final_report = {
        'timestamp': datetime.now().isoformat(),
        'base_dir': base_dir,
        'rules_dir': rules_dir,
        'total_samples': total_files,
        'total_batches': len(batches),
        'batch_size': batch_size,
        'scanners': scanners,
        'batch_results': batch_results,
        'summary': {}
    }
    
    # 汇总每个扫描器的结果
    for scanner_name in scanners:
        scanner_results = [r for r in all_results if r.get('scanner') == scanner_name]
        if scanner_results:
            total_malicious = sum(r.get('malicious', 0) for r in scanner_results)
            total_samples = sum(r.get('total', 0) for r in scanner_results)
            total_time = sum(r.get('time', 0) for r in scanner_results)
            
            final_report['summary'][scanner_name] = {
                'total_samples': total_samples,
                'malicious': total_malicious,
                'detection_rate': total_malicious / total_samples if total_samples > 0 else 0,
                'total_time_seconds': round(total_time, 3),
                'avg_time_ms': round(statistics.mean([r.get('avg_time', 0) for r in scanner_results]), 3)
            }
    
    # 保存总报告
    report_file = output_path / f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)
    
    # 显示摘要
    print("\n" + "=" * 70)
    print("📊 Benchmark 摘要")
    print("=" * 70)
    print(f"总样本数：{total_files}")
    print(f"总批次数：{len(batches)}")
    print()
    
    for scanner_name, summary in final_report['summary'].items():
        print(f"{scanner_name}:")
        print(f"  检测率：{summary['detection_rate']*100:.1f}%")
        print(f"  恶意样本：{summary['malicious']}/{summary['total_samples']}")
        print(f"  总耗时：{summary['total_time_seconds']:.3f}秒")
        print(f"  平均耗时：{summary['avg_time_ms']:.3f}ms/样本")
        print()
    
    print(f"💾 报告已保存：{report_file}")
    print("=" * 70)
    
    return final_report

def main():
    parser = argparse.ArgumentParser(description='🛡️ Security Benchmark 专用扫描器')
    parser.add_argument('--samples', default='/home/cdy/Desktop/security-benchmark',
                       help='样本目录')
    parser.add_argument('--rules', default='rules/scanner_v3/yara',
                       help='规则目录')
    parser.add_argument('--output', default='reports/benchmark',
                       help='输出目录')
    parser.add_argument('--batch-size', type=int, default=100,
                       help='每批样本数')
    parser.add_argument('--workers', type=int, default=4,
                       help='并发数')
    parser.add_argument('--scanners', nargs='+', default=['ultimate_v2'],
                       choices=['ultimate_v2', 'ultimate_v1'],
                       help='使用的扫描器')
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    rules_dir = script_dir / args.rules if not Path(args.rules).is_absolute() else Path(args.rules)
    output_dir = script_dir / args.output if not Path(args.output).is_absolute() else Path(args.output)
    
    run_benchmark(
        args.samples,
        str(rules_dir),
        str(output_dir),
        args.batch_size,
        args.workers,
        args.scanners
    )

if __name__ == '__main__':
    main()
