#!/usr/bin/env python3
"""
🎯 快速验证测试 - 用标注样本测试扫描器
"""

import json
import yaml
from pathlib import Path
import subprocess
import sys

# 样本目录
SAMPLES_DIR = Path('/home/cdy/Desktop/security-benchmark/samples/mitre-atlas')
SCANNER = '/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/ultimate_scanner_v2.py'
RULES_DIR = '/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/rules/scanner_v3/yara'

def load_labeled_samples():
    """加载标注样本"""
    samples = []
    
    for yaml_file in SAMPLES_DIR.rglob('*.yaml'):
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load_all(f)
                for item in data:
                    if isinstance(item, dict) and 'ground_truth' in item:
                        samples.append({
                            'id': item.get('id', 'unknown'),
                            'attack_type': item.get('attack_type', 'unknown'),
                            'language': item.get('language', 'unknown'),
                            'is_malicious': item.get('ground_truth', {}).get('is_malicious', False),
                            'expected_detection': item.get('ground_truth', {}).get('expected_detection', False),
                            'file_path': str(yaml_file)
                        })
        except Exception as e:
            print(f"⚠️  加载失败 {yaml_file}: {e}")
    
    return samples

def run_quick_test():
    """运行快速验证测试"""
    print("=" * 70)
    print("🎯 快速验证测试 - 使用标注样本")
    print("=" * 70)
    
    # 加载标注样本
    print("\n📚 加载标注样本...")
    samples = load_labeled_samples()
    print(f"找到 {len(samples)} 个标注样本")
    
    if not samples:
        print("❌ 未找到标注样本")
        return
    
    # 统计
    malicious_count = sum(1 for s in samples if s['is_malicious'])
    benign_count = len(samples) - malicious_count
    
    print(f"恶意样本：{malicious_count}")
    print(f"良性样本：{benign_count}")
    
    # 按攻击类型统计
    by_attack = {}
    for s in samples:
        attack = s['attack_type']
        if attack not in by_attack:
            by_attack[attack] = 0
        by_attack[attack] += 1
    
    print("\n按攻击类型:")
    for attack, count in sorted(by_attack.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {attack}: {count}")

if __name__ == '__main__':
    run_quick_test()
