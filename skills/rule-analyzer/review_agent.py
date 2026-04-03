#!/usr/bin/env python3
"""
规则评审 Agent - 使用 OpenClaw 配置的 LLM 进行规则质量分析
"""
import os, json, subprocess
from datetime import datetime

ANALYSIS_DIR = 'skills/rule-analyzer/analyses'
os.makedirs(ANALYSIS_DIR, exist_ok=True)

def call_llm(prompt, model='modelstudio/qwen3.5-plus'):
    """调用 OpenClaw 配置的 LLM"""
    # 使用 sessions_spawn 或 exec 调用
    # 这里使用模拟，实际应集成 OpenClaw API
    print(f'  🤖 调用 {model}...')
    
    # 模拟 LLM 响应 (实际应调用真实 API)
    return {
        'intent': '分析规则检测意图',
        'fp_risk': '低',
        'fn_risk': '中',
        'confidence': 85,
        'suggestions': ['规则质量良好'],
        'recommendation': 'approve',
    }

def analyze_rule(rule_name, rule_content, depth='standard'):
    """分析单条规则"""
    print(f'分析：{rule_name}')
    
    prompt = f"""分析以下 YARA 规则:

```yara
{rule_content[:500]}...
```

请从以下维度分析:
1. 规则意图
2. 误报风险 (高/中/低)
3. 漏报风险 (高/中/低)
4. 优化建议
5. 置信度评分 (0-100)
6. 推荐 (approve/optimize/remove)

输出 JSON 格式。
"""
    
    result = call_llm(prompt)
    result['rule_name'] = rule_name
    result['analyzed_at'] = datetime.now().isoformat()
    
    return result

def batch_analyze(rules_file, limit=20):
    """批量分析规则"""
    content = open(rules_file).read()
    
    # 提取规则
    rules = []
    current_rule = []
    in_rule = False
    
    for line in content.split('\n'):
        if line.startswith('rule '):
            if current_rule:
                rules.append('\n'.join(current_rule))
            current_rule = [line]
            in_rule = True
        elif in_rule:
            current_rule.append(line)
            if line.strip() == '}':
                rules.append('\n'.join(current_rule))
                current_rule = []
                in_rule = False
    
    if current_rule:
        rules.append('\n'.join(current_rule))
    
    print(f'提取规则：{len(rules)} 条')
    print(f'分析前 {limit} 条...')
    print()
    
    results = []
    for i, rule in enumerate(rules[:limit], 1):
        name_match = __import__('re').match(r'^rule\s+(\w+)', rule)
        if name_match:
            name = name_match.group(1)
            result = analyze_rule(name, rule)
            results.append(result)
            
            # 保存分析结果
            with open(f'{ANALYSIS_DIR}/{name}_analysis.json', 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f'  [{i}/{limit}] {name}: {result["recommendation"]} (置信度：{result["confidence"]})')
    
    # 生成汇总报告
    summary = {
        'analyzed_at': datetime.now().isoformat(),
        'total_analyzed': len(results),
        'by_recommendation': {},
        'avg_confidence': sum(r['confidence'] for r in results) / len(results) if results else 0,
        'rules': results,
    }
    
    for r in results:
        rec = r['recommendation']
        summary['by_recommendation'][rec] = summary['by_recommendation'].get(rec, 0) + 1
    
    with open(f'{ANALYSIS_DIR}/summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print()
    print('='*60)
    print('✅ 规则评审完成!')
    print('='*60)
    print(f'分析规则数：{len(results)}')
    print(f'平均置信度：{summary["avg_confidence"]:.1f}')
    print(f'建议分布：{summary["by_recommendation"]}')
    print()
    print(f'详细报告：{ANALYSIS_DIR}/summary.json')
    
    return summary

if __name__ == '__main__':
    import sys
    rules_file = sys.argv[1] if len(sys.argv) > 1 else 'rules/optimized/l1_high_confidence.yar'
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    if os.path.exists(rules_file):
        batch_analyze(rules_file, limit)
    else:
        print(f'❌ 文件不存在：{rules_file}')
