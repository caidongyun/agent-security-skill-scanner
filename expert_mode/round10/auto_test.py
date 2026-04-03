#!/usr/bin/env python3
"""
Round 10 - 自动化测试框架

批量测试样本与检测规则的匹配效果
"""

import os
import sys
import json
import yaml
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ============== 配置 ==============

BASE_DIR = Path(__file__).parent.parent
SAMPLES_DIR = BASE_DIR / "samples"
RULES_DIR = BASE_DIR / "rules"
RESULTS_DIR = BASE_DIR / "round10" / "results"
REPORTS_DIR = BASE_DIR / "round10" / "reports"

# 确保输出目录存在
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ============== 规则加载器 ==============

class RuleLoader:
    """规则加载器"""
    
    def __init__(self, rules_dir):
        self.rules_dir = Path(rules_dir)
        self.rules = []
        self.rules_by_type = defaultdict(list)
    
    def load_all(self):
        """加载所有规则"""
        print("📚 加载检测规则...")
        
        # 加载 YAML 规则
        for rule_file in self.rules_dir.glob("*.yaml"):
            with open(rule_file) as f:
                rule_data = yaml.safe_load(f)
                if rule_data and 'rules' in rule_data:
                    for rule in rule_data['rules']:
                        rule['source_file'] = rule_file.name
                        self.rules.append(rule)
                        
                        # 按类型分类
                        attack_type = rule.get('metadata', {}).get('attack_type', 'unknown')
                        self.rules_by_type[attack_type].append(rule)
        
        # 加载 JSON 规则
        for rule_file in self.rules_dir.glob("*.json"):
            with open(rule_file) as f:
                rule_data = json.load(f)
                if isinstance(rule_data, list):
                    for rule in rule_data:
                        rule['source_file'] = rule_file.name
                        self.rules.append(rule)
                        attack_type = rule.get('metadata', {}).get('attack_type', 'unknown')
                        self.rules_by_type[attack_type].append(rule)
                elif isinstance(rule_data, dict) and 'rules' in rule_data:
                    for rule in rule_data['rules']:
                        rule['source_file'] = rule_file.name
                        self.rules.append(rule)
                        attack_type = rule.get('metadata', {}).get('attack_type', 'unknown')
                        self.rules_by_type[attack_type].append(rule)
        
        print(f"  ✅ 加载 {len(self.rules)} 条规则")
        print(f"  📊 威胁类型：{len(self.rules_by_type)} 类")
        
        return self.rules
    
    def get_rules_for_type(self, attack_type):
        """获取指定类型的规则"""
        return self.rules_by_type.get(attack_type, [])

# ============== 样本加载器 ==============

class SampleLoader:
    """样本加载器"""
    
    def __init__(self, samples_dir):
        self.samples_dir = Path(samples_dir)
        self.samples = []
        self.malicious_samples = []
        self.benign_samples = []
    
    def load_all(self):
        """加载所有样本"""
        print("\n📚 加载测试样本...")
        
        # 加载样本索引
        index_file = self.samples_dir / "samples_index.json"
        if index_file.exists():
            with open(index_file) as f:
                index = json.load(f)
                self.samples = index.get('samples', [])
        
        # 分类
        self.malicious_samples = [s for s in self.samples if s.get('severity') != 'none']
        self.benign_samples = [s for s in self.samples if s.get('severity') == 'none']
        
        print(f"  ✅ 总样本：{len(self.samples)}")
        print(f"  🔴 恶意样本：{len(self.malicious_samples)}")
        print(f"  🟢 白样本：{len(self.benign_samples)}")
        
        return self.samples
    
    def load_sample_content(self, sample_meta):
        """加载样本内容"""
        sample_id = sample_meta.get('sample_id')
        if not sample_id:
            return None
        
        # 查找样本文件
        if sample_meta.get('severity') == 'none':
            sample_dir = self.samples_dir / "benign" / sample_id
        else:
            sample_dir = self.samples_dir / "malicious" / sample_id
        
        if not sample_dir.exists():
            return None
        
        # 查找代码文件
        for ext in ['.py', '.sh', '.json', '.js', '.service', '.txt']:
            sample_file = sample_dir / f"{sample_id}{ext}"
            if sample_file.exists():
                with open(sample_file) as f:
                    return f.read()
        
        return None

# ============== 规则引擎 ==============

class RuleEngine:
    """规则引擎 - 简化版匹配"""
    
    def __init__(self, rules):
        self.rules = rules
    
    def match(self, content, sample_meta):
        """
        匹配样本内容
        
        返回：(detected: bool, matched_rules: list, confidence: float)
        """
        matched_rules = []
        
        for rule in self.rules:
            if self._rule_matches(rule, content, sample_meta):
                matched_rules.append(rule)
        
        detected = len(matched_rules) > 0
        confidence = self._calculate_confidence(matched_rules, sample_meta)
        
        return detected, matched_rules, confidence
    
    def _rule_matches(self, rule, content, sample_meta):
        """检查规则是否匹配"""
        # 检查条件
        conditions = rule.get('condition', {})
        
        # 简单字符串匹配
        if 'contains' in conditions:
            for pattern in conditions['contains']:
                if pattern.lower() in content.lower():
                    return True
        
        # 正则匹配
        if 'regex' in conditions:
            import re
            for pattern in conditions['regex']:
                if re.search(pattern, content, re.IGNORECASE):
                    return True
        
        # 指标匹配
        if 'indicators' in conditions:
            sample_indicators = sample_meta.get('indicators', [])
            for indicator in conditions['indicators']:
                if indicator in sample_indicators:
                    return True
        
        # 行为匹配
        if 'behaviors' in conditions:
            sample_behaviors = sample_meta.get('behaviors', [])
            for behavior in conditions['behaviors']:
                if behavior in sample_behaviors:
                    return True
        
        return False
    
    def _calculate_confidence(self, matched_rules, sample_meta):
        """计算置信度"""
        if not matched_rules:
            return 0.0
        
        # 基于规则数量和严重程度计算
        base_confidence = min(0.5 + len(matched_rules) * 0.1, 0.95)
        
        # 严重程度加成
        severity = sample_meta.get('severity', 'medium')
        severity_bonus = {
            'critical': 0.05,
            'high': 0.03,
            'medium': 0.02,
            'low': 0.01,
        }.get(severity, 0)
        
        return min(base_confidence + severity_bonus, 0.99)

# ============== 测试执行器 ==============

class TestExecutor:
    """测试执行器"""
    
    def __init__(self, rule_engine, sample_loader):
        self.rule_engine = rule_engine
        self.sample_loader = sample_loader
        self.results = []
        self.stats = defaultdict(lambda: {
            'total': 0,
            'detected': 0,
            'missed': 0,
            'false_positives': 0,
            'true_negatives': 0,
        })
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "=" * 60)
        print("🧪 执行自动化测试")
        print("=" * 60)
        
        # 测试恶意样本 (检测率)
        print("\n🔴 测试恶意样本...")
        for sample_meta in self.sample_loader.malicious_samples:
            result = self._test_sample(sample_meta, expect_malicious=True)
            self.results.append(result)
            
            attack_type = sample_meta.get('attack_type', 'unknown')
            self.stats[attack_type]['total'] += 1
            if result['detected']:
                self.stats[attack_type]['detected'] += 1
            else:
                self.stats[attack_type]['missed'] += 1
        
        # 测试白样本 (误报率)
        print("\n🟢 测试白样本...")
        for sample_meta in self.sample_loader.benign_samples:
            result = self._test_sample(sample_meta, expect_malicious=False)
            self.results.append(result)
            
            sample_type = sample_meta.get('sample_type', 'unknown')
            self.stats[sample_type]['total'] += 1
            if not result['detected']:
                self.stats[sample_type]['true_negatives'] += 1
            else:
                self.stats[sample_type]['false_positives'] += 1
        
        return self.results
    
    def _test_sample(self, sample_meta, expect_malicious=True):
        """测试单个样本"""
        sample_id = sample_meta.get('sample_id', 'unknown')
        
        # 加载样本内容
        content = self.sample_loader.load_sample_content(sample_meta)
        if not content:
            return {
                'sample_id': sample_id,
                'status': 'error',
                'error': '无法加载样本内容',
            }
        
        # 执行匹配
        start_time = time.time()
        detected, matched_rules, confidence = self.rule_engine.match(content, sample_meta)
        elapsed_ms = (time.time() - start_time) * 1000
        
        # 判断结果
        if expect_malicious:
            correct = detected
            result_type = 'true_positive' if detected else 'false_negative'
        else:
            correct = not detected
            result_type = 'true_negative' if not detected else 'false_positive'
        
        result = {
            'sample_id': sample_id,
            'attack_type': sample_meta.get('attack_type') or sample_meta.get('sample_type'),
            'severity': sample_meta.get('severity', 'none'),
            'detected': detected,
            'matched_rules_count': len(matched_rules),
            'matched_rule_ids': [r.get('id', 'unknown') for r in matched_rules[:5]],
            'confidence': confidence,
            'correct': correct,
            'result_type': result_type,
            'elapsed_ms': round(elapsed_ms, 2),
            'timestamp': datetime.now().isoformat(),
        }
        
        # 打印进度
        status_icon = "✅" if correct else "❌"
        print(f"  {status_icon} {sample_id}: {'检测到' if detected else '未检测'} ({len(matched_rules)} 条规则, {elapsed_ms:.1f}ms)")
        
        return result
    
    def calculate_stats(self):
        """计算统计信息"""
        total_samples = len(self.results)
        correct_results = len([r for r in self.results if r.get('correct', False)])
        
        # 恶意样本统计
        malicious_results = [r for r in self.results if r.get('severity') != 'none']
        true_positives = len([r for r in malicious_results if r.get('detected', False)])
        false_negatives = len([r for r in malicious_results if not r.get('detected', False)])
        detection_rate = true_positives / len(malicious_results) if malicious_results else 0
        
        # 白样本统计
        benign_results = [r for r in self.results if r.get('severity') == 'none']
        true_negatives = len([r for r in benign_results if not r.get('detected', False)])
        false_positives = len([r for r in benign_results if r.get('detected', False)])
        false_positive_rate = false_positives / len(benign_results) if benign_results else 0
        
        # 性能统计
        elapsed_times = [r.get('elapsed_ms', 0) for r in self.results if r.get('elapsed_ms')]
        avg_elapsed = sum(elapsed_times) / len(elapsed_times) if elapsed_times else 0
        p99_elapsed = sorted(elapsed_times)[int(len(elapsed_times) * 0.99)] if len(elapsed_times) > 100 else max(elapsed_times) if elapsed_times else 0
        
        stats = {
            'summary': {
                'total_samples': total_samples,
                'correct_results': correct_results,
                'accuracy': round(correct_results / total_samples, 4) if total_samples else 0,
                'test_timestamp': datetime.now().isoformat(),
            },
            'detection': {
                'malicious_samples': len(malicious_results),
                'true_positives': true_positives,
                'false_negatives': false_negatives,
                'detection_rate': round(detection_rate, 4),
                'detection_rate_percent': f"{detection_rate * 100:.2f}%",
            },
            'false_positive': {
                'benign_samples': len(benign_results),
                'true_negatives': true_negatives,
                'false_positives': false_positives,
                'false_positive_rate': round(false_positive_rate, 4),
                'false_positive_rate_percent': f"{false_positive_rate * 100:.2f}%",
            },
            'performance': {
                'avg_elapsed_ms': round(avg_elapsed, 2),
                'p99_elapsed_ms': round(p99_elapsed, 2),
            },
            'by_type': {},
        }
        
        # 按类型统计
        for attack_type, type_stats in self.stats.items():
            if type_stats['total'] > 0:
                detected = type_stats['detected']
                stats['by_type'][attack_type] = {
                    'total': type_stats['total'],
                    'detected': detected,
                    'missed': type_stats['missed'],
                    'detection_rate': round(detected / type_stats['total'], 4) if type_stats['total'] else 0,
                }
        
        return stats

# ============== 报告生成器 ==============

class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, results, stats, output_dir):
        self.results = results
        self.stats = stats
        self.output_dir = Path(output_dir)
    
    def generate_markdown_report(self):
        """生成 Markdown 报告"""
        report_path = self.output_dir / "ROUND10_TEST_REPORT.md"
        
        content = f"""# 🔬 Round 10 - 自动化测试报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**样本总数**: {self.stats['summary']['total_samples']}  
**测试类型**: 批量自动化测试

---

## 📊 核心指标

| 指标 | 值 | 目标 | 状态 |
|------|-----|------|------|
| **检测率** | {self.stats['detection']['detection_rate_percent']} | ≥95% | {'✅' if self.stats['detection']['detection_rate'] >= 0.95 else '🔴'} |
| **误报率** | {self.stats['false_positive']['false_positive_rate_percent']} | <5% | {'✅' if self.stats['false_positive']['false_positive_rate'] < 0.05 else '🔴'} |
| **准确率** | {self.stats['summary']['accuracy'] * 100:.2f}% | ≥95% | {'✅' if self.stats['summary']['accuracy'] >= 0.95 else '🔴'} |
| **平均耗时** | {self.stats['performance']['avg_elapsed_ms']:.1f}ms | <50ms | {'✅' if self.stats['performance']['avg_elapsed_ms'] < 50 else '🔴'} |

---

## 🎯 检测结果

### 恶意样本检测

| 类别 | 样本数 | 检出数 | 漏报数 | 检测率 |
|------|--------|--------|--------|--------|
"""
        
        # 恶意样本按类型统计
        for attack_type, type_stats in sorted(self.stats['by_type'].items()):
            if type_stats['detected'] > 0 or type_stats['missed'] > 0:
                rate = type_stats['detection_rate'] * 100
                icon = '✅' if rate >= 95 else '⚠️'
                content += f"| {attack_type} | {type_stats['total']} | {type_stats['detected']} | {type_stats['missed']} | {rate:.1f}% {icon} |\n"
        
        content += f"""
### 白样本误报

| 类别 | 样本数 | 正确 | 误报 | 误报率 |
|------|--------|------|------|--------|
"""
        
        # 白样本统计
        benign_results = [r for r in self.results if r.get('severity') == 'none']
        benign_by_type = defaultdict(lambda: {'total': 0, 'correct': 0, 'false_positive': 0})
        
        for result in benign_results:
            sample_type = result.get('attack_type', 'unknown')
            benign_by_type[sample_type]['total'] += 1
            if not result.get('detected', False):
                benign_by_type[sample_type]['correct'] += 1