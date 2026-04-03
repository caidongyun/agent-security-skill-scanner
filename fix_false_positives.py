#!/usr/bin/env python3
"""
专注优化：降低 Top 5 高 FP 规则的误报率
"""
import re, os

RULES_FILE = 'scanner-master/output/rules/scanner_master_rules.yar'
OUTPUT_FILE = 'rules/optimized_fp_reduced/all_rules.yar'

os.makedirs('rules/optimized_fp_reduced', exist_ok=True)

content = open(RULES_FILE).read()

# 优化规则映射
OPTIMIZATIONS = {
    # 规则名 -> (原条件片段，新条件片段，说明)
    'Shell_ReverseShell_Python': (
        '$py1 or $py2 or $py3 or $subprocess',
        '$py1 or $py2 or $py3',
        '移除 subprocess (太宽泛)'
    ),
}

def optimize_rule(rule_text, rule_name):
    """优化单条规则"""
    if rule_name not in OPTIMIZATIONS:
        return rule_text
    
    old_cond, new_cond, note = OPTIMIZATIONS[rule_name]
    
    if old_cond in rule_text:
        rule_text = rule_text.replace(old_cond, new_cond)
        print('  ✅ {}: {}'.format(rule_name, note))
    
    return rule_text

# 处理规则
rules = content.split('\n\n')
optimized_rules = []

print("优化高 FP 规则:")
for rule in rules:
    if rule.strip() and rule.startswith('rule '):
        # 提取规则名
        m = re.match(r'^rule\s+(\w+)', rule)
        if m:
            rule_name = m.group(1)
            opt_rule = optimize_rule(rule, rule_name)
            optimized_rules.append(opt_rule)

# 写入
output_content = '\n\n'.join(optimized_rules)
open(OUTPUT_FILE, 'w').write(output_content)
print()
print('✅ 优化完成：{}'.format(OUTPUT_FILE))
print('   规则数：{}'.format(len(optimized_rules)))

# 验证
try:
    import yara
    yara.compile(filepath=OUTPUT_FILE)
    print('✅ YARA 验证通过')
except Exception as e:
    print('❌ YARA 验证失败：{}'.format(e))
