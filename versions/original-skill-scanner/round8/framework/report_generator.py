#!/usr/bin/env python3
"""
报告生成器
生成 JSON 和 Markdown 格式的报告
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

BASE_DIR = Path('/home/cdy/.openclaw/workspace/skills/agent-security-skill-scanner/expert_mode/round8')
REPORTS_DIR = BASE_DIR / 'reports'
RESULTS_DIR = BASE_DIR / 'results'


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        self.analysis = None
        self.results = None
    
    def load_analysis(self, path: str = None) -> Dict:
        """加载分析结果"""
        if path is None:
            path = REPORTS_DIR / 'analysis_results.json'
        
        with open(path, 'r', encoding='utf-8') as f:
            self.analysis = json.load(f)
        
        return self.analysis
    
    def load_results(self, path: str = None) -> list:
        """加载执行结果"""
        if path is None:
            path = RESULTS_DIR / 'execution_results.json'
        
        with open(path, 'r', encoding='utf-8') as f:
            self.results = json.load(f)
        
        return self.results
    
    def generate_json_report(self, output_path: str = None) -> str:
        """生成 JSON 报告"""
        if output_path is None:
            REPORTS_DIR.mkdir(parents=True, exist_ok=True)
            output_path = REPORTS_DIR / 'report.json'
        
        report = {
            'report_type': 'round8_validation',
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_test_cases': self.analysis['total_test_cases'],
                'total_results': self.analysis['total_results'],
                'detection_rate': self.analysis['overall_metrics']['detection_rate_pct'],
                'false_positive_rate': self.analysis['overall_metrics']['false_positive_rate_pct'],
                'f1_score': self.analysis['overall_metrics']['f1_score_pct'],
                'accuracy': self.analysis['overall_metrics']['accuracy_pct'],
                'performance_p99_ms': self.analysis['performance_stats']['p99_ms'],
                'passed_rules': self.analysis['passed_rules']['passed'],
                'total_rules': self.analysis['passed_rules']['total']
            },
            'metrics': self.analysis['overall_metrics'],
            'by_attack_type': self.analysis['by_attack_type'],
            'by_rule_type': self.analysis['by_rule_type'],
            'performance': self.analysis['performance_stats'],
            'problem_rules': self.analysis['problem_rules'],
            'recommendations': self._generate_recommendations()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return str(output_path)
    
    def generate_markdown_report(self, output_path: str = None) -> str:
        """生成 Markdown 报告"""
        if output_path is None:
            REPORTS_DIR.mkdir(parents=True, exist_ok=True)
            output_path = REPORTS_DIR / 'report.md'
        
        md = self._build_markdown_content()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md)
        
        return str(output_path)
    
    def _generate_recommendations(self) -> list:
        """生成优化建议"""
        recommendations = []
        
        metrics = self.analysis['overall_metrics']
        
        # 检测率低
        if metrics['detection_rate_pct'] < 90:
            recommendations.append({
                'priority': 'high',
                'category': 'detection',
                'issue': f"检测率 ({metrics['detection_rate_pct']}%) 低于目标 (90%)",
                'suggestion': '加强规则覆盖，特别是针对漏报的攻击类型'
            })
        
        # 误报率高
        if metrics['false_positive_rate_pct'] > 10:
            recommendations.append({
                'priority': 'high',
                'category': 'precision',
                'issue': f"误报率 ({metrics['false_positive_rate_pct']}%) 高于目标 (10%)",
                'suggestion': '优化规则阈值，减少对正常样本的误判'
            })
        
        # 性能问题
        if self.analysis['performance_stats']['p99_ms'] > 100:
            recommendations.append({
                'priority': 'medium',
                'category': 'performance',
                'issue': f"P99 延迟 ({self.analysis['performance_stats']['p99_ms']}ms) 较高",
                'suggestion': '优化规则匹配算法，考虑使用缓存或预编译'
            })
        
        # 问题规则
        if len(self.analysis['problem_rules']) > 5:
            recommendations.append({
                'priority': 'medium',
                'category': 'rules',
                'issue': f"发现 {len(self.analysis['problem_rules'])} 个问题规则",
                'suggestion': '审查并优化问题规则，特别是误报率高的规则'
            })
        
        # 按攻击类型分析
        for attack_type, stats in self.analysis['by_attack_type'].items():
            if stats['detection_rate'] < 80:
                recommendations.append({
                    'priority': 'high',
                    'category': 'attack_specific',
                    'issue': f"{attack_type} 检测率 ({stats['detection_rate']}%) 较低",
                    'suggestion': f'针对 {attack_type} 攻击增加专用检测规则'
                })
        
        return recommendations
    
    def _build_markdown_content(self) -> str:
        """构建 Markdown 内容"""
        md = []
        
        # 标题
        md.append("# 🔒 Round 8 规则验证报告\n")
        md.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 执行摘要
        md.append("## 📊 执行摘要\n")
        summary = self.analysis['overall_metrics']
        passed = self.analysis['passed_rules']
        
        md.append("| 指标 | 值 | 目标 | 状态 |")
        md.append("|------|-----|------|------|")
        
        detection = summary['detection_rate_pct']
        fpr = summary['false_positive_rate_pct']
        f1 = summary['f1_score_pct']
        p99 = self.analysis['performance_stats']['p99_ms']
        
        md.append(f"| 检测率 | {detection}% | ≥90% | {'✅' if detection >= 90 else '⚠️'} |")
        md.append(f"| 误报率 | {fpr}% | ≤10% | {'✅' if fpr <= 10 else '⚠️'} |")
        md.append(f"| F1 Score | {f1}% | ≥85% | {'✅' if f1 >= 85 else '⚠️'} |")
        md.append(f"| 性能 P99 | {p99}ms | ≤100ms | {'✅' if p99 <= 100 else '⚠️'} |")
        md.append(f"| 通过规则 | {passed['passed']}/{passed['total']} | ≥80% | {'✅' if passed['pass_rate'] >= 80 else '⚠️'} |")
        md.append("")
        
        # 混淆矩阵
        md.append("## 🎯 混淆矩阵\n")
        cm = summary['confusion_matrix']
        md.append("| | 预测阳性 | 预测阴性 |")
        md.append("|---|---------|---------|")
        md.append(f"| **实际阳性** | TP={cm['TP']} | FN={cm['FN']} |")
        md.append(f"| **实际阴性** | FP={cm['FP']} | TN={cm['TN']} |")
        md.append(f"| **边界样本** | - | UNCLEAR={cm['UNCLEAR']} |")
        md.append("")
        
        # 按攻击类型分析
        md.append("## 🎭 按攻击类型分析\n")
        md.append("| 攻击类型 | 检测率 | 误报率 | TP | FN | FP | TN |")
        md.append("|---------|--------|--------|----|----|----|----|")
        
        for attack_type, stats in self.analysis['by_attack_type'].items():
            status = '✅' if stats['detection_rate'] >= 80 else '⚠️'
            md.append(
                f"| {attack_type} {status} | {stats['detection_rate']}% | "
                f"{stats['false_positive_rate']}% | {stats['true_positives']} | "
                f"{stats['false_negatives']} | {stats['false_positives']} | {stats['true_negatives']} |"
            )
        md.append("")
        
        # 性能统计
        md.append("## ⚡ 性能统计\n")
        perf = self.analysis['performance_stats']
        md.append(f"- **P50**: {perf['p50_ms']} ms")
        md.append(f"- **P90**: {perf['p90_ms']} ms")
        md.append(f"- **P99**: {perf['p99_ms']} ms")
        md.append(f"- **平均**: {perf['avg_ms']} ms")
        md.append(f"- **最小**: {perf['min_ms']} ms")
        md.append(f"- **最大**: {perf['max_ms']} ms")
        md.append("")
        
        # 可视化图表数据 (用于后续生成图表)
        md.append("## 📈 可视化数据\n")
        md.append("### 检测率对比\n")
        md.append("```json")
        chart_data = {
            'labels': list(self.analysis['by_attack_type'].keys()),
            'detection_rates': [s['detection_rate'] for s in self.analysis['by_attack_type'].values()],
            'fpr': [s['false_positive_rate'] for s in self.analysis['by_attack_type'].values()]
        }
        md.append(json.dumps(chart_data, indent=2))
        md.append("```\n")
        
        # 问题规则
        md.append("## ⚠️ 问题规则\n")
        if self.analysis['problem_rules']:
            md.append("| 规则 ID | 类型 | 问题 | 详情 |")
            md.append("|--------|------|------|------|")
            for pr in self.analysis['problem_rules'][:10]:
                if 'false_positive_rate' in pr:
                    detail = f"误报率 {pr['false_positive_rate']}%"
                else:
                    detail = f"漏报率 {pr.get('false_negative_rate', 'N/A')}%"
                md.append(f"| {pr['rule_id']} | {pr['rule_type']} | {pr['issue']} | {detail} |")
        else:
            md.append("未发现明显问题规则 ✅")
        md.append("")
        
        # 优化建议
        md.append("## 💡 优化建议\n")
        recommendations = self._generate_recommendations()
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(rec['priority'], '⚪')
                md.append(f"{i}. {priority_icon} **{rec['category']}**: {rec['issue']}")
                md.append(f"   - 建议：{rec['suggestion']}\n")
        else:
            md.append("所有指标均达标，无需特别优化 ✅")
        md.append("")
        
        # 详细结果
        md.append("## 📋 详细结果\n")
        md.append(f"- 总测试用例数：{self.analysis['total_test_cases']}")
        md.append(f"- 总执行结果数：{self.analysis['total_results']}")
        md.append(f"- 分析时间：{self.analysis['analysis_timestamp']}")
        md.append("")
        
        # 结论
        md.append("## 🏁 结论\n")
        if detection >= 90 and fpr <= 10 and f1 >= 85:
            md.append("**✅ 验证通过** - 所有关键指标均达到目标要求\n")
        elif detection >= 80 and fpr <= 20:
            md.append("**⚠️ 基本通过** - 主要指标达标，但有优化空间\n")
        else:
            md.append("**❌ 需要改进** - 关键指标未达标，需要优化规则\n")
        
        md.append("\n---\n")
        md.append("*报告由 Round 8 验证框架自动生成*\n")
        
        return '\n'.join(md)
    
    def generate_chart_data(self, output_path: str = None) -> str:
        """生成可视化图表数据"""
        if output_path is None:
            output_path = REPORTS_DIR / 'chart_data.json'
        
        chart_data = {
            'detection_by_attack': {
                'type': 'bar',
                'labels': list(self.analysis['by_attack_type'].keys()),
                'datasets': [
                    {
                        'label': '检测率 (%)',
                        'data': [s['detection_rate'] for s in self.analysis['by_attack_type'].values()]
                    },
                    {
                        'label': '误报率 (%)',
                        'data': [s['false_positive_rate'] for s in self.analysis['by_attack_type'].values()]
                    }
                ]
            },
            'confusion_matrix': {
                'type': 'heatmap',
                'labels': ['预测阳性', '预测阴性'],
                'values': [
                    [self.analysis['overall_metrics']['confusion_matrix']['TP'],
                     self.analysis['overall_metrics']['confusion_matrix']['FN']],
                    [self.analysis['overall_metrics']['confusion_matrix']['FP'],
                     self.analysis['overall_metrics']['confusion_matrix']['TN']]
                ]
            },
            'performance': {
                'type': 'line',
                'labels': ['P50', 'P90', 'P99', '平均'],
                'data': [
                    self.analysis['performance_stats']['p50_ms'],
                    self.analysis['performance_stats']['p90_ms'],
                    self.analysis['performance_stats']['p99_ms'],
                    self.analysis['performance_stats']['avg_ms']
                ]
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chart_data, f, indent=2)
        
        return str(output_path)
    
    def generate_all_reports(self) -> Dict[str, str]:
        """生成所有报告"""
        print("加载分析结果...")
        self.load_analysis()
        self.load_results()
        
        print("生成 JSON 报告...")
        json_path = self.generate_json_report()
        
        print("生成 Markdown 报告...")
        md_path = self.generate_markdown_report()
        
        print("生成图表数据...")
        chart_path = self.generate_chart_data()
        
        return {
            'json': json_path,
            'markdown': md_path,
            'chart_data': chart_path
        }


def main():
    print("=" * 60)
    print("Round 8 报告生成器")
    print("=" * 60)
    
    generator = ReportGenerator()
    reports = generator.generate_all_reports()
    
    print("\n报告生成完成:")
    print(f"  JSON 报告：{reports['json']}")
    print(f"  Markdown 报告：{reports['markdown']}")
    print(f"  图表数据：{reports['chart_data']}")
    
    print("\n✅ 报告生成完成!")
    
    return reports


if __name__ == '__main__':
    main()
