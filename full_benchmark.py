#!/usr/bin/env python3
"""
Full Benchmark - 完整检测率测试
包含恶意样本 + 良性样本
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

# 添加扫描器路径
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'release' / 'v6.1.2publish'))
sys.path.insert(0, str(Path(__file__).parent / 'release' / 'v6.1.2publish' / 'src'))

from engines import PatternEngine, RuleEngine

def load_ground_truth():
    """加载 ground truth"""
    # 优先使用 v2 (包含良性样本)
    gt_file = 'samples/ground_truth_v2.json' if Path('samples/ground_truth_v2.json').exists() else 'samples/ground_truth.json'
    with open(gt_file) as f:
        data = json.load(f)
    print(f"  使用：{gt_file}")
    
    samples = {}
    for s in data['samples']:
        samples[s['file']] = {
            'label': s['label'],
            'attack_type': s.get('attack_type', 'unknown')
        }
    return samples

def scan_content(pattern_engine, content):
    """扫描内容"""
    try:
        matches = pattern_engine.scan(content)
        return len(matches) > 0
    except Exception as e:
        return False

def main():
    print("=" * 80)
    print("📊 Full Benchmark - Scanner v6.1.2")
    print("=" * 80)
    
    # 加载扫描器
    print("\n🔧 加载扫描器...")
    pattern_engine = PatternEngine()
    rules_file = Path('release/v6.1.2publish/rules/dist/all_rules.json')
    if rules_file.exists():
        rule_engine = RuleEngine(rules_file=rules_file)
        print(f"✅ PatternEngine 已加载")
        print(f"✅ RuleEngine: {len(rule_engine.rules)} rules")
    else:
        print(f"⚠️ 规则文件不存在：{rules_file}")
        rule_engine = None
    
    # 加载 ground truth
    print("\n📁 加载样本...")
    ground_truth = load_ground_truth()
    print(f"✅ 加载 {len(ground_truth)} 个样本")
    
    # 扫描所有样本
    print("\n🔍 开始扫描...")
    
    # 统计
    stats = {
        'malicious': {'total': 0, 'detected': 0, 'by_type': defaultdict(lambda: {'total': 0, 'detected': 0})},
        'benign': {'total': 0, 'false_positives': 0}
    }
    
    missed_files = []
    
    for filepath, info in ground_truth.items():
        filepath = Path(filepath)
        if not filepath.exists():
            continue
        
        # 读取并扫描
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            is_detected = scan_content(pattern_engine, content)
        except Exception as e:
            print(f"⚠️ 读取失败 {filepath}: {e}")
            is_detected = False
        
        if info['label'] == 'malicious':
            stats['malicious']['total'] += 1
            attack_type = info['attack_type']
            stats['malicious']['by_type'][attack_type]['total'] += 1
            
            if is_detected:
                stats['malicious']['detected'] += 1
                stats['malicious']['by_type'][attack_type]['detected'] += 1
            else:
                missed_files.append((filepath, attack_type))
        else:
            stats['benign']['total'] += 1
            if is_detected:
                stats['benign']['false_positives'] += 1
    
    # 计算指标
    mal_total = stats['malicious']['total']
    mal_detected = stats['malicious']['detected']
    ben_total = stats['benign']['total']
    ben_fp = stats['benign']['false_positives']
    
    detection_rate = mal_detected / mal_total if mal_total > 0 else 0
    false_positive_rate = ben_fp / ben_total if ben_total > 0 else 0
    precision = mal_detected / (mal_detected + ben_fp) if (mal_detected + ben_fp) > 0 else 0
    recall = detection_rate
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    # 输出结果
    print("\n" + "=" * 80)
    print("📈 BENCHMARK RESULTS")
    print("=" * 80)
    
    print(f"\n📊 OVERALL METRICS")
    print(f"  Total Samples:     {mal_total + ben_total}")
    print(f"  Malicious:         {mal_total}")
    print(f"  Benign:            {ben_total}")
    print(f"\n  🎯 Detection Rate:    {detection_rate*100:.1f}%  ({mal_detected}/{mal_total})")
    print(f"  ⚠️  False Positive:    {false_positive_rate*100:.1f}%  ({ben_fp}/{ben_total})")
    print(f"  📈 Precision:         {precision*100:.1f}%")
    print(f"  📉 Recall:            {recall*100:.1f}%")
    print(f"  🎯 F1 Score:          {f1:.3f}")
    
    print(f"\n📈 BY ATTACK TYPE")
    print(f"  {'Attack Type':<25s} {'Rate':>8s} {'Detected':>12s} {'Total':>8s} {'Status':>10s}")
    print("  " + "-"*25 + " " + "-"*8 + " " + "-"*12 + " " + "-"*8 + " " + "-"*10)
    
    for attack_type, type_stats in sorted(stats['malicious']['by_type'].items()):
        rate = type_stats['detected'] / type_stats['total'] if type_stats['total'] > 0 else 0
        status = "✅" if rate >= 0.95 else "⚠️" if rate >= 0.8 else "🔴"
        print(f"  {attack_type:<25s} {rate*100:7.1f}% {type_stats['detected']:>6d} {type_stats['total']:>8d} {status:>10s}")
    
    # 显示漏检的文件
    if missed_files:
        print(f"\n🔴 MISSED FILES ({len(missed_files)}):")
        by_type = defaultdict(list)
        for filepath, attack_type in missed_files:
            by_type[attack_type].append(filepath)
        
        for attack_type, files in sorted(by_type.items()):
            print(f"\n  {attack_type} ({len(files)}):")
            for f in files[:5]:  # 只显示前 5 个
                print(f"    - {f}")
            if len(files) > 5:
                print(f"    ... 还有 {len(files) - 5} 个")
    
    # 保存结果
    result = {
        'timestamp': str(Path('benchmark').stat().st_mtime if Path('benchmark').exists() else ''),
        'scanner_version': 'v6.1.2',
        'overall': {
            'total_samples': mal_total + ben_total,
            'malicious_total': mal_total,
            'benign_total': ben_total,
            'detection_rate': detection_rate,
            'false_positive_rate': false_positive_rate,
            'precision': precision,
            'recall': recall,
            'f1_score': f1
        },
        'by_attack_type': {
            k: {
                'total': v['total'],
                'detected': v['detected'],
                'rate': v['detected'] / v['total'] if v['total'] > 0 else 0
            } for k, v in stats['malicious']['by_type'].items()
        },
        'missed_files': [(str(f), at) for f, at in missed_files]
    }
    
    # 保存 JSON
    with open('benchmark/full_benchmark_v6.1.2.json', 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n✅ 结果已保存：benchmark/full_benchmark_v6.1.2.json")
    
    # 保存 Markdown 报告
    with open('benchmark/FULL_BENCHMARK_V6.1.2_REPORT.md', 'w') as f:
        f.write("# 📊 Full Benchmark Report - Scanner v6.1.2\n\n")
        f.write(f"**检测率**: {detection_rate*100:.1f}%  \n")
        f.write(f"**误报率**: {false_positive_rate*100:.1f}%  \n")
        f.write(f"**F1 Score**: {f1:.3f}\n\n")
        
        f.write("## 按攻击类型\n\n")
        f.write("| 攻击类型 | 检测率 | 检出数 | 总数 | 状态 |\n")
        f.write("|---------|--------|--------|------|------|\n")
        for attack_type, type_stats in sorted(stats['malicious']['by_type'].items()):
            rate = type_stats['detected'] / type_stats['total'] if type_stats['total'] > 0 else 0
            status = "✅" if rate >= 0.95 else "⚠️" if rate >= 0.8 else "🔴"
            f.write(f"| {attack_type} | {rate*100:.1f}% | {type_stats['detected']} | {type_stats['total']} | {status} |\n")
        
        if missed_files:
            f.write(f"\n## 漏检文件 ({len(missed_files)})\n\n")
            for filepath, attack_type in missed_files[:20]:
                f.write(f"- `{filepath}` ({attack_type})\n")
    
    print(f"✅ 报告已保存：benchmark/FULL_BENCHMARK_V6.1.2_REPORT.md")
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()
