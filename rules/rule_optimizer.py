#!/usr/bin/env python3
"""
Security Scanner Rule Optimizer v6.2.0

功能:
1. 标准化 severity (全部大写)
2. 修复 category (中文→英文映射)
3. 补全缺失字段
4. 分类整理规则库
5. 生成优化报告
"""

import json
import os
from pathlib import Path
from datetime import datetime


# 中文 category → 英文映射
CATEGORY_MAP = {
    '命令执行': 'command_injection',
    '代码执行': 'arbitrary_execution',
    '数据泄露': 'data_exfiltration',
    '凭据窃取': 'credential_theft',
    '权限提升': 'privilege_escalation',
    '持久化': 'persistence',
    '内网渗透': 'lateral_movement',
    '远程代码执行': 'remote_code_execution',
    '权限滥用': 'broad_permissions',
    '未知': 'unknown',
}

# Severity 标准化映射
SEVERITY_MAP = {
    'CRITICAL': 'CRITICAL',
    'HIGH': 'HIGH',
    'MEDIUM': 'MEDIUM',
    'LOW': 'LOW',
    'SAFE': 'LOW',
    'critical': 'CRITICAL',
    'high': 'HIGH',
    'medium': 'MEDIUM',
    'low': 'LOW',
    'error': 'CRITICAL',    # error → CRITICAL
    'warning': 'MEDIUM',    # warning → MEDIUM
    'INFO': 'LOW',
    'info': 'LOW',
    'MISSING': 'MEDIUM',   # 缺失 → MEDIUM
    '': 'MEDIUM',
}


def normalize_severity(sev: str) -> str:
    """标准化 severity"""
    if not sev:
        return 'MEDIUM'
    return SEVERITY_MAP.get(sev.upper().strip(), 'MEDIUM')


def normalize_category(cat: str) -> str:
    """标准化 category"""
    if not cat:
        return 'unknown'
    cat = cat.strip()
    if cat in CATEGORY_MAP:
        return CATEGORY_MAP[cat]
    # 如果已经是英文，直接返回
    if cat.replace('_', '').isalpha():
        return cat.lower()
    return 'unknown'


def get_risk_weight(level: str) -> int:
    """获取风险权重"""
    weights = {
        'CRITICAL': 100,
        'HIGH': 75,
        'MEDIUM': 50,
        'LOW': 25,
    }
    return weights.get(level.upper(), 50)


class RuleOptimizer:
    """规则优化器"""
    
    def __init__(self, rules_file: str):
        self.rules_file = rules_file
        self.rules_data = None
        self.optimized_rules = []
        self.stats = {
            'total': 0,
            'severity_fixed': 0,
            'category_fixed': 0,
            'deduplicated': 0,
            'by_category': {},
            'by_severity': {},
            'by_source': {},
        }
    
    def load(self):
        """加载规则文件"""
        with open(self.rules_file, 'r', encoding='utf-8') as f:
            self.rules_data = json.load(f)
        print(f"✅ 加载了 {len(self.rules_data['rules'])} 条规则")
    
    def optimize(self):
        """优化规则"""
        seen_ids = set()
        new_rules = []
        
        for rule in self.rules_data['rules']:
            self.stats['total'] += 1
            
            # 1. 标准化 severity
            old_sev = rule.get('severity', 'MISSING')
            new_sev = normalize_severity(old_sev)
            if old_sev != new_sev:
                self.stats['severity_fixed'] += 1
            rule['severity'] = new_sev
            
            # 2. 标准化 category
            old_cat = rule.get('category', '')
            new_cat = normalize_category(old_cat)
            if old_cat != new_cat:
                self.stats['category_fixed'] += 1
            rule['category'] = new_cat
            
            # 3. 添加默认字段
            rule.setdefault('min_matches', 1)
            rule.setdefault('confidence', 80)
            rule.setdefault('enabled', True)
            
            # 4. 去重 (基于 rule ID)
            rule_id = rule.get('id', '')
            if rule_id and rule_id not in seen_ids:
                seen_ids.add(rule_id)
                new_rules.append(rule)
            else:
                self.stats['deduplicated'] += 1
            
            # 5. 统计
            cat = rule.get('category', 'unknown')
            sev = rule.get('severity', 'MEDIUM')
            src = rule.get('source', 'unknown').split('/')[0]
            
            self.stats['by_category'][cat] = self.stats['by_category'].get(cat, 0) + 1
            self.stats['by_severity'][sev] = self.stats['by_severity'].get(sev, 0) + 1
            self.stats['by_source'][src] = self.stats['by_source'].get(src, 0) + 1
        
        self.optimized_rules = new_rules
        print(f"✅ 优化完成: {len(self.optimized_rules)} 条有效规则")
    
    def save(self, output_file: str = None):
        """保存优化后的规则"""
        if not output_file:
            output_file = self.rules_file.replace('.json', '_optimized.json')
        
        # 构建输出
        output = {
            'version': self.rules_data.get('version', 'unknown'),
            'build_date': datetime.now().strftime('%Y-%m-%d'),
            'total_rules': len(self.optimized_rules),
            'optimization_stats': self.stats,
            'rules': self.optimized_rules
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 保存到: {output_file}")
        return output_file
    
    def print_report(self):
        """打印优化报告"""
        print()
        print("=" * 60)
        print("📊 规则优化报告")
        print("=" * 60)
        
        print(f"\n📈 总体统计:")
        print(f"   总规则数: {self.stats['total']}")
        print(f"   有效规则: {len(self.optimized_rules)}")
        print(f"   Severity 修复: {self.stats['severity_fixed']}")
        print(f"   Category 修复: {self.stats['category_fixed']}")
        print(f"   去重数量: {self.stats['deduplicated']}")
        
        print(f"\n🔢 风险等级分布:")
        for sev, count in sorted(self.stats['by_severity'].items(), 
                                  key=lambda x: -x[1]):
            pct = count / len(self.optimized_rules) * 100
            bar = '█' * int(pct / 5)
            print(f"   {sev:10s}: {count:4d} ({pct:5.1f}%) {bar}")
        
        print(f"\n📂 规则分类 (Top 10):")
        for cat, count in sorted(self.stats['by_category'].items(), 
                                  key=lambda x: -x[1])[:10]:
            pct = count / len(self.optimized_rules) * 100
            bar = '█' * int(pct / 3)
            print(f"   {cat:25s}: {count:4d} ({pct:5.1f}%) {bar}")
        
        print(f"\n📦 规则来源:")
        for src, count in sorted(self.stats['by_source'].items(), 
                                  key=lambda x: -x[1]):
            pct = count / len(self.optimized_rules) * 100
            print(f"   {src:20s}: {count:4d} ({pct:5.1f}%)")
        
        print()
        print("=" * 60)


def generate_category_report(rules: list) -> dict:
    """生成规则分类报告"""
    report = {
        'execution': [],      # 代码执行类
        'data': [],           # 数据安全类
        'network': [],        # 网络安全类
        'persistence': [],    # 持久化类
        'privilege': [],      # 权限类
        'credential': [],     # 凭据类
        'model': [],          # AI/模型类
        'supply_chain': [],   # 供应链类
        'other': []           # 其他
    }
    
    category_groups = {
        'execution': ['arbitrary_execution', 'command_injection', 'remote_code_execution', 
                      'code_execution', 'exec'],
        'data': ['data_exfiltration', 'data_leak', 'collection'],
        'network': ['network_access', 'c2_communication', 'reverse_shell', 
                    'remote_load', 'insecure_transport'],
        'persistence': ['persistence', 'persistence_mechanism'],
        'privilege': ['privilege_escalation', 'broad_permissions'],
        'credential': ['credential_theft', 'credential_harvesting', 'credential_leak'],
        'model': ['prompt_injection', 'memory_pollution', 'model_poisoning', 
                  'model_backdoor', 'rag_poisoning', 'jailbreak', 'adversarial_examples',
                  'model_extraction', 'model_inversion'],
        'supply_chain': ['supply_chain_attack', 'supply_chain', 'typosquatting', 
                         'npm_script_abuse', 'tool_poisoning'],
    }
    
    for rule in rules:
        cat = rule.get('category', 'unknown')
        grouped = False
        for group, cats in category_groups.items():
            if cat in cats:
                report[group].append(rule)
                grouped = True
                break
        if not grouped:
            report['other'].append(rule)
    
    return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Security Scanner Rule Optimizer')
    parser.add_argument('--input', '-i', required=True, help='输入规则文件')
    parser.add_argument('--output', '-o', help='输出文件 (默认: 输入_optimized.json)')
    parser.add_argument('--no-backup', action='store_true', help='不创建备份')
    args = parser.parse_args()
    
    # 备份原文件
    if not args.no_backup:
        backup_file = args.input + '.bak'
        import shutil
        shutil.copy2(args.input, backup_file)
        print(f"📦 备份到: {backup_file}")
    
    # 优化
    optimizer = RuleOptimizer(args.input)
    optimizer.load()
    optimizer.optimize()
    output_file = optimizer.save(args.output)
    optimizer.print_report()
    
    # 生成分类报告
    print("\n📋 规则分类报告:")
    report = generate_category_report(optimizer.optimized_rules)
    for group, rules in report.items():
        if rules:
            print(f"\n   [{group.upper()}] {len(rules)} 条规则")
            top_rules = sorted(rules, key=lambda x: -get_risk_weight(x.get('severity', 'MEDIUM')))[:3]
            for r in top_rules:
                print(f"      - {r['id']}: {r.get('name', '?')} ({r.get('severity', '?')})")


if __name__ == '__main__':
    main()
