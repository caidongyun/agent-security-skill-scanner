#!/usr/bin/env python3
"""
Round 15 - 样本与规则质量验证

验证所有样本的检测率、误报率、性能指标
"""

import os
import sys
import json
import yaml
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent
SAMPLES_DIR = BASE_DIR / "samples"
RULES_DIR = BASE_DIR / "rules" / "optimized"
RESULTS_DIR = BASE_DIR / "round15" / "results"
REPORTS_DIR = BASE_DIR / "round15" / "reports"

# 创建输出目录
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# 质量目标
QUALITY_TARGETS = {
    'detection_rate': 0.98,      # ≥98%
    'false_positive_rate': 0.02, # <2%
    'p99_latency': 0.005,        # <5ms
}

class RuleMatcher:
    """规则匹配引擎（简化版）"""
    
    def __init__(self):
        self.rules = []
        self.load_rules()
    
    def load_rules(self):
        """加载所有规则"""
        self.rules = []
        for rule_file in RULES_DIR.glob("*.yaml"):
            try:
                with open(rule_file) as f:
                    data = yaml.safe_load(f)
                if data and 'rules' in data:
                    for rule in data['rules']:
                        rule['source_file'] = str(rule_file)
                        self.rules.append(rule)
            except Exception as e:
                print(f"⚠️  规则文件加载失败：{rule_file.name} - {e}")
        
        print(f"📚 加载规则：{len(self.rules)} 条")
    
    def match(self, content: str) -> List[Dict]:
        """匹配内容"""
        matched_rules = []
        
        for rule in self.rules:
            condition = rule.get('condition', {})
            
            # L1: contains 匹配
            if 'contains' in condition:
                for pattern in condition['contains']:
                    if pattern.lower() in content.lower():
                        matched_rules.append(rule)
                        break
            
            # L2: regex 匹配
            elif 'regex' in condition:
                import re
                for pattern in condition['regex']:
                    try:
                        if re.search(pattern, content, re.IGNORECASE):
                            matched_rules.append(rule)
                            break
                    except:
                        pass
            
            # L3: behavior 匹配（简化）
            elif 'behaviors' in condition:
                # 简化处理：检查是否包含相关关键词
                for behavior in condition['behaviors']:
                    if behavior in content.lower():
                        matched_rules.append(rule)
                        break
        
        return matched_rules

class QualityValidator:
    """质量验证器"""
    
    def __init__(self):
        self.matcher = RuleMatcher()
        self.results = {
            'round': 15,
            'timestamp': datetime.now().isoformat(),
            'samples_tested': 0,
            'detection_results': [],
            'metrics': {},
            'issues': [],
            'passed': False,
        }
    
    def validate_all(self):
        """验证所有样本"""
        print("\n" + "="*60)
        print("🔍 Round 15 - 质量验证")
        print("="*60)
        
        # 1. 验证恶意样本（检测率）
        self._validate_malicious_samples()
        
        # 2. 验证白样本（误报率）
        self._validate_benign_samples()
        
        # 3. 性能测试
        self._benchmark_performance()
        
        # 4. 计算指标
        self._calculate_metrics()
        
        # 5. 评估
        self._evaluate()
        
        # 6. 生成报告
        self._generate_reports()
        
        return self.results
    
    def _validate_malicious_samples(self):
        """验证恶意样本检测率"""
        print("\n📦 验证恶意样本...")
        
        malicious_dir = SAMPLES_DIR / "malicious"
        true_positives = 0
        false_negatives = 0
        total = 0
        
        for attack_dir in malicious_dir.iterdir():
            if not attack_dir.is_dir():
                continue
            
            for sample_dir in attack_dir.iterdir():
                if not sample_dir.is_dir():
                    continue
                
                total += 1
                
                # 读取样本
                sample_file = sample_dir / "sample.py"
                if not sample_file.exists():
                    continue
                
                with open(sample_file) as f:
                    content = f.read()
                
                # 匹配规则
                start = time.time()
                matched = self.matcher.match(content)
                match_time = time.time() - start
                
                # 记录结果
                detected = len(matched) > 0
                if detected:
                    true_positives += 1
                else:
                    false_negatives += 1
                    self.results['issues'].append(
                        f"漏报：{sample_dir.name} ({attack_dir.name})"
                    )
                
                self.results['detection_results'].append({
                    'sample_id': sample_dir.name,
                    'attack_type': attack_dir.name,
                    'detected': detected,
                    'rules_matched': len(matched),
                    'match_time_ms': match_time * 1000,
                })
        
        print(f"  总计：{total} 个")
        print(f"  检出：{true_positives} 个")
        print(f"  漏报：{false_negatives} 个")
        
        self.results['malicious_stats'] = {
            'total': total,
            'true_positives': true_positives,
            'false_negatives': false_negatives,
        }
    
    def _validate_benign_samples(self):
        """验证白样本误报率"""
        print("\n📦 验证白样本...")
        
        benign_dir = SAMPLES_DIR / "benign"
        true_negatives = 0
        false_positives = 0
        total = 0
        
        if not benign_dir.exists():
            print("  ⚠️  白样本目录不存在，跳过")
            return
        
        for sample_dir in benign_dir.iterdir():
            if not sample_dir.is_dir():
                continue
            
            total += 1
            
            # 读取样本
            sample_file = sample_dir / "sample.py"
            if not sample_file.exists():
                continue
            
            with open(sample_file) as f:
                content = f.read()
            
            # 匹配规则
            matched = self.matcher.match(content)
            
            # 记录结果
            if len(matched) == 0:
                true_negatives += 1
            else:
                false_positives += 1
                self.results['issues'].append(
                    f"误报：{sample_dir.name} (匹配 {len(matched)} 规则)"
                )
        
        print(f"  总计：{total} 个")
        print(f"  正确：{true_negatives} 个")
        print(f"  误报：{false_positives} 个")
        
        self.results['benign_stats'] = {
            'total': total,
            'true_negatives': true_negatives,
            'false_positives': false_positives,
        }
    
    def _benchmark_performance(self):
        """性能基准测试"""
        print("\n⚡ 性能测试...")
        
        latencies = []
        
        # 随机抽取 100 个样本测试
        test_samples = self.results['detection_results'][:100]
        
        for result in test_samples:
            latencies.append(result['match_time_ms'])
        
        if latencies:
            latencies.sort()
            p50_idx = int(len(latencies) * 0.5)
            p95_idx = int(len(latencies) * 0.95)
            p99_idx = int(len(latencies) * 0.99)
            
            p50 = latencies[p50_idx]
            p95 = latencies[p95_idx]
            p99 = latencies[p99_idx]
            
            self.results['performance'] = {
                'samples_tested': len(latencies),
                'p50_latency_ms': p50,
                'p95_latency_ms': p95,
                'p99_latency_ms': p99,
            }
            
            print(f"  P50: {p50:.2f}ms")
            print(f"  P95: {p95:.2f}ms")
            print(f"  P99: {p99:.2f}ms")
    
    def _calculate_metrics(self):
        """计算核心指标"""
        print("\n📊 计算指标...")
        
        # 检测率
        mal_stats = self.results.get('malicious_stats', {})
        total_mal = mal_stats.get('total', 0)
        tp = mal_stats.get('true_positives', 0)
        
        detection_rate = tp / total_mal if total_mal > 0 else 0
        
        # 误报率
        ben_stats = self.results.get('benign_stats', {})
        total_ben = ben_stats.get('total', 0)
        fp = ben_stats.get('false_positives', 0)
        
        false_positive_rate = fp / total_ben if total_ben > 0 else 0
        
        # P99 延迟
        perf = self.results.get('performance', {})
        p99_latency = perf.get('p99_latency_ms', 0) / 1000  # 转换为秒
        
        self.results['metrics'] = {
            'detection_rate': detection_rate,
            'false_positive_rate': false_positive_rate,
            'p99_latency_sec': p99_latency,
            'total_rules': len(self.matcher.rules),
            'total_samples': total_mal + total_ben,
        }
        
        print(f"  检测率：{detection_rate*100:.2f}%")
        print(f"  误报率：{false_positive_rate*100:.2f}%")
        print(f"  P99 延迟：{p99_latency*1000:.2f}ms")
    
    def _evaluate(self):
        """综合评估"""
        print("\n📋 评估...")
        
        metrics = self.results['metrics']
        issues_count = len(self.results['issues'])
        
        # 检查是否达标
        passed = True
        
        if metrics['detection_rate'] < QUALITY_TARGETS['detection_rate']:
            print(f"  ❌ 检测率 {metrics['detection_rate']:.1%} < 目标 {QUALITY_TARGETS['detection_rate']:.1%}")
            passed = False
        else:
            print(f"  ✅ 检测率达标")
        
        if metrics['false_positive_rate'] > QUALITY_TARGETS['false_positive_rate']:
            print(f"  ❌ 误报率 {metrics['false_positive_rate']:.1%} > 目标 {QUALITY_TARGETS['false_positive_rate']:.1%}")
            passed = False
        else:
            print(f"  ✅ 误报率达标")
        
        if metrics['p99_latency_sec'] > QUALITY_TARGETS['p99_latency']:
            print(f"  ❌ P99 延迟 {metrics['p99_latency_sec']*1000:.2f}ms > 目标 {QUALITY_TARGETS['p99_latency']*1000:.0f}ms")
            passed = False
        else:
            print(f"  ✅ P99 延迟达标")
        
        self.results['passed'] = passed
        
        if passed:
            print(f"\n✅ Round 15 质量验证通过（{issues_count} 个小问题）")
        else:
            print(f"\n❌ Round 15 质量验证未通过（{issues_count} 个问题）")
    
    def _generate_reports(self):
        """生成报告"""
        # JSON 报告
        json_file = RESULTS_DIR / "validation_results.json"
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        # Markdown 摘要
        md_file = REPORTS_DIR / "ROUND15_QUALITY_REPORT.md"
        with open(md_file, 'w') as f:
            f.write("# Round 15 - 质量验证报告\n\n")
            f.write(f"**时间**: {self.results['timestamp']}\n\n")
            f.write(f"**状态**: {'✅ 通过' if self.results['passed'] else '❌ 未通过'}\n\n")
            
            f.write("## 核心指标\n\n")
            metrics = self.results['metrics']
            f.write(f"| 指标 | 结果 | 目标 | 状态 |\n")
            f.write(f"|------|------|------|------|\n")
            
            dr = metrics.get('detection_rate', 0)
            fpr = metrics.get('false_positive_rate', 0)
            p99 = metrics.get('p99_latency_sec', 0) * 1000
            
            f.write(f"| 检测率 | {dr*100:.2f}% | ≥98% | {'✅' if dr >= 0.98 else '❌'} |\n")
            f.write(f"| 误报率 | {fpr*100:.2f}% | <2% | {'✅' if fpr < 0.02 else '❌'} |\n")
            f.write(f"| P99 延迟 | {p99:.2f}ms | <5ms | {'✅' if p99 < 5 else '❌'} |\n\n")
            
            f.write("## 样本统计\n\n")
            mal = self.results.get('malicious_stats', {})
            ben = self.results.get('benign_stats', {})
            f.write(f"- 恶意样本：{mal.get('total', 0)} 个 (TP={mal.get('true_positives', 0)}, FN={mal.get('false_negatives', 0)})\n")
            f.write(f"- 白样本：{ben.get('total', 0)} 个 (TN={ben.get('true_negatives', 0)}, FP={ben.get('false_positives', 0)})\n\n")
            
            f.write("## 问题列表\n\n")
            if self.results['issues']:
                for issue in self.results['issues'][:20]:  # 只显示前 20 个
                    f.write(f"- {issue}\n")
                if len(self.results['issues']) > 20:
                    f.write(f"\n... 还有 {len(self.results['issues']) - 20} 个问题\n")
            else:
                f.write("无问题\n")
        
        print(f"\n💾 JSON 报告：{json_file}")
        print(f"💾 Markdown 报告：{md_file}")

def main():
    validator = QualityValidator()
    results = validator.validate_all()
    
    # 退出码
    sys.exit(0 if results['passed'] else 1)

if __name__ == '__main__':
    main()
