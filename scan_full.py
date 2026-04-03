#!/usr/bin/env python3
"""
🛡️ 终极全量扫描器 - 最高检测能力
使用完整 YARA 规则目录 (342+ 条) 扫描所有样本
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

import yara as yara_lib

@dataclass
class ScanResult:
    sample_path: str
    is_malicious: bool
    matched_rules: List[str]
    scan_time_ms: float

def load_all_rules(rules_dir: str) -> yara_lib.Rules:
    """加载目录下所有 YARA 规则"""
    rules_path = Path(rules_dir)
    if not rules_path.exists():
        raise FileNotFoundError(f"规则目录不存在：{rules_path}")
    
    # 编译所有 .yar 文件
    yar_files = list(rules_path.glob("*.yar"))
    if not yar_files:
        raise FileNotFoundError(f"规则目录中没有 .yar 文件：{rules_path}")
    
    print(f"📚 加载 {len(yar_files)} 个规则文件...")
    
    # 合并所有规则
    all_rules = ""
    for yar_file in yar_files:
        try:
            content = yar_file.read_text(encoding='utf-8')
            all_rules += content + "\n\n"
        except Exception as e:
            print(f"⚠️  跳过文件 {yar_file.name}: {e}")
    
    # 编译规则
    rules = yara_lib.compile(source=all_rules)
    print(f"✅ 编译完成：{len(yar_files)} 个文件")
    
    return rules

def scan_sample(rules: yara_lib.Rules, sample_path: str) -> ScanResult:
    """扫描单个样本"""
    start = time.perf_counter()
    
    try:
        matches = rules.match(sample_path)
        is_malicious = len(matches) > 0
        matched_rules = [m.rule for m in matches]
    except Exception as e:
        is_malicious = False
        matched_rules = []
    
    duration = (time.perf_counter() - start) * 1000
    
    return ScanResult(
        sample_path=str(sample_path),
        is_malicious=is_malicious,
        matched_rules=matched_rules,
        scan_time_ms=duration
    )

def scan_directory(rules: yara_lib.Rules, samples_dir: str, workers: int = 8) -> Tuple[List[ScanResult], float]:
    """并发扫描目录"""
    samples_path = Path(samples_dir)
    if not samples_path.exists():
        raise FileNotFoundError(f"样本目录不存在：{samples_path}")
    
    # 收集所有样本文件
    extensions = {'.py', '.js', '.sh', '.ps1', '.bat', '.cmd', '.vbs', '.lua'}
    sample_files = []
    for ext in extensions:
        sample_files.extend(samples_path.rglob(f"*{ext}"))
    
    # 去重
    sample_files = list(set(sample_files))
    
    print(f"📂 找到 {len(sample_files)} 个样本文件")
    print(f"⚡ 启动 {workers} 线程并发扫描...")
    
    start_time = time.perf_counter()
    results = []
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(scan_sample, rules, str(f)): f for f in sample_files}
        
        for i, future in enumerate(as_completed(futures)):
            try:
                result = future.result()
                results.append(result)
                
                if (i + 1) % 100 == 0:
                    print(f"  已扫描 {i+1}/{len(sample_files)} ...")
            except Exception as e:
                print(f"⚠️  扫描错误：{e}")
    
    total_time = time.perf_counter() - start_time
    return results, total_time

def generate_report(results: List[ScanResult], total_time: float, output_file: str):
    """生成扫描报告"""
    total = len(results)
    malicious = sum(1 for r in results if r.is_malicious)
    benign = total - malicious
    
    detection_rate = malicious / total if total > 0 else 0
    avg_time = statistics.mean([r.scan_time_ms for r in results]) if results else 0
    
    # 统计规则匹配次数
    rule_counts = {}
    for r in results:
        for rule in r.matched_rules:
            rule_counts[rule] = rule_counts.get(rule, 0) + 1
    
    # 排序
    top_rules = sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_samples": total,
        "malicious_count": malicious,
        "benign_count": benign,
        "detection_rate": detection_rate,
        "detection_rate_percent": f"{detection_rate * 100:.1f}%",
        "scan_time_seconds": round(total_time, 3),
        "avg_time_ms": round(avg_time, 3),
        "throughput_samples_per_sec": round(total / total_time, 1) if total_time > 0 else 0,
        "top_matched_rules": dict(top_rules),
        "results": [asdict(r) for r in results]
    }
    
    # 保存 JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # 显示摘要
    print("\n" + "=" * 70)
    print("📊 扫描结果")
    print("=" * 70)
    print(f"✅ 扫描样本：{total} 个")
    print(f"🔴 恶意样本：{malicious} ({detection_rate * 100:.1f}%)")
    print(f"🟢 安全样本：{benign} ({(1 - detection_rate) * 100:.1f}%)")
    print(f"⚡ 扫描耗时：{total_time:.3f} 秒")
    print(f"⚡ 平均耗时：{avg_time:.3f} ms/样本")
    print(f"⚡ 吞吐量：{total / total_time:.1f} 样本/秒")
    
    if top_rules:
        print("\n📋 Top 10 规则匹配:")
        for rule, count in top_rules[:10]:
            print(f"   {rule}: {count} 次")
    
    print(f"\n💾 报告已保存：{output_file}")
    
    # 评估
    print("\n" + "=" * 70)
    if detection_rate >= 0.95:
        print("✅ 检测能力：优秀 (≥95%)")
    elif detection_rate >= 0.90:
        print("✅ 检测能力：良好 (≥90%)")
    elif detection_rate >= 0.80:
        print("⚠️  检测能力：一般 (≥80%)")
    else:
        print("❌ 检测能力：不足 (<80%)")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(description='🛡️ 终极全量扫描器')
    parser.add_argument('--samples', default='samples', help='样本目录')
    parser.add_argument('--rules', default='rules/scanner_v3/yara', help='规则目录')
    parser.add_argument('--output', default=None, help='输出报告文件')
    parser.add_argument('--workers', type=int, default=8, help='并发数')
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    samples_dir = script_dir / args.samples if not Path(args.samples).is_absolute() else Path(args.samples)
    rules_dir = script_dir / args.rules if not Path(args.rules).is_absolute() else Path(args.rules)
    
    output_file = args.output or f"reports/ultimate_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    print("=" * 70)
    print("🛡️  终极全量扫描器 - 最高检测能力")
    print("=" * 70)
    print(f"📂 样本目录：{samples_dir}")
    print(f"📚 规则目录：{rules_dir}")
    print(f"💾 输出文件：{output_file}")
    print()
    
    # 加载规则
    rules = load_all_rules(str(rules_dir))
    
    # 扫描
    results, total_time = scan_directory(rules, str(samples_dir), args.workers)
    
    # 生成报告
    generate_report(results, total_time, output_file)

if __name__ == '__main__':
    main()
