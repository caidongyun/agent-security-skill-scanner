#!/usr/bin/env python3
"""
完成报告生成器
生成 Round 8 验证的完成报告
"""

import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path('/home/cdy/.openclaw/workspace/skills/agent-security-skill-scanner/expert_mode/round8')
REPORTS_DIR = BASE_DIR / 'reports'


def load_analysis() -> dict:
    """加载分析结果"""
    analysis_path = REPORTS_DIR / 'analysis_results.json'
    with open(analysis_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_report() -> dict:
    """加载报告"""
    report_path = REPORTS_DIR / 'report.json'
    with open(report_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_completion_report():
    """生成完成报告"""
    print("加载分析结果...")
    analysis = load_analysis()
    
    print("生成完成报告...")
    
    metrics = analysis['overall_metrics']
    performance = analysis['performance_stats']
    passed = analysis['passed_rules']
    problem_rules = analysis['problem_rules']
    
    # 判断是否通过
    detection_rate = metrics['detection_rate_pct']
    fpr = metrics['false_positive_rate_pct']
    f1_score = metrics['f1_score_pct']
    p99 = performance['p99_ms']
    
    passed_all = (
        detection_rate >= 90 and
        fpr <= 10 and
        f1_score >= 85 and
        p99 <= 100
    )
    
    report = f"""# 🔒 Round 8 规则验证完成报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 验证结果摘要

本次验证共执行 **{analysis['total_test_cases']}** 个测试用例，覆盖 **6** 类攻击场景。

### 整体评估

| 评估项 | 结果 | 状态 |
|--------|------|------|
| 检测率 | {detection_rate}% | {'✅ 达标' if detection_rate >= 90 else '⚠️ 需改进'} |
| 误报率 | {fpr}% | {'✅ 达标' if fpr <= 10 else '⚠️ 需改进'} |
| F1 Score | {f1_score}% | {'✅ 达标' if f1_score >= 85 else '⚠️ 需改进'} |
| 性能 P99 | {p99}ms | {'✅ 达标' if p99 <= 100 else '⚠️ 需改进'} |
| 通过规则 | {passed['passed']}/{passed['total']} | {'✅' if passed['pass_rate'] >= 80 else '⚠️'} |

**总体结论**: {'✅ 验证通过' if passed_all else '⚠️ 基本通过，有优化空间' if detection_rate >= 80 and fpr <= 20 else '❌ 需要改进'}

---

## 🎯 关键指标达成情况

### 1. 检测率 (Detection Rate)

- **当前值**: {detection_rate}%
- **目标值**: ≥90%
- **状态**: {'✅ 已达成' if detection_rate >= 90 else '❌ 未达成'}

检测率反映了系统正确识别攻击样本的能力。

### 2. 误报率 (False Positive Rate)

- **当前值**: {fpr}%
- **目标值**: ≤10%
- **状态**: {'✅ 已达成' if fpr <= 10 else '❌ 未达成'}

误报率反映了系统将正常样本误判为攻击的比例。

### 3. F1 Score

- **当前值**: {f1_score}%
- **目标值**: ≥85%
- **状态**: {'✅ 已达成' if f1_score >= 85 else '❌ 未达成'}

F1 Score 综合衡量了精确率和召回率。

### 4. 性能指标 (P99 Latency)

- **当前值**: {p99}ms
- **目标值**: ≤100ms
- **状态**: {'✅ 已达成' if p99 <= 100 else '❌ 未达成'}

P99 延迟反映了 99% 请求的处理时间上限。

---

## 📈 按攻击类型分析

| 攻击类型 | 检测率 | 误报率 | TP | FN | 状态 |
|---------|--------|--------|----|----|----|
"""
    
    for attack_type, stats in analysis['by_attack_type'].items():
        status = '✅' if stats['detection_rate'] >= 80 else '⚠️'
        report += f"| {attack_type} | {stats['detection_rate']}% | {stats['false_positive_rate']}% | {stats['true_positives']} | {stats['false_negatives']} | {status} |\n"
    
    report += f"""
---

## ⚠️ 问题规则列表

"""
    
    if problem_rules:
        report += f"共发现 **{len(problem_rules)}** 个问题规则：\n\n"
        report += "| 规则 ID | 类型 | 问题 | 详情 |\n"
        report += "|--------|------|------|------|\n"
        
        for pr in problem_rules[:10]:
            if 'false_positive_rate' in pr:
                detail = f"误报率 {pr['false_positive_rate']}%"
            else:
                detail = f"漏报率 {pr.get('false_negative_rate', 'N/A')}%"
            report += f"| {pr['rule_id']} | {pr['rule_type']} | {pr['issue']} | {detail} |\n"
        
        if len(problem_rules) > 10:
            report += f"\n*还有 {len(problem_rules) - 10} 个问题规则，详见分析报告*\n"
    else:
        report += "✅ 未发现明显问题规则\n"
    
    report += f"""
---

## 💡 优化建议

"""
    
    recommendations = []
    
    if detection_rate < 90:
        recommendations.append(f"### 1. 提升检测率 (优先级：高)\n")
        recommendations.append(f"当前检测率为 {detection_rate}%，需要提升 {90 - detection_rate:.1f}% 以达到目标。\n")
        recommendations.append("**建议措施**:\n")
        recommendations.append("- 分析漏报样本 (FN)，找出规则覆盖盲区\n")
        recommendations.append("- 针对高漏报率的攻击类型增加专用规则\n")
        recommendations.append("- 考虑使用机器学习模型辅助检测\n\n")
    
    if fpr > 10:
        recommendations.append(f"### 2. 降低误报率 (优先级：高)\n")
        recommendations.append(f"当前误报率为 {fpr}%，需要降低 {fpr - 10:.1f}% 以达到目标。\n")
        recommendations.append("**建议措施**:\n")
        recommendations.append("- 审查误报样本 (FP)，找出过度匹配的规则\n")
        recommendations.append("- 增加规则的前置条件，提高匹配精度\n")
        recommendations.append("- 考虑引入白名单机制\n\n")
    
    if p99 > 100:
        recommendations.append(f"### 3. 优化性能 (优先级：中)\n")
        recommendations.append(f"当前 P99 延迟为 {p99}ms，需要降低 {p99 - 100:.1f}ms 以达到目标。\n")
        recommendations.append("**建议措施**:\n")
        recommendations.append("- 优化正则表达式，使用预编译\n")
        recommendations.append("- 减少不必要的规则匹配\n")
        recommendations.append("- 考虑使用缓存机制\n\n")
    
    if problem_rules:
        recommendations.append(f"### 4. 修复问题规则 (优先级：中)\n")
        recommendations.append(f"共发现 {len(problem_rules)} 个问题规则需要修复。\n")
        recommendations.append("**建议措施**:\n")
        recommendations.append("- 优先修复误报率高的规则\n")
        recommendations.append("- 对问题规则进行 A/B 测试\n")
        recommendations.append("- 建立规则回归测试机制\n\n")
    
    if recommendations:
        report += ''.join(recommendations)
    else:
        report += "✅ 所有指标均达标，无需特别优化\n"
    
    report += f"""
---

## 📋 详细统计

### 混淆矩阵

| | 预测阳性 | 预测阴性 |
|---|---------|---------|
| **实际阳性** | TP={metrics['confusion_matrix']['TP']} | FN={metrics['confusion_matrix']['FN']} |
| **实际阴性** | FP={metrics['confusion_matrix']['FP']} | TN={metrics['confusion_matrix']['TN']} |
| **边界样本** | - | UNCLEAR={metrics['confusion_matrix']['UNCLEAR']} |

### 性能统计

- **P50**: {performance['p50_ms']} ms
- **P90**: {performance['p90_ms']} ms
- **P99**: {performance['p99_ms']} ms
- **平均**: {performance['avg_ms']} ms
- **最小**: {performance['min_ms']} ms
- **最大**: {performance['max_ms']} ms

### 测试覆盖

- **总测试用例**: {analysis['total_test_cases']}
- **阳性样本**: {analysis['by_attack_type']['tool_poisoning']['total'] // 3 * 6} (6 类攻击 × 20 阳性)
- **阴性样本**: {analysis['by_attack_type']['tool_poisoning']['total'] // 3 * 6} (6 类攻击 × 20 阴性)
- **边界样本**: {analysis['by_attack_type']['tool_poisoning']['total'] // 3 * 6} (6 类攻击 × 10 边界)

---

## 📁 输出文件

| 文件 | 路径 |
|------|------|
| JSON 报告 | `round8/reports/report.json` |
| Markdown 报告 | `round8/reports/report.md` |
| 分析结果 | `round8/reports/analysis_results.json` |
| 执行结果 | `round8/results/execution_results.json` |
| 图表数据 | `round8/reports/chart_data.json` |

---

## ✅ 验证完成

**验证框架**: Round 8 Security Rule Validation Framework  
**版本**: 1.0.0  
**执行时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

*本报告由 Round 8 验证框架自动生成*
"""
    
    # 保存报告
    output_path = BASE_DIR / 'ROUND8_COMPLETION_REPORT.md'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"完成报告保存到：{output_path}")
    
    return output_path


def print_summary():
    """打印关键指标摘要"""
    analysis = load_analysis()
    metrics = analysis['overall_metrics']
    performance = analysis['performance_stats']
    passed = analysis['passed_rules']
    
    print("\n" + "=" * 60)
    print("Round 8 验证关键指标")
    print("=" * 60)
    print(f"\n检测率 (Detection Rate):     {metrics['detection_rate_pct']}%")
    print(f"误报率 (False Positive Rate): {metrics['false_positive_rate_pct']}%")
    print(f"性能 P99:                    {performance['p99_ms']} ms")
    print(f"通过的规则数：               {passed['passed']}/{passed['total']}")
    print("\n" + "=" * 60)


if __name__ == '__main__':
    generate_completion_report()
    print_summary()
