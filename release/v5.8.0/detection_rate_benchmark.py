#!/usr/bin/env python3
"""
v5.8.0 检测率 Benchmark

对标真实攻击样本，计算每种攻击类型的检出率
用法:
    python3 detection_rate_benchmark.py [--attack-type TYPE] [--limit N]
"""

import sys
import json
import time
from pathlib import Path
from collections import defaultdict

# 导入 v5.8.0 Scanner
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from engines import Scanner


BENCHMARK_INDEX = "/home/cdy/Desktop/security-benchmark/samples-index/payload-index.json"
SAMPLES_BASE = "/home/cdy/Desktop/security-benchmark"


def load_benchmark_index():
    """加载样本索引"""
    with open(BENCHMARK_INDEX, 'r') as f:
        return json.load(f)


def run_detection_benchmark(attack_types=None, limit_per_type=500, verbose=False):
    """运行检测率 benchmark
    
    Args:
        attack_types: 要测试的攻击类型列表，None 表示全部
        limit_per_type: 每种类型最多测试样本数
        verbose: 是否显示详细信息
    """
    print("=" * 70)
    print("v5.8.0 检测率 Benchmark")
    print("=" * 70)
    
    # 加载索引
    index_data = load_benchmark_index()
    payloads = index_data['payloads']
    attack_type_counts = index_data['attack_types']
    
    # 按攻击类型分组
    by_type = defaultdict(list)
    for p in payloads:
        by_type[p['attack_type']].append(p)
    
    # 确定要测试的类型
    if attack_types:
        types_to_test = attack_types
    else:
        types_to_test = list(by_type.keys())
    
    # 初始化 Scanner
    scanner = Scanner()
    
    results_summary = {}
    total_samples = 0
    total_detected = 0
    
    print(f"\n📊 测试配置:")
    print(f"  样本索引: {BENCHMARK_INDEX}")
    print(f"  样本基准: {SAMPLES_BASE}")
    print(f"  每类型限制: {limit_per_type}")
    print(f"  测试类型: {len(types_to_test)}")
    print()
    
    for attack_type in sorted(types_to_test):
        samples = by_type[attack_type][:limit_per_type]
        if not samples:
            continue
        
        detected = 0
        false_negatives = []  # 漏检的样本
        
        type_start = time.time()
        
        for sample in samples:
            sample_path = Path(SAMPLES_BASE) / sample['path']
            
            if not sample_path.exists():
                if verbose:
                    print(f"  ⚠️ 样本不存在: {sample_path}")
                continue
            
            try:
                result = scanner.scan_file(sample_path)  # Pass Path object, not string
                
                if result.is_malicious or result.score >= 50:
                    detected += 1
                else:
                    false_negatives.append({
                        'path': sample['path'],
                        'sample_id': sample['sample_id'],
                        'score': result.score
                    })
            except Exception as e:
                if verbose:
                    print(f"  ⚠️ 扫描失败: {sample_path} - {e}")
        
        detection_rate = (detected / len(samples)) * 100 if samples else 0
        elapsed = time.time() - type_start
        
        results_summary[attack_type] = {
            'total': len(samples),
            'detected': detected,
            'missed': len(samples) - detected,
            'detection_rate': detection_rate,
            'elapsed': elapsed,
            'false_negatives': false_negatives[:10]  # 只保留前10个漏检样本
        }
        
        total_samples += len(samples)
        total_detected += detected
        
        # 打印进度
        status = "✅" if detection_rate >= 95 else "⚠️" if detection_rate >= 80 else "🔴"
        print(f"  {status} {attack_type:25s}: {detection_rate:6.1f}% ({detected:4d}/{len(samples):4d})")
    
    # 汇总
    overall_rate = (total_detected / total_samples) * 100 if total_samples else 0
    
    print()
    print("=" * 70)
    print("📊 汇总结果")
    print("=" * 70)
    print(f"  总样本数: {total_samples}")
    print(f"  总检出: {total_detected}")
    print(f"  总体检出率: {overall_rate:.1f}%")
    print()
    
    # 按检出率排序
    sorted_types = sorted(results_summary.items(), key=lambda x: x[1]['detection_rate'])
    
    print("🔴 需要优化的攻击类型 (检出率 < 95%):")
    for atype, data in sorted_types:
        if data['detection_rate'] < 95:
            print(f"  - {atype}: {data['detection_rate']:.1f}% ({data['detected']}/{data['total']})")
    
    print()
    print("✅ 已达标的攻击类型 (检出率 >= 95%):")
    for atype, data in sorted_types:
        if data['detection_rate'] >= 95:
            print(f"  - {atype}: {data['detection_rate']:.1f}% ({data['detected']}/{data['total']})")
    
    # 保存详细报告
    report_file = Path(__file__).parent / "reports" / f"detection_rate_{time.strftime('%Y%m%d_%H%M%S')}.json"
    report_file.parent.mkdir(exist_ok=True)
    
    report = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'config': {
            'limit_per_type': limit_per_type,
            'attack_types_tested': types_to_test
        },
        'overall': {
            'total_samples': total_samples,
            'total_detected': total_detected,
            'overall_detection_rate': overall_rate
        },
        'by_attack_type': results_summary
    }
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 详细报告已保存: {report_file}")
    
    return results_summary


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="v5.8.0 检测率 Benchmark")
    parser.add_argument("--attack-type", "-t", action="append", help="指定攻击类型 (可多次)")
    parser.add_argument("--limit", "-l", type=int, default=500, help="每类型样本数 (默认500)")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细信息")
    
    args = parser.parse_args()
    
    run_detection_benchmark(
        attack_types=args.attack_type,
        limit_per_type=args.limit,
        verbose=args.verbose
    )