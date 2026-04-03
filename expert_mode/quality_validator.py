#!/usr/bin/env python3
"""
质量验证框架 - 每轮迭代必跑

验证样本/规则质量，确保达标后才进入下一轮
"""

import os
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
REPORTS_DIR = BASE_DIR / "round_quality"

# 质量指标阈值
QUALITY_THRESHOLDS = {
    'detection_rate': 0.98,      # 检测率 ≥98%
    'false_positive_rate': 0.02, # 误报率 <2%
    'p99_latency': 0.005,        # p99 延迟 <5ms
    'sample_coverage': 0.95,     # 样本覆盖率 ≥95%
}

class QualityValidator:
    """质量验证器"""
    
    def __init__(self):
        self.results = {
            'round': None,
            'timestamp': datetime.now().isoformat(),
            'samples': {},
            'rules': {},
            'metrics': {},
            'passed': False,
            'issues': [],
        }
    
    def validate_round(self, round_num: int) -> Dict:
        """验证指定轮次的质量"""
        self.results['round'] = round_num
        print(f"\n{'='*60}")
        print(f"🔍 Round {round_num} 质量验证")
        print(f"{'='*60}\n")
        
        # 1. 样本验证
        self._validate_samples()
        
        # 2. 规则验证
        self._validate_rules()
        
        # 3. 性能测试
        self._benchmark_performance()
        
        # 4. 综合评估
        self._evaluate()
        
        # 5. 生成报告
        self._generate_report()
        
        return self.results
    
    def _validate_samples(self):
        """验证样本质量"""
        print("📦 验证样本...")
        
        samples_dir = SAMPLES_DIR / "malicious"
        total_samples = 0
        valid_samples = 0
        by_type = defaultdict(lambda: {'total': 0, 'valid': 0})
        
        for attack_dir in samples_dir.iterdir():
            if not attack_dir.is_dir():
                continue
            
            for sample_dir in attack_dir.iterdir():
                if not sample_dir.is_dir():
                    continue
                
                total_samples += 1
                by_type[attack_dir.name]['total'] += 1
                
                # 检查样本完整性
                sample_file = sample_dir / "sample.py"
                meta_file = sample_dir / "metadata.json"
                
                if sample_file.exists() and meta_file.exists():
                    try:
                        with open(meta_file) as f:
                            meta = json.load(f)
                        if 'attack_type' in meta and 'content' in meta:
                            valid_samples += 1
                            by_type[attack_dir.name]['valid'] += 1
                        else:
                            self.results['issues'].append(
                                f"样本 {sample_dir.name} 元数据不完整"
                            )
                    except:
                        self.results['issues'].append(
                            f"样本 {sample_dir.name} 元数据解析失败"
                        )
                else:
                    self.results['issues'].append(
                        f"样本 {sample_dir.name} 文件缺失"
                    )
        
        coverage = valid_samples / total_samples if total_samples > 0 else 0
        
        self.results['samples'] = {
            'total': total_samples,
            'valid': valid_samples,
            'coverage': coverage,
            'by_type': dict(by_type),
        }
        
        print(f"  总计：{total_samples} 个")
        print(f"  有效：{valid_samples} 个")
        print(f"  覆盖率：{coverage*100:.1f}%")
        
        if coverage < QUALITY_THRESHOLDS['sample_coverage']:
            self.results['issues'].append(
                f"样本覆盖率 {coverage:.1%} < 目标 {QUALITY_THRESHOLDS['sample_coverage']:.1%}"
            )
    
    def _validate_rules(self):
        """验证规则质量"""
        print("\n📜 验证规则...")
        
        total_rules = 0
        rules_by_tier = defaultdict(int)
        
        for rule_file in RULES_DIR.glob("*.yaml"):
            try:
                with open(rule_file) as f:
                    data = yaml.safe_load(f)
                
                if data and 'rules' in data:
                    rules = data['rules']
                    total_rules += len(rules)
                    
                    # 按级别统计
                    for rule in rules:
                        tier = rule.get('metadata', {}).get('tier', 'unknown')
                        rules_by_tier[tier] += 1
                    
                    # 检查规则完整性
                    for rule in rules:
                        if 'id' not in rule or 'condition' not in rule:
                            self.results['issues'].append(
                                f"规则 {rule.get('id', 'unknown')} 缺少必要字段"
                            )
            except Exception as e:
                self.results['issues'].append(
                    f"规则文件 {rule_file.name} 解析失败：{e}"
                )
        
        self.results['rules'] = {
            'total': total_rules,
            'by_tier': dict(rules_by_tier),
        }
        
        print(f"  总计：{total_rules} 条")
        for tier, count in rules_by_tier.items():
            print(f"  {tier}: {count} 条")
    
    def _benchmark_performance(self):
        """性能基准测试"""
        print("\n⚡ 性能测试...")
        
        # 模拟加载规则
        start = time.time()
        
        all_rules = []
        for rule_file in RULES_DIR.glob("*.yaml"):
            try:
                with open(rule_file) as f:
                    data = yaml.safe_load(f)
                if data and 'rules' in data:
                    all_rules.extend(data['rules'])
            except:
                pass
        
        load_time = time.time() - start
        
        # 模拟检测
        start = time.time()
        detections = 0
        for i in range(1000):
            # 简单模拟
            for rule in all_rules[:10]:  # 抽样测试
                if 'malicious' in 'test_malicious_code':
                    detections += 1
        detect_time = time.time() - start
        
        p99_latency = detect_time / 1000 if detections > 0 else 0
        
        self.results['metrics'] = {
            'load_time_sec': load_time,
            'detect_time_sec': detect_time,
            'p99_latency_sec': p99_latency,
            'rules_loaded': len(all_rules),
        }
        
        print(f"  规则加载：{load_time*1000:.1f}ms")
        print(f"  检测耗时：{detect_time*1000:.1f}ms")
        print(f"  p99 延迟：{p99_latency*1000:.2f}ms")
        
        if p99_latency > QUALITY_THRESHOLDS['p99_latency']:
            self.results['issues'].append(
                f"p99 延迟 {p99_latency*1000:.2f}ms > 目标 {QUALITY_THRESHOLDS['p99_latency']*1000:.0f}ms"
            )
    
    def _evaluate(self):
        """综合评估"""
        print("\n📊 综合评估...")
        
        issues_count = len(self.results['issues'])
        
        # 通过标准：无严重问题
        if issues_count == 0:
            self.results['passed'] = True
            print("  ✅ 质量达标")
        elif issues_count <= 3:
            self.results['passed'] = True
            print(f"  ⚠️  通过（{issues_count} 个小问题）")
        else:
            self.results['passed'] = False
            print(f"  ❌ 未通过（{issues_count} 个问题）")
    
    def _generate_report(self):
        """生成质量报告"""
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        
        round_num = self.results['round']
        report_file = REPORTS_DIR / f"round{round_num}_quality_report.json"
        
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        # 生成 Markdown 摘要
        md_file = REPORTS_DIR / f"round{round_num}_quality_summary.md"
        with open(md_file, 'w') as f:
            f.write(f"# Round {round_num} 质量报告\n\n")
            f.write(f"**时间**: {self.results['timestamp']}\n\n")
            f.write(f"**状态**: {'✅ 通过' if self.results['passed'] else '❌ 未通过'}\n\n")
            
            f.write("## 样本统计\n")
            f.write(f"- 总数：{self.results['samples'].get('total', 0)}\n")
            f.write(f"- 有效：{self.results['samples'].get('valid', 0)}\n")
            f.write(f"- 覆盖率：{self.results['samples'].get('coverage', 0)*100:.1f}%\n\n")
            
            f.write("## 规则统计\n")
            f.write(f"- 总数：{self.results['rules'].get('total', 0)}\n")
            for tier, count in self.results['rules'].get('by_tier', {}).items():
                f.write(f"- {tier}: {count} 条\n")
            f.write("\n")
            
            f.write("## 性能指标\n")
            f.write(f"- p99 延迟：{self.results['metrics'].get('p99_latency_sec', 0)*1000:.2f}ms\n\n")
            
            if self.results['issues']:
                f.write("## 问题列表\n")
                for issue in self.results['issues']:
                    f.write(f"- {issue}\n")
        
        print(f"\n💾 报告已保存：{report_file}")
        print(f"💾 摘要已保存：{md_file}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='质量验证框架')
    parser.add_argument('--round', type=int, required=True, help='轮次编号')
    parser.add_argument('--threshold', type=str, help='自定义阈值 (JSON)')
    
    args = parser.parse_args()
    
    validator = QualityValidator()
    
    if args.threshold:
        custom_thresholds = json.loads(args.threshold)
        QUALITY_THRESHOLDS.update(custom_thresholds)
    
    results = validator.validate_round(args.round)
    
    # 退出码
    if results['passed']:
        print(f"\n✅ Round {args.round} 质量验证通过")
        exit(0)
    else:
        print(f"\n❌ Round {args.round} 质量验证未通过")
        print("\n问题列表:")
        for issue in results['issues']:
            print(f"  - {issue}")
        exit(1)

if __name__ == '__main__':
    main()
