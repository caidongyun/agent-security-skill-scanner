#!/usr/bin/env python3
"""
Round 13 - 规则生成器

从样本自动提取特征并生成检测规则
"""

import os
import re
import json
import yaml
from pathlib import Path
from datetime import datetime
from collections import Counter

BASE_DIR = Path(__file__).parent.parent
SAMPLES_DIR = BASE_DIR / "samples"
RULES_DIR = BASE_DIR / "rules" / "optimized"

# ============== 特征提取器 ==============

class FeatureExtractor:
    """从样本提取特征"""
    
    def __init__(self):
        # 恶意模式
        self.malicious_patterns = {
            'network': [
                r'requests\.(get|post)\(',
                r'urllib\.request',
                r'curl\s+',
                r'wget\s+',
                r'socket\.connect',
            ],
            'execution': [
                r'subprocess\.',
                r'os\.system',
                r'eval\s*\(',
                r'exec\s*\(',
                r'Popen\s*\(',
            ],
            'file_ops': [
                r'open\s*\([^)]*["\'][rw]',
                r'os\.path\.expanduser',
                r'\.ssh/',
                r'\.aws/',
            ],
            'obfuscation': [
                r'base64\.(b64encode|b64decode)',
                r'eval\s*\(.*base64',
                r'chr\s*\(\s*\d+\s*\)',
            ],
            'persistence': [
                r'\.bashrc',
                r'crontab',
                r'systemd',
                r'/etc/init',
            ],
        }
    
    def extract_from_sample(self, sample_path: Path) -> dict:
        """从样本文件提取特征"""
        features = {
            'patterns': [],
            'indicators': [],
            'behaviors': [],
            'severity': 'medium',
        }
        
        # 读取样本内容
        sample_file = sample_path / 'sample.py'
        if not sample_file.exists():
            sample_file = sample_path / 'sample.js'
        if not sample_file.exists():
            return features
        
        with open(sample_file) as f:
            content = f.read()
        
        # 提取模式
        for category, patterns in self.malicious_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    features['patterns'].append({
                        'category': category,
                        'pattern': pattern,
                    })
        
        # 提取指标
        urls = re.findall(r'https?://[^\s"\')]+', content)
        if urls:
            features['indicators'].extend(urls)
        
        ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', content)
        if ips:
            features['indicators'].extend(ips)
        
        # 提取行为
        if any('subprocess' in p['pattern'] for p in features['patterns']):
            features['behaviors'].append('subprocess_spawn')
        if any('requests' in p['pattern'] or 'curl' in p['pattern'] for p in features['patterns']):
            features['behaviors'].append('network_request')
        if any('.ssh' in p['pattern'] or '.aws' in p['pattern'] for p in features['patterns']):
            features['behaviors'].append('file_access')
        
        # 评估严重程度
        if len(features['patterns']) >= 5:
            features['severity'] = 'critical'
        elif len(features['patterns']) >= 3:
            features['severity'] = 'high'
        
        return features

# ============== 规则生成器 ==============

class RuleGenerator:
    """规则生成器"""
    
    def __init__(self):
        self.extractor = FeatureExtractor()
        self.generated_rules = []
    
    def generate_from_samples(self, attack_type: str) -> list:
        """从指定攻击类型的样本生成规则"""
        sample_dir = SAMPLES_DIR / "malicious" / attack_type
        
        if not sample_dir.exists():
            print(f"  ⚠️  样本目录不存在：{sample_dir}")
            return []
        
        print(f"\n📋 从 [{attack_type}] 生成规则...")
        
        # 收集所有特征
        all_features = []
        for sample_path in sample_dir.iterdir():
            if sample_path.is_dir():
                features = self.extractor.extract_from_sample(sample_path)
                if features['patterns']:
                    all_features.append(features)
        
        print(f"  分析 {len(all_features)} 个样本")
        
        # 生成规则
        rules = self._generate_rules(attack_type, all_features)
        
        return rules
    
    def _generate_rules(self, attack_type: str, features_list: list) -> list:
        """基于特征生成规则"""
        rules = []
        
        # 统计最常见模式
        pattern_counter = Counter()
        for features in features_list:
            for pattern_info in features['patterns']:
                pattern_counter[pattern_info['pattern']] += 1
        
        # 生成 L1 规则 (简单字符串匹配)
        l1_rules = self._generate_l1_rules(attack_type, pattern_counter)
        rules.extend(l1_rules)
        print(f"  ✅ 生成 {len(l1_rules)} 条 L1 规则")
        
        # 生成 L2 规则 (正则匹配)
        l2_rules = self._generate_l2_rules(attack_type, pattern_counter)
        rules.extend(l2_rules)
        print(f"  ✅ 生成 {len(l2_rules)} 条 L2 规则")
        
        # 生成 L3 规则 (行为分析)
        l3_rules = self._generate_l3_rules(attack_type, features_list)
        rules.extend(l3_rules)
        print(f"  ✅ 生成 {len(l3_rules)} 条 L3 规则")
        
        return rules
    
    def _generate_l1_rules(self, attack_type: str, pattern_counter: Counter) -> list:
        """生成 L1 快速规则"""
        rules = []
        
        # 常见恶意字符串
        l1_patterns = [
            ('curl', 'bash', 'shell'),
            ('wget', '-O', '|'),
            ('eval', 'exec'),
            ('subprocess', 'system'),
            ('requests', 'post', 'get'),
            ('.ssh', 'id_rsa'),
            ('.aws', 'credentials'),
            ('base64', 'decode'),
        ]
        
        for i, patterns in enumerate(l1_patterns):
            rule = {
                'id': f'R13-L1-{attack_type[:3].upper()}-{i:03d}',
                'name': f'[L1] {attack_type} 快速检测 #{i}',
                'metadata': {
                    'attack_type': attack_type,
                    'rule_type': 'l1_fast',
                    'tier': 'L1',
                    'severity': 'medium',
                    'version': '13.0',
                },
                'condition': {
                    'contains': list(patterns),
                },
                'action': 'alert',
            }
            rules.append(rule)
        
        return rules
    
    def _generate_l2_rules(self, attack_type: str, pattern_counter: Counter) -> list:
        """生成 L2 精确规则"""
        rules = []
        
        # 基于频率生成正则规则
        top_patterns = pattern_counter.most_common(10)
        
        for i, (pattern, count) in enumerate(top_patterns):
            rule = {
                'id': f'R13-L2-{attack_type[:3].upper()}-{i:03d}',
                'name': f'[L2] {attack_type} 正则检测 #{i} (覆盖{count}样本)',
                'metadata': {
                    'attack_type': attack_type,
                    'rule_type': 'l2_regex',
                    'tier': 'L2',
                    'severity': 'high',
                    'version': '13.0',
                    'coverage': count,
                },
                'condition': {
                    'regex': [pattern],
                },
                'action': 'alert',
            }
            rules.append(rule)
        
        return rules
    
    def _generate_l3_rules(self, attack_type: str, features_list: list) -> list:
        """生成 L3 行为规则"""
        rules = []
        
        # 收集所有行为
        all_behaviors = set()
        for features in features_list:
            all_behaviors.update(features['behaviors'])
        
        # 生成行为组合规则
        behavior_combos = [
            ['subprocess_spawn', 'network_request'],
            ['file_access', 'network_request'],
            ['subprocess_spawn', 'file_access'],
        ]
        
        for i, combo in enumerate(behavior_combos):
            if all(b in all_behaviors for b in combo):
                rule = {
                    'id': f'R13-L3-{attack_type[:3].upper()}-{i:03d}',
                    'name': f'[L3] {attack_type} 行为检测 #{i}',
                    'metadata': {
                        'attack_type': attack_type,
                        'rule_type': 'l3_behavior',
                        'tier': 'L3',
                        'severity': 'critical',
                        'version': '13.0',
                    },
                    'condition': {
                        'behaviors': combo,
                        'sequence': False,
                    },
                    'action': 'alert',
                }
                rules.append(rule)
        
        return rules

# ============== 规则保存 ==============

def save_rules(rules: list, tier: str):
    """保存规则到文件"""
    tier_rules = [r for r in rules if r['metadata']['tier'] == tier]
    
    if not tier_rules:
        return
    
    output_file = RULES_DIR / f'{tier}_rules_r13.yaml'
    
    data = {
        'version': '13.0',
        'tier': tier,
        'generated_at': datetime.now().isoformat(),
        'rule_count': len(tier_rules),
        'rules': tier_rules,
    }
    
    with open(output_file, 'w') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    
    print(f"  💾 保存 {tier} 规则：{output_file}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Round 13 规则生成器')
    parser.add_argument('--attack-type', choices=['all'] + [
        'tool_poisoning', 'remote_load', 'data_exfil',
        'prompt_injection', 'resource_exhaustion', 'memory_pollution'
    ], default='all')
    parser.add_argument('--merge', action='store_true', help='合并到现有规则')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📜 Round 13 - 规则生成")
    print("=" * 60)
    
    generator = RuleGenerator()
    all_rules = []
    
    attack_types = [
        'tool_poisoning', 'remote_load', 'data_exfil',
        'prompt_injection', 'resource_exhaustion', 'memory_pollution'
    ]
    
    if args.attack_type != 'all':
        attack_types = [args.attack_type]
    
    for attack_type in attack_types:
        rules = generator.generate_from_samples(attack_type)
        all_rules.extend(rules)
    
    # 保存规则
    print("\n💾 保存规则...")
    save_rules(all_rules, 'L1')
    save_rules(all_rules, 'L2')
    save_rules(all_rules, 'L3')
    
    print("\n" + "=" * 60)
    print(f"✅ 规则生成完成：{len(all_rules)} 条")
    print(f"📁 位置：{RULES_DIR}")
    print("=" * 60)

if __name__ == '__main__':
    main()
