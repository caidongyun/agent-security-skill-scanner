#!/usr/bin/env python3
"""
Quick Benchmark - 快速检测率测试
"""
import json
import sys
from pathlib import Path

# 添加扫描器路径
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'release' / 'v6.1.2publish'))
sys.path.insert(0, str(Path(__file__).parent / 'release' / 'v6.1.2publish' / 'src'))

from engines import PatternEngine, RuleEngine

def load_ground_truth():
    """加载 ground truth"""
    with open('samples/ground_truth.json') as f:
        data = json.load(f)
    return {s['file']: s['label'] for s in data['samples']}

def scan_file(scanner, filepath):
    """扫描单个文件"""
    try:
        result = scanner.scan_file(filepath)
        if result and hasattr(result, 'is_malicious'):
            return result.is_malicious
        if isinstance(result, dict):
            return result.get('is_malicious', False)
        return bool(result)
    except Exception as e:
        print(f"Error scanning {filepath}: {e}")
        return False

def main():
    print("=" * 70)
    print("📊 Quick Benchmark - Scanner v6.1.2")
    print("=" * 70)
    
    # 加载扫描器
    print("\n🔧 加载扫描器...")
    pattern_engine = PatternEngine()
    rules_file = Path('release/v6.1.2publish/rules/dist/all_rules.json')
    if rules_file.exists():
        rule_engine = RuleEngine(rules_file=rules_file)
        print(f"✅ 规则引擎已加载：{rules_file}")
    else:
        rule_engine = None
        print(f"⚠️ 规则文件不存在：{rules_file}")
    
    # 加载 ground truth
    print("\n📁 加载样本...")
    ground_truth = load_ground_truth()
    print(f"✅ 加载 {len(ground_truth)} 个样本")
    
    # 扫描
    print("\n🔍 开始扫描...")
    malicious_total = 0
    malicious_detected = 0
    benign_total = 0
    benign_false_positives = 0
    
    for filepath, true_label in ground_truth.items():
        if not Path(filepath).exists():
            continue
        
        # 读取文件内容并扫描
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            matches = pattern_engine.scan(content)
            is_detected = len(matches) > 0
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            is_detected = False
        
        if true_label == 'malicious':
            malicious_total += 1
            if is_detected:
                malicious_detected += 1
        else:
            benign_total += 1
            if is_detected:
                benign_false_positives += 1
    
    # 计算指标
    detection_rate = malicious_detected / malicious_total if malicious_total > 0 else 0
    false_positive_rate = benign_false_positives / benign_total if benign_total > 0 else 0
    precision = malicious_detected / (malicious_detected + benign_false_positives) if (malicious_detected + benign_false_positives) > 0 else 0
    recall = detection_rate
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    # 输出结果
    print("\n" + "=" * 70)
    print("📈 BENCHMARK RESULTS")
    print("=" * 70)
    print(f"\n📊 OVERALL METRICS")
    print(f"  Total Samples:     {malicious_total + benign_total}")
    print(f"  Malicious:         {malicious_total}")
    print(f"  Benign:            {benign_total}")
    print(f"\n  Detection Rate:    {detection_rate*100:.1f}%")
    print(f"  False Positive:    {false_positive_rate*100:.1f}%")
    print(f"  Precision:         {precision*100:.1f}%")
    print(f"  Recall:            {recall*100:.1f}%")
    print(f"  F1 Score:          {f1:.3f}")
    
    print(f"\n📈 BY ATTACK TYPE")
    # 按攻击类型统计
    attack_types = {}
    for filepath, true_label in ground_truth.items():
        if not Path(filepath).exists():
            continue
        # 从路径提取攻击类型
        parts = Path(filepath).parts
        if 'malicious' in parts:
            idx = parts.index('malicious')
            if idx + 1 < len(parts):
                attack_type = parts[idx + 1]
                if attack_type not in attack_types:
                    attack_types[attack_type] = {'total': 0, 'detected': 0}
                attack_types[attack_type]['total'] += 1
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    matches = pattern_engine.scan(content)
                    is_detected = len(matches) > 0
                except:
                    is_detected = False
                if is_detected:
                    attack_types[attack_type]['detected'] += 1
    
    for attack_type, stats in sorted(attack_types.items()):
        rate = stats['detected'] / stats['total'] if stats['total'] > 0 else 0
        status = "✅" if rate >= 0.95 else "⚠️" if rate >= 0.8 else "🔴"
        print(f"  {status} {attack_type:25s}: {rate*100:5.1f}% ({stats['detected']}/{stats['total']})")
    
    print("\n" + "=" * 70)
    
    # 保存结果
    result = {
        'detection_rate': detection_rate,
        'false_positive_rate': false_positive_rate,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'by_attack_type': {k: {'total': v['total'], 'detected': v['detected'], 'rate': v['detected']/v['total'] if v['total'] > 0 else 0} for k, v in attack_types.items()}
    }
    
    with open('benchmark/quick_benchmark_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    print(f"✅ 结果已保存：benchmark/quick_benchmark_result.json")

if __name__ == '__main__':
    main()
