#!/usr/bin/env python3
"""
Resource Exhaustion 检测能力验证
验证新创建的 YARA 规则对样本的检测率
"""

import os
import sys
import time
import statistics
from pathlib import Path

try:
    import yara
except ImportError:
    print("❌ 需要安装 yara-python: pip3 install yara-python")
    sys.exit(1)

SAMPLE_DIR = "samples/malicious/resource_exhaustion"
RULES_DIR = "rules/yara"

def load_rules():
    """加载所有 YARA 规则"""
    print("📋 加载 YARA 规则...")
    rules_content = ""
    # 只加载优化规则
    rule_files = list(Path(RULES_DIR).glob("resource_exhaustion_optimized.yar"))
    
    if not rule_files:
        # 如果没有优化规则，加载原来的规则
        rule_files = list(Path(RULES_DIR).glob("resource_exhaustion*.yar"))
    
    if not rule_files:
        print(f"❌ 未找到规则文件：{RULES_DIR}/resource_exhaustion*.yar")
        return None
    
    for rf in rule_files:
        rules_content += rf.read_text(errors='ignore') + "\n\n"
    
    print(f"   ✅ 加载 {len(rule_files)} 条规则")
    
    try:
        rules = yara.compile(source=rules_content)
        print("   ✅ 规则编译成功")
        return rules
    except Exception as e:
        print(f"❌ 规则编译失败：{e}")
        return None

def load_samples():
    """加载所有样本"""
    print("\n📂 加载样本...")
    samples = []
    
    sample_path = Path(SAMPLE_DIR)
    if not sample_path.exists():
        print(f"❌ 样本目录不存在：{SAMPLE_DIR}")
        return []
    
    for f in sample_path.glob("*.txt"):
        samples.append(f)
    
    print(f"   ✅ 加载 {len(samples)} 个样本")
    return samples

def scan_sample(rules, sample_path):
    """扫描单个样本"""
    content = sample_path.read_text(errors='ignore')
    
    start = time.perf_counter()
    matches = rules.match(data=content)
    elapsed = (time.perf_counter() - start) * 1000  # ms
    
    detected = len(matches) > 0
    matched_rules = [m.rule for m in matches]
    
    return {
        'file': sample_path.name,
        'detected': detected,
        'rules': matched_rules,
        'time_ms': elapsed
    }

def main():
    print("=" * 60)
    print("🔍 Resource Exhaustion 检测能力验证")
    print("=" * 60)
    
    # 加载规则
    rules = load_rules()
    if not rules:
        sys.exit(1)
    
    # 加载样本
    samples = load_samples()
    if not samples:
        sys.exit(1)
    
    # 扫描所有样本
    print("\n🚀 开始扫描...")
    results = []
    scan_times = []
    
    for sample in samples:
        result = scan_sample(rules, sample)
        results.append(result)
        scan_times.append(result['time_ms'])
    
    # 统计结果
    detected_count = sum(1 for r in results if r['detected'])
    missed_count = len(results) - detected_count
    detection_rate = (detected_count / len(results)) * 100 if results else 0
    
    avg_time = statistics.mean(scan_times) if scan_times else 0
    p99_time = sorted(scan_times)[int(len(scan_times) * 0.99)] if len(scan_times) > 1 else avg_time
    
    print("\n" + "=" * 60)
    print("📊 检测结果")
    print("=" * 60)
    
    print(f"\n✅ 检测成功：{detected_count}/{len(results)} ({detection_rate:.1f}%)")
    print(f"❌ 漏报：{missed_count}/{len(results)} ({100-detection_rate:.1f}%)")
    
    print(f"\n⚡ 性能指标")
    print(f"   平均耗时：{avg_time:.2f} ms")
    print(f"   P99 耗时：{p99_time:.2f} ms")
    
    # 显示漏报样本
    if missed_count > 0:
        print(f"\n⚠️  漏报样本:")
        for r in results:
            if not r['detected']:
                print(f"   - {r['file']}")
    
    # 显示规则匹配统计
    print(f"\n📋 规则匹配统计:")
    rule_stats = {}
    for r in results:
        for rule in r['rules']:
            rule_stats[rule] = rule_stats.get(rule, 0) + 1
    
    for rule, count in sorted(rule_stats.items(), key=lambda x: -x[1]):
        print(f"   {rule}: {count} 次")
    
    # 生成报告
    report = {
        'total_samples': len(results),
        'detected': detected_count,
        'missed': missed_count,
        'detection_rate': detection_rate,
        'avg_time_ms': avg_time,
        'p99_time_ms': p99_time,
        'rule_stats': rule_stats,
        'status': 'PASS' if detection_rate >= 95 else 'NEEDS_IMPROVEMENT'
    }
    
    print("\n" + "=" * 60)
    if detection_rate >= 98:
        print("✅ 检测能力：优秀 (≥98%)")
    elif detection_rate >= 95:
        print("✅ 检测能力：良好 (≥95%)")
    elif detection_rate >= 90:
        print("⚠️  检测能力：需要改进 (≥90%)")
    else:
        print("❌ 检测能力：不足 (<90%)")
    print("=" * 60)
    
    # 保存报告
    import json
    report_file = "reports/resource_exhaustion_detection_report.json"
    Path("reports").mkdir(exist_ok=True)
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 报告已保存：{report_file}")
    
    return report

if __name__ == "__main__":
    main()
