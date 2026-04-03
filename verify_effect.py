#!/usr/bin/env python3
"""
📊 HROS 效果验证工具
验证自动提升的实际效果
"""

import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List

WORKSPACE = Path('/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master')
BENCHMARK = WORKSPACE / 'benchmark' / 'benchmark_v3.py'
RULES_DIR = WORKSPACE / 'rules' / 'scanner_v3' / 'yara'

print("="*70)
print("📊 HROS 效果验证工具")
print("="*70)

# === 验证方法 1: 基准测试对比 ===
print("\n📋 验证方法 1: 基准测试对比")
print("-" * 50)

# 找到所有规则版本
rule_versions = sorted(RULES_DIR.glob('all_rules_v*.yar'))
print(f"找到 {len(rule_versions)} 个规则版本")

if len(rule_versions) >= 2:
    # 对比最新版本和次新版本
    v_latest = rule_versions[-1]
    v_previous = rule_versions[-2]
    
    print(f"\n对比：{v_previous.name} vs {v_latest.name}")
    
    # 运行基准测试
    print("\n运行基准测试...")
    
    def run_bench(rules_file):
        result = subprocess.run(
            ['python3', str(BENCHMARK), '--rules', str(rules_file)],
            capture_output=True, text=True, timeout=90
        )
        
        metrics = {}
        for line in result.stdout.split('\n'):
            if 'Detection Rate' in line:
                metrics['detection_rate'] = float(line.split(':')[1].strip().replace('%', ''))
            elif 'False Positive' in line:
                metrics['false_positive'] = float(line.split(':')[1].strip().replace('%', ''))
            elif 'F1 Score' in line:
                metrics['f1_score'] = float(line.split(':')[1].strip().replace('%', ''))
            elif 'YARA Rules Loaded' in line:
                metrics['rules_count'] = int(line.split(':')[1].strip())
        
        return metrics
    
    m_previous = run_bench(v_previous)
    m_latest = run_bench(v_latest)
    
    print("\n基准测试结果:")
    print(f"{'指标':<15} {v_previous.name:<15} {v_latest.name:<15} {'变化':<10}")
    print("-" * 60)
    print(f"{'检测率':<15} {m_previous.get('detection_rate', 0):>6.1f}%        {m_latest.get('detection_rate', 0):>6.1f}%        {m_latest.get('detection_rate', 0) - m_previous.get('detection_rate', 0):>+.1f}%")
    print(f"{'误报率':<15} {m_previous.get('false_positive', 0):>6.1f}%        {m_latest.get('false_positive', 0):>6.1f}%        {m_latest.get('false_positive', 0) - m_previous.get('false_positive', 0):>+.1f}%")
    print(f"{'F1 Score':<15} {m_previous.get('f1_score', 0):>6.1f}        {m_latest.get('f1_score', 0):>6.1f}        {m_latest.get('f1_score', 0) - m_previous.get('f1_score', 0):>+.1f}")
    print(f"{'规则数':<15} {m_previous.get('rules_count', 0):>6}        {m_latest.get('rules_count', 0):>6}        {m_latest.get('rules_count', 0) - m_previous.get('rules_count', 0):>+}")
    
    # 效果评估
    improvement = m_latest.get('detection_rate', 0) - m_previous.get('detection_rate', 0)
    if improvement > 0:
        print(f"\n✅ 效果提升：检测率 +{improvement:.1f}%")
    elif improvement == 0:
        print(f"\n➡️  效果持平：检测率无变化")
    else:
        print(f"\n⚠️  效果下降：检测率 {improvement:.1f}%")

else:
    print("⚠️  版本不足，无法对比")

# === 验证方法 2: 样本扫描测试 ===
print("\n\n📋 验证方法 2: 样本扫描测试")
print("-" * 50)

# 运行测试套件
print("运行完整测试套件...")
test_result = subprocess.run(
    ['python3', str(WORKSPACE / 'ros_test.py')],
    capture_output=True, text=True, timeout=120
)

# 解析测试结果
if '通过' in test_result.stdout:
    import re
    match = re.search(r'(\d+)/(\d+) 通过', test_result.stdout)
    if match:
        passed = int(match.group(1))
        total = int(match.group(2))
        print(f"\n测试结果：{passed}/{total} 通过 ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("✅ 所有测试通过")
        else:
            print(f"⚠️  {total - passed} 个测试失败")
else:
    print("⚠️  测试运行失败")

# === 验证方法 3: 历史记录分析 ===
print("\n\n📋 验证方法 3: 历史记录分析")
print("-" * 50)

history_file = WORKSPACE / 'ros_meta' / 'history.json'
if history_file.exists():
    history = json.loads(history_file.read_text())
    print(f"共 {len(history)} 轮循环记录")
    
    if len(history) >= 2:
        # 对比第一轮和最后一轮
        first = history[0]
        last = history[-1]
        
        print(f"\n第 1 轮 vs 第{len(history)}轮:")
        
        before_rate = first.get('before', {}).get('detection_rate', 0)
        after_rate = last.get('after', {}).get('detection_rate', 0)
        
        print(f"检测率：{before_rate:.1f}% → {after_rate:.1f}% ({after_rate - before_rate:+.1f}%)")
        
        if after_rate > before_rate:
            print("✅ 持续提升：检测率提升")
        else:
            print("➡️  保持稳定：检测率无明显变化")
else:
    print("⚠️  历史记录不存在")

# === 验证方法 4: 自学习成果 ===
print("\n\n📋 验证方法 4: 自学习成果")
print("-" * 50)

learning_file = WORKSPACE / 'ros_meta' / 'self_learning' / 'self_learning_report.json'
if learning_file.exists():
    learning = json.loads(learning_file.read_text())
    
    assessment = learning.get('assessment', {})
    opportunities = learning.get('opportunities', [])
    mined = learning.get('mined_results', {})
    improvement = learning.get('improvement', {})
    
    print(f"评估完成：{len(assessment.get('strengths', []))}个优势，{len(assessment.get('weaknesses', []))}个劣势")
    print(f"探索完成：{len(opportunities)}个学习机会")
    print(f"挖掘完成：{len(mined.get('new_rules', []))}条新规则，{len(mined.get('optimized_rules', []))}条优化")
    print(f"提升完成：{improvement.get('rules_added', 0)}条添加，{improvement.get('rules_updated', 0)}条优化")
    
    if len(opportunities) > 0:
        print("✅ 自学习引擎正常工作")
    else:
        print("⚠️  未发现学习机会")
else:
    print("⚠️  自学习报告不存在")

# === 验证方法 5: 日志分析 ===
print("\n\n📋 验证方法 5: 运行日志分析")
print("-" * 50)

logs_dir = WORKSPACE / 'ros_logs'
if logs_dir.exists():
    auto_logs = sorted(logs_dir.glob('auto_*.log'))
    print(f"找到 {len(auto_logs)} 个自动运行日志")
    
    # 统计成功次数
    success_count = 0
    for log_file in auto_logs[-5:]:  # 最近 5 个日志
        content = log_file.read_text()
        if '✅' in content and '完成' in content:
            success_count += 1
    
    print(f"最近运行成功率：{success_count}/5 ({success_count/5*100:.0f}%)")
    
    if success_count >= 4:
        print("✅ 自动提升运行稳定")
    else:
        print("⚠️  运行不稳定")
else:
    print("⚠️  日志目录不存在")

# === 综合评估 ===
print("\n\n" + "="*70)
print("📊 综合效果评估")
print("="*70)

# 综合评分
scores = []

# 1. 基准测试评分
if 'improvement' in dir() and isinstance(improvement, (int, float)) and improvement > 0:
    scores.append(5)
elif 'improvement' in dir() and isinstance(improvement, (int, float)) and improvement == 0:
    scores.append(3)
else:
    scores.append(2)

# 2. 测试通过率评分
if 'passed' in dir() and 'total' in dir() and passed == total:
    scores.append(5)
else:
    scores.append(2)

# 3. 自学习评分
if 'opportunities' in dir() and len(opportunities) > 0:
    scores.append(5)
else:
    scores.append(2)

# 4. 运行稳定性评分
if 'success_count' in dir() and success_count >= 4:
    scores.append(5)
else:
    scores.append(3)

avg_score = sum(scores) / len(scores)

print(f"""
综合评分：{avg_score:.1f}/5.0

{'✅ 优秀' if avg_score >= 4.5 else '⚠️  良好' if avg_score >= 3.0 else '🔴 需改进'}

各维度评分:
- 基准测试：{'⭐⭐⭐⭐⭐' if scores[0] == 5 else '⭐⭐⭐' if scores[0] == 3 else '⭐⭐'}
- 测试覆盖：{'⭐⭐⭐⭐⭐' if scores[1] == 5 else '⭐⭐'}
- 自学习能力：{'⭐⭐⭐⭐⭐' if scores[2] == 5 else '⭐⭐'}
- 运行稳定性：{'⭐⭐⭐⭐⭐' if scores[3] == 5 else '⭐⭐⭐'}
""")

print("="*70)
print("\n💾 验证报告已保存：ros_tests/effect_verification_report.md")

# 保存报告
improvement_value = improvement if isinstance(improvement, (int, float)) else 0

report = f"""# HROS 效果验证报告

**时间**: {datetime.now().isoformat()}

## 基准测试对比
- 检测率：{m_previous.get('detection_rate', 0):.1f}% → {m_latest.get('detection_rate', 0):.1f}% ({improvement_value:+.1f}%)
- 误报率：{m_previous.get('false_positive', 0):.1f}% → {m_latest.get('false_positive', 0):.1f}%
- F1 Score: {m_previous.get('f1_score', 0):.1f} → {m_latest.get('f1_score', 0):.1f}

## 测试覆盖
- 通过率：{passed}/{total} ({passed/total*100:.1f}%)

## 历史记录
- 循环轮次：{len(history)}轮
- 提升趋势：{'持续提升' if 'after_rate' in dir() and after_rate > before_rate else '稳定'}

## 自学习成果
- 学习机会：{len(opportunities)}个
- 规则优化：{len(mined.get('optimized_rules', []))}条

## 运行稳定性
- 成功率：{success_count}/5 ({success_count/5*100:.0f}%)

## 综合评估
- 评分：{avg_score:.1f}/5.0
- 等级：{'优秀' if avg_score >= 4.5 else '良好' if avg_score >= 3.0 else '需改进'}
"""

Path(WORKSPACE / 'ros_tests' / 'effect_verification_report.md').write_text(report)

print("\n下次验证：20 分钟后 (下次自动提升后)")
print("="*70)
