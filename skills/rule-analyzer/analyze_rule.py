#!/usr/bin/env python3
"""
多模型规则分析器 - 使用 LLM 交叉分析规则质量
"""
import os, json, hashlib
from datetime import datetime

OUTPUT_DIR = 'rules/reviewed'
ANALYSIS_DIR = 'skills/rule-analyzer/analyses'

# 分析 Prompt 模板
ANALYSIS_PROMPT = """
你是一个 Agent 安全检测专家。请分析以下 YARA 规则:

## 规则内容
```yara
{rule_content}
```

## 分析维度

1. **规则意图**: 这条规则检测什么攻击或行为？

2. **误报风险** (高/中/低): 
   - 良性代码是否可能触发此规则？
   - 常见开发/运维场景是否会误报？

3. **漏报风险** (高/中/低):
   - 攻击者是否容易绕过此规则？
   - 规则覆盖是否全面？

4. **优化建议**:
   - 是否需要添加例外条件？
   - 是否需要增强检测逻辑？

5. **置信度评分** (0-100):
   - 90-100: 高置信度，可直接使用
   - 70-89: 中置信度，需少量优化
   - 50-69: 低置信度，需大量优化
   - <50: 不可靠，建议移除

## 输出格式 (JSON)
{
  "intent": "规则意图描述",
  "fp_risk": "高|中|低",
  "fn_risk": "高|中|低",
  "suggestions": ["优化建议 1", "优化建议 2"],
  "confidence_score": 0-100,
  "recommendation": "approve|optimize|remove"
}
"""

def analyze_rule_single_model(rule_name, rule_content, model='mock'):
    """单模型分析 (模拟)"""
    # 实际应调用 LLM API
    # 这里使用规则分析启发式方法模拟
    
    # 分析规则特征
    fp_risk = '低'
    fn_risk = '中'
    confidence = 75
    recommendation = 'optimize'
    
    # 宽泛关键词 → 高 FP 风险
    broad_keywords = ['subprocess', 'eval', 'exec', 'curl', 'wget', 'socket']
    if any(kw in rule_content.lower() for kw in broad_keywords):
        fp_risk = '高'
        confidence = 50
        recommendation = 'optimize'
    
    # 具体攻击特征 → 低 FP 风险
    specific_keywords = ['/dev/tcp/', 'nc -e', 'base64 -d', 'powershell -enc']
    if any(kw in rule_content.lower() for kw in specific_keywords):
        fp_risk = '低'
        confidence = 90
        recommendation = 'approve'
    
    # 条件过于简单 → 高 FN 风险
    if 'any of them' in rule_content and rule_content.count('$') < 3:
        fn_risk = '高'
    
    return {
        'model': model,
        'intent': f'检测 {rule_name.replace("_", " ")} 相关行为',
        'fp_risk': fp_risk,
        'fn_risk': fn_risk,
        'suggestions': ['添加路径例外条件', '增加多条件组合'] if fp_risk == '高' else ['规则质量良好'],
        'confidence_score': confidence,
        'recommendation': recommendation,
    }

def analyze_rule_multi_model(rule_name, rule_content, models=['mock-1', 'mock-2', 'mock-3', 'mock-4']):
    """多模型交叉分析"""
    print(f'分析规则：{rule_name}')
    
    results = []
    for model in models:
        result = analyze_rule_single_model(rule_name, rule_content, model)
        results.append(result)
    
    # 聚合结果
    avg_confidence = sum(r['confidence_score'] for r in results) / len(results)
    fp_votes = {'高': 0, '中': 0, '低': 0}
    for r in results:
        fp_votes[r['fp_risk']] += 1
    
    # 共识决策
    max_fp = max(fp_votes, key=fp_votes.get)
    if avg_confidence >= 80 and fp_votes['高'] == 0:
        consensus = 'approve'
    elif avg_confidence >= 60:
        consensus = 'optimize'
    else:
        consensus = 'remove'
    
    return {
        'rule_name': rule_name,
        'analyses': results,
        'consensus': {
            'avg_confidence': round(avg_confidence, 1),
            'fp_risk_consensus': max_fp,
            'recommendation': consensus,
        },
        'analyzed_at': datetime.now().isoformat(),
    }

def analyze_rules_batch(rules_dir, output_dir=OUTPUT_DIR):
    """批量分析规则"""
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    
    # 读取规则文件
    rule_files = [
        'rules/optimized/l1_high_confidence.yar',
        'rules/optimized/l2_medium_confidence.yar',
        'rules/optimized/l3_low_confidence.yar',
    ]
    
    all_rules = {}
    for rf in rule_files:
        if os.path.exists(rf):
            content = open(rf).read()
            # 简单分割规则
            rules = content.split('\nrule ')
            for rule in rules:
                if rule.strip() and not rule.startswith('//'):
                    rule = 'rule ' + rule if not rule.startswith('rule ') else rule
                    m = __import__('re').match(r'^rule\s+(\w+)', rule)
                    if m:
                        name = m.group(1)
                        all_rules[name] = rule
    
    print(f'待分析规则：{len(all_rules)} 条')
    print()
    
    # 分析每条规则
    results = []
    for i, (name, content) in enumerate(list(all_rules.items())[:10], 1):  # 先分析 10 条
        print(f'[{i}/10] ', end='')
        result = analyze_rule_multi_model(name, content)
        results.append(result)
        
        # 保存分析结果
        analysis_file = os.path.join(ANALYSIS_DIR, f'{name}_analysis.json')
        with open(analysis_file, 'w') as f:
            json.dump(result, f, indent=2)
    
    # 生成汇总报告
    summary = {
        'total_analyzed': len(results),
        'by_recommendation': {},
        'by_fp_risk': {},
        'avg_confidence': sum(r['consensus']['avg_confidence'] for r in results) / len(results) if results else 0,
        'rules': results,
    }
    
    for r in results:
        rec = r['consensus']['recommendation']
        fp = r['consensus']['fp_risk_consensus']
        summary['by_recommendation'][rec] = summary['by_recommendation'].get(rec, 0) + 1
        summary['by_fp_risk'][fp] = summary['by_fp_risk'].get(fp, 0) + 1
    
    summary_file = os.path.join(output_dir, 'analysis_summary.json')
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print()
    print('='*60)
    print('✅ 规则分析完成!')
    print('='*60)
    print(f'分析规则数：{len(results)}')
    print(f'平均置信度：{summary["avg_confidence"]:.1f}')
    print(f'建议分布：{summary["by_recommendation"]}')
    print(f'FP 风险分布：{summary["by_fp_risk"]}')
    print()
    print(f'详细报告：{summary_file}')
    
    return summary

if __name__ == '__main__':
    analyze_rules_batch('rules/optimized/')
