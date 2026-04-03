#!/usr/bin/env python3
"""
Round 16: AST 检测规则优化器

优化方向:
1. 调整风险评分权重
2. 增加新的检测规则
3. 降低误报率
"""

import json
from pathlib import Path
from datetime import datetime

SCANNER_V3 = Path.home() / ".openclaw" / "workspace" / "agent-security-skill-scanner-V3"
AST_REPORT = SCANNER_V3 / "samples" / "high_fidelity" / "ast_scan_report.json"
ROUND16_DIR = SCANNER_V3 / "round16"

# 加载原始报告
with open(AST_REPORT, 'r', encoding='utf-8') as f:
    results = json.load(f)

print("=" * 60)
print("Round 16: AST 检测结果分析")
print("=" * 60)

# 详细统计
total = len(results)
malicious = sum(1 for r in results if r.get('malicious'))
safe = total - malicious
errors = sum(1 for r in results if r.get('error'))

# 风险评分分布
risk_scores = [r.get('risk_score', 0) for r in results if not r.get('error')]
high_risk = sum(1 for s in risk_scores if s >= 70)
medium_risk = sum(1 for s in risk_scores if 40 <= s < 70)
low_risk = sum(1 for s in risk_scores if s < 40)

print(f"""
📊 扫描统计
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
总文件数：{total}
恶意文件：{malicious} ({malicious/total*100:.1f}%)
安全文件：{safe} ({safe/total*100:.1f}%)
解析错误：{errors}

📈 风险分布
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
高风险 (≥70):  {high_risk} ({high_risk/total*100:.1f}%)
中风险 (40-69): {medium_risk} ({medium_risk/total*100:.1f}%)
低风险 (<40):  {low_risk} ({low_risk/total*100:.1f}%)

平均风险分：{sum(risk_scores)/len(risk_scores):.1f}/100
最高风险分：{max(risk_scores)}/100
""")

# 混淆检测详情
obf_types = {}
for r in results:
    for f in r.get('obfuscation', {}).get('findings', []):
        t = f.get('type', 'unknown')
        obf_types[t] = obf_types.get(t, 0) + 1

print(f"""
🔍 混淆类型统计
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
for t, c in sorted(obf_types.items(), key=lambda x: x[1], reverse=True):
    print(f'{t:25} {c:5} 个')

# 行为分析详情
behaviors = {}
for r in results:
    for b in r.get('behaviors', []):
        c = b.get('category', 'unknown')
        behaviors[c] = behaviors.get(c, 0) + 1

print(f"""
🎯 行为类型统计
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
for c, cnt in sorted(behaviors.items(), key=lambda x: x[1], reverse=True):
    print(f'{c:25} {cnt:5} 次')

# Top 10 高风险样本
print(f"""
⚠️  Top 10 高风险样本
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
sorted_results = sorted([r for r in results if not r.get('error')], 
                        key=lambda x: x.get('risk_score', 0), reverse=True)[:10]
for i, r in enumerate(sorted_results, 1):
    file_name = r.get('file', '').split('/')[-2]
    risk = r.get('risk_score', 0)
    obf_count = len(r.get('obfuscation', {}).get('findings', []))
    behavior_count = len(r.get('behaviors', []))
    print(f'{i:2}. {file_name:30} 风险分：{risk:5.1f} | 混淆：{obf_count} | 行为：{behavior_count}')

# 优化建议
print(f"""
💡 优化建议
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 调整风险评分权重
   - 动态执行 (eval/exec): 30 → 40 分
   - Base64 解码：20 → 25 分
   - 动态导入：20 → 25 分
   - 网络行为：10 → 15 分
   - 文件系统：10 → 12 分

2. 新增检测规则
   - 字符串拼接混淆
   - 反射调用检测
   - 加密库使用检测
   - 异常处理隐藏

3. 降低误报率
   - 白名单机制 (常见安全库)
   - 上下文分析 (结合多个特征)
   - 阈值调整 (50 → 55 分)

下一步：运行优化后的扫描器验证效果
""")

# 保存分析报告
report = {
    'analysis_timestamp': datetime.now().isoformat(),
    'summary': {
        'total': total,
        'malicious': malicious,
        'safe': safe,
        'errors': errors,
        'detection_rate': f"{malicious/total*100:.1f}%"
    },
    'risk_distribution': {
        'high': high_risk,
        'medium': medium_risk,
        'low': low_risk,
        'avg_score': round(sum(risk_scores)/len(risk_scores), 1),
        'max_score': max(risk_scores)
    },
    'obfuscation_types': obf_types,
    'behavior_categories': behaviors,
    'top_risky_samples': [
        {
            'file': r.get('file', '').split('/')[-2],
            'risk_score': r.get('risk_score', 0),
            'obfuscation_count': len(r.get('obfuscation', {}).get('findings', [])),
            'behavior_count': len(r.get('behaviors', []))
        }
        for r in sorted_results
    ],
    'optimization_recommendations': [
        '调整风险评分权重',
        '新增检测规则 (字符串拼接/反射调用/加密库)',
        '白名单机制降低误报',
        '阈值调整 50 → 55'
    ]
}

analysis_path = ROUND16_DIR / 'ROUND16_ANALYSIS.json'
with open(analysis_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"📄 详细报告：{analysis_path}")
