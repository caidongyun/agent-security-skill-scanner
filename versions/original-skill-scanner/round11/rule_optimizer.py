#!/usr/bin/env python3
"""
Round 11 - 规则优化器

功能：规则分析、去重、合并、压缩
"""

import os
import json
import yaml
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ============== 配置 ==============

BASE_DIR = Path(__file__).parent.parent
RULES_DIR = BASE_DIR / "rules"
OUTPUT_DIR = BASE_DIR / "round11" / "results"
REPORTS_DIR = BASE_DIR / "round11" / "reports"
OPTIMIZED_DIR = RULES_DIR / "optimized"
ARCHIVE_DIR = RULES_DIR / "archive"

# 确保目录存在
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
OPTIMIZED_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

# ============== 规则加载器 ==============

class RuleLoader:
    """规则加载器"""
    
    def __init__(self, rules_dir):
        self.rules_dir = Path(rules_dir)
        self.rules = []
        self.rules_by_file = defaultdict(list)
    
    def load_all(self):
        """加载所有规则"""
        print("📚 加载检测规则...")
        
        # 跳过 optimized 和 archive 目录
        skip_dirs = {'optimized', 'archive'}
        
        for rule_file in self.rules_dir.glob("*.yaml"):
            if rule_file.parent.name in skip_dirs:
                continue
            
            with open(rule_file) as f:
                try:
                    rule_data = yaml.safe_load(f)
                    if rule_data and 'rules' in rule_data:
                        for rule in rule_data['rules']:
                            rule['source_file'] = rule_file.name
                            rule['source_path'] = str(rule_file)
                            self.rules.append(rule)
                            self.rules_by_file[rule_file.name].append(rule)
                except Exception as e:
                    print(f"  ⚠️  解析失败 {rule_file.name}: {e}")
        
        # 加载 JSON 规则
        for rule_file in self.rules_dir.glob("*.json"):
            if rule_file.parent.name in skip_dirs:
                continue
            
            with open(rule_file) as f:
                try:
                    rule_data = json.load(f)
                    if isinstance(rule_data, list):
                        for rule in rule_data:
                            rule['source_file'] = rule_file.name
                            rule['source_path'] = str(rule_file)
                            self.rules.append(rule)
                            self.rules_by_file[rule_file.name].append(rule)
                    elif isinstance(rule_data, dict) and 'rules' in rule_data:
                        for rule in rule_data['rules']:
                            rule['source_file'] = rule_file.name
                            rule['source_path'] = str(rule_file)
                            self.rules.append(rule)
                            self.rules_by_file[rule_file.name].append(rule)
                except Exception as e:
                    print(f"  ⚠️  解析失败 {rule_file.name}: {e}")
        
        print(f"  ✅ 加载 {len(self.rules)} 条规则")
        print(f"  📁 规则文件：{len(self.rules_by_file)} 个")
        
        return self.rules
    
    def get_rule_signature(self, rule):
        """生成规则签名 (用于去重)"""
        # 提取关键特征
        condition = rule.get('condition', {})
        metadata = rule.get('metadata', {})
        
        # 排序条件以保证一致性
        condition_str = json.dumps(condition, sort_keys=True)
        
        # 生成哈希
        signature = hashlib.md5(condition_str.encode()).hexdigest()[:12]
        
        return signature

# ============== 规则分析器 ==============

class RuleAnalyzer:
    """规则分析器"""
    
    def __init__(self, rules):
        self.rules = rules
        self.analysis = {}
    
    def analyze(self):
        """分析规则"""
        print("\n🔍 分析规则...")
        
        # 按攻击类型分类
        by_type = defaultdict(list)
        for rule in self.rules:
            attack_type = rule.get('metadata', {}).get('attack_type', 'unknown')
            by_type[attack_type].append(rule)
        
        # 按规则类型分类
        by_rule_type = defaultdict(list)
        for rule in self.rules:
            rule_type = rule.get('metadata', {}).get('rule_type', 'unknown')
            by_rule_type[rule_type].append(rule)
        
        # 按严重程度分类
        by_severity = defaultdict(list)
        for rule in self.rules:
            severity = rule.get('metadata', {}).get('severity', 'medium')
            by_severity[severity].append(rule)
        
        # 分析条件类型
        condition_types = defaultdict(int)
        for rule in self.rules:
            condition = rule.get('condition', {})
            if 'contains' in condition:
                condition_types['contains'] += 1
            if 'regex' in condition:
                condition_types['regex'] += 1
            if 'indicators' in condition:
                condition_types['indicators'] += 1
            if 'behaviors' in condition:
                condition_types['behaviors'] += 1
        
        self.analysis = {
            'total_rules': len(self.rules),
            'by_attack_type': {k: len(v) for k, v in by_type.items()},
            'by_rule_type': {k: len(v) for k, v in by_rule_type.items()},
            'by_severity': {k: len(v) for k, v in by_severity.items()},
            'condition_types': dict(condition_types),
            'files_count': len(set(r.get('source_file', '') for r in self.rules)),
        }
        
        # 打印分析结果
        print(f"\n📊 规则分析:")
        print(f"  总规则数：{self.analysis['total_rules']}")
        print(f"  攻击类型：{len(self.analysis['by_attack_type'])} 类")
        print(f"  规则类型：{len(self.analysis['by_rule_type'])} 类")
        print(f"  严重程度：{len(self.analysis['by_severity'])} 级")
        print(f"\n  按攻击类型:")
        for attack_type, count in sorted(self.analysis['by_attack_type'].items()):
            print(f"    {attack_type}: {count}")
        print(f"\n  按条件类型:")
        for cond_type, count in sorted(self.analysis['condition_types'].items()):
            print(f"    {cond_type}: {count}")
        
        return self.analysis

# ============== 规则去重器 ==============

class RuleDeduplicator:
    """规则去重器"""
    
    def __init__(self, rules):
        self.rules = rules
        self.duplicates = []
        self.unique_rules = []
        self.merge_log = []
    
    def deduplicate(self):
        """去重规则"""
        print("\n🔄 执行规则去重...")
        
        seen_signatures = {}
        
        for rule in self.rules:
            # 生成签名
            loader = RuleLoader(Path(__file__).parent.parent / "rules")
            signature = loader.get_rule_signature(rule)
            
            if signature in seen_signatures:
                # 发现重复
                self.duplicates.append({
                    'rule': rule,
                    'original': seen_signatures[signature],
                    'reason': 'condition_duplicate'
                })
                
                # 记录合并日志
                self.merge_log.append({
                    'action': 'merge_duplicate',
                    'duplicate_id': rule.get('id', 'unknown'),
                    'original_id': seen_signatures[signature].get('id', 'unknown'),
                    'timestamp': datetime.now().isoformat(),
                })
            else:
                seen_signatures[signature] = rule
                self.unique_rules.append(rule)
        
        print(f"  原始规则：{len(self.rules)}")
        print(f"  唯一规则：{len(self.unique_rules)}")
        print(f"  重复规则：{len(self.duplicates)}")
        print(f"  压缩率：{(1 - len(self.unique_rules)/len(self.rules))*100:.1f}%")
        
        return self.unique_rules, self.duplicates
    
    def merge_similar_rules(self, rules):
        """合并相似规则"""
        print("\n🔗 合并相似规则...")
        
        # 按攻击类型分组
        by_type = defaultdict(list)
        for rule in rules:
            attack_type = rule.get('metadata', {}).get('attack_type', 'unknown')
            by_type[attack_type].append(rule)
        
        merged_rules = []
        merge_count = 0
        
        for attack_type, type_rules in by_type.items():
            # 按规则类型进一步分组
            by_rule_type = defaultdict(list)
            for rule in type_rules:
                rule_type = rule.get('metadata', {}).get('rule_type', 'unknown')
                by_rule_type[rule_type].append(rule)
            
            for rule_type, rt_rules in by_rule_type.items():
                if len(rt_rules) > 1:
                    # 尝试合并同一类型的规则
                    merged = self._merge_rule_group(rt_rules, attack_type, rule_type)
                    if merged:
                        merged_rules.append(merged)
                        merge_count += len(rt_rules) - 1
                        self.merge_log.append({
                            'action': 'merge_similar',
                            'attack_type': attack_type,
                            'rule_type': rule_type,
                            'merged_count': len(rt_rules),
                            'timestamp': datetime.now().isoformat(),
                        })
                    else:
                        merged_rules.extend(rt_rules)
                else:
                    merged_rules.extend(rt_rules)
        
        print(f"  合并前：{len(rules)}")
        print(f"  合并后：{len(merged_rules)}")
        print(f"  合并规则：{merge_count} 条")
        
        return merged_rules
    
    def _merge_rule_group(self, rules, attack_type, rule_type):
        """合并一组规则"""
        if len(rules) < 2:
            return None
        
        # 合并条件
        merged_condition = {
            'contains': set(),
            'regex': set(),
            'indicators': set(),
            'behaviors': set(),
        }
        
        for rule in rules:
            condition = rule.get('condition', {})
            if 'contains' in condition:
                merged_condition['contains'].update(condition['contains'])
            if 'regex' in condition:
                merged_condition['regex'].update(condition['regex'])
            if 'indicators' in condition:
                merged_condition['indicators'].update(condition['indicators'])
            if 'behaviors' in condition:
                merged_condition['behaviors'].update(condition['behaviors'])
        
        # 清理空集合
        for key in list(merged_condition.keys()):
            if not merged_condition[key]:
                del merged_condition[key]
            else:
                merged_condition[key] = list(merged_condition[key])
        
        # 创建合并后的规则
        first_rule = rules[0]
        merged_rule = {
            'id': f"MERGED-{attack_type[:3].upper()}-{rule_type[:3].upper()}-{len(rules)}in1",
            'name': f"[合并] {first_rule.get('name', 'Unknown')} (+{len(rules)-1} 条)",
            'description': f"合并了 {len(rules)} 条相似规则: " + ", ".join(r.get('id', '?') for r in rules),
            'metadata': {
                'attack_type': attack_type,
                'rule_type': rule_type,
                'severity': max((r.get('metadata', {}).get('severity', 'medium') for r in rules), 
                               key=lambda x: {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}.get(x, 0)),
                'version': '11.0',
                'merged_from': [r.get('id', 'unknown') for r in rules],
            },
            'condition': merged_condition,
            'action': first_rule.get('action', 'alert'),
        }
        
        return merged_rule

# ============== 规则分级器 ==============

class RuleTiering:
    """规则分级器"""
    
    def __init__(self, rules):
        self.rules = rules
        self.tiers = {
            'L1': [],  # 快速过滤
            'L2': [],  # 精确匹配
            'L3': [],  # 行为分析
        }
    
    def tier_rules(self):
        """将规则分级"""
        print("\n📋 规则分级...")
        
        for rule in self.rules:
            tier = self._classify_rule(rule)
            self.tiers[tier].append(rule)
        
        print(f"  L1 (快速过滤): {len(self.tiers['L1'])} 条")
        print(f"  L2 (精确匹配): {len(self.tiers['L2'])} 条")
        print(f"  L3 (行为分析): {len(self.tiers['L3'])} 条")
        
        return self.tiers
    
    def _classify_rule(self, rule):
        """分类规则"""
        condition = rule.get('condition', {})
        
        # L1: 简单字符串匹配
        if 'contains' in condition and len(condition) == 1:
            contains_list = condition['contains']
            if len(contains_list) <= 3:
                return 'L1'
        
        # L2: 正则/指标匹配
        if 'regex' in condition or 'indicators' in condition:
            return 'L2'
        
        # L3: 行为分析/复杂逻辑
        if 'behaviors' in condition or len(condition) > 2:
            return 'L3'
        
        # 默认 L2
        return 'L2'
    
    def save_tiers(self, output_dir):
        """保存分级规则"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for tier_name, tier_rules in self.tiers.items():
            output_file = output_path / f"{tier_name}_rules.yaml"
            
            rule_data = {
                'version': '11.0',
                'tier': tier_name,
                'generated_at': datetime.now().isoformat(),
                'rule_count': len(tier_rules),
                'rules': tier_rules,
            }
            
            with open(output_file, 'w') as f:
                yaml.dump(rule_data, f, allow_unicode=True, default_flow_style=False)
            
            print(f"  ✅ 保存 {tier_name} 规则：{output_file}")

# ============== 主函数 ==============

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Round 11 规则优化器")
    parser.add_argument('--analyze', action='store_true', help='分析规则')
    parser.add_argument('--deduplicate', action='store_true', help='去重规则')
    parser.add_argument('--tier', action='store_true', help='规则分级')
    parser.add_argument('--output', '-o', default=str(OPTIMIZED_DIR), help='输出目录')
    
    args = parser.parse_args()
    
    # 加载规则
    loader = RuleLoader(RULES_DIR)
    rules = loader.load_all()
    
    if args.analyze or not (args.deduplicate or args.tier):
        # 分析规则
        analyzer = RuleAnalyzer(rules)
        analysis = analyzer.analyze()
        
        # 保存分析结果
        analysis_file = OUTPUT_DIR / "rule_analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        print(f"\n📝 分析结果：{analysis_file}")
    
    if args.deduplicate:
        # 去重规则
        deduplicator = RuleDeduplicator(rules)
        unique_rules, duplicates = deduplicator.deduplicate()
        
        # 合并相似规则
        merged_rules = deduplicator.merge_similar_rules(unique_rules)
        
        # 保存去重结果
        dedup_result = {
            'original_count': len(rules),
            'unique_count': len(unique_rules),
            'merged_count': len(merged_rules),
            'duplicate_count': len(duplicates),
            'compression_rate': (1 - len(merged_rules)/len(rules)) * 100 if rules else 0,
            'merge_log': deduplicator.merge_log,
            'timestamp': datetime.now().isoformat(),
        }
        
        result_file = OUTPUT_DIR / "deduplication_result.json"
        with open(result_file, 'w') as f:
            json.dump(dedup_result, f, indent=2, ensure_ascii=False)
        print(f"\n📝 去重结果：{result_file}")
        
        return merged_rules
    
    if args.tier:
        # 规则分级
        tiering = RuleTiering(rules)
        tiers = tiering.tier_rules()
        tiering.save_tiers(args.output)
        
        return rules
    
    return rules

if __name__ == "__main__":
    main()
