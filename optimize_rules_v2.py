#!/usr/bin/env python3
"""
规则优化器 v2 - 基于误报数据智能分级
"""
import re, os, json
from collections import defaultdict

RULES_DIR = 'rules/scanner_v3/yara'
OUTPUT_DIR = 'rules/optimized'

# 基于扫描结果的误报规则映射 (从 by_attack_type 推断)
HIGH_FP_ATTACKS = {
    # 攻击类型 -> 估计 FP 率
    'agent_curl_remote_exec': 0.60,  # 60% FP
    'credential_theft': 0.55,
    'persistence': 0.50,
    'cred_cloudcred': 0.65,
    'malicious_general': 0.70,
    'agent_memory_pollution': 0.45,
    'js_remotecodeexecution_dynamicimport': 0.50,
    'code_execution': 0.40,
    'agent_resource_exhaustion': 0.35,
    'agent_data_exfil': 0.30,
}

LOW_FP_ATTACKS = {
    # 低 FP 攻击类型
    'shell_codeinjection': 0.05,
    'exfil_large_file': 0.02,
    'data_exfiltration': 0.08,
    'evasion': 0.10,
    'resource_exhaustion': 0.12,
    'memory_pollution': 0.15,
}

# 规则关键词映射到攻击类型
ATTACK_KEYWORDS = {
    'curl': 'agent_curl_remote_exec',
    'remote_exec': 'agent_curl_remote_exec',
    'credential': 'credential_theft',
    'theft': 'credential_theft',
    'persistence': 'persistence',
    'persist': 'persistence',
    'cloudcred': 'cred_cloudcred',
    'memory_pollution': 'agent_memory_pollution',
    'js_remote': 'js_remotecodeexecution_dynamicimport',
    'code_exec': 'code_execution',
    'resource': 'agent_resource_exhaustion',
    'exfil': 'agent_data_exfil',
    'shell': 'shell_codeinjection',
    'evasion': 'evasion',
}


def estimate_fp_rate(rule_name, rule_text):
    """估计规则的误报率"""
    name_lower = rule_name.lower()
    text_lower = rule_text.lower()
    
    # 检查是否匹配已知高 FP 攻击
    for attack, fp_rate in HIGH_FP_ATTACKS.items():
        if attack in name_lower or attack.replace('_', '') in name_lower:
            return fp_rate
    
    # 检查关键词
    for keyword, attack in ATTACK_KEYWORDS.items():
        if keyword in name_lower:
            return HIGH_FP_ATTACKS.get(attack, 0.30)
    
    # 检查低 FP 攻击
    for attack, fp_rate in LOW_FP_ATTACKS.items():
        if attack in name_lower:
            return fp_rate
    
    # 默认中等 FP 率
    return 0.25


def classify_by_fp(fp_rate):
    """根据 FP 率分级"""
    if fp_rate < 0.05:
        return 'L1'  # 高置信度
    elif fp_rate < 0.20:
        return 'L2'  # 中置信度
    else:
        return 'L3'  # 低置信度


def add_confidence_metadata(rule_text, level, fp_estimate):
    """添加置信度元数据"""
    # 在 rule 开头添加 meta
    m = re.match(r'^(rule\s+\S+\s*\{)', rule_text)
    if m:
        prefix = m.group(1)
        rest = rule_text[len(prefix):]
        
        # 插入 meta 块
        meta_block = '''
    meta:
        confidence_level = "{}"
        estimated_fp_rate = {:.2f}
'''.format(level, fp_estimate)
        
        # 检查是否已有 meta
        if 'meta:' in rest:
            return rule_text  # 已有 meta，跳过
        
        return prefix + meta_block + rest
    return rule_text


def extract_rules_from_file(fpath):
    content = open(fpath, 'rb').read().decode('utf-8', errors='ignore')
    lines = content.split('\n')
    rules = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^rule\s+(\S+)\s*\{', line)
        if m:
            rule_name = m.group(1)
            rule_lines = [line]
            bc = line.count('{') - line.count('}')
            i += 1
            while i < len(lines) and bc > 0:
                line = lines[i]
                rule_lines.append(line)
                bc += line.count('{') - line.count('}')
                i += 1
            rule_text = '\n'.join(rule_lines)
            if bc == 0:
                rules[rule_name] = rule_text
        else:
            i += 1
    return rules


def fix_unicode_escapes(text):
    def replacer(m):
        cp = int(m.group(1), 16)
        char = chr(cp)
        return ''.join('\\x{:02x}'.format(b) for b in char.encode('utf-8'))
    return re.sub(r'\\u([0-9a-fA-F]{4})', replacer, text)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 收集所有规则
    all_rules = {}
    for fname in sorted(os.listdir(RULES_DIR)):
        if not fname.endswith('.yar') or 'all_rules' in fname or fname == 'all_rules_v51_dedup.yar':
            continue
        fpath = os.path.join(RULES_DIR, fname)
        rules = extract_rules_from_file(fpath)
        for name, text in rules.items():
            if name not in all_rules:
                all_rules[name] = fix_unicode_escapes(text)
    
    print('总规则数：{}'.format(len(all_rules)))
    
    # 分类
    l1_rules = {}
    l2_rules = {}
    l3_rules = {}
    fp_stats = []
    
    for name, text in all_rules.items():
        fp_rate = estimate_fp_rate(name, text)
        level = classify_by_fp(fp_rate)
        optimized = add_confidence_metadata(text, level, fp_rate)
        
        if level == 'L1':
            l1_rules[name] = optimized
        elif level == 'L2':
            l2_rules[name] = optimized
        else:
            l3_rules[name] = optimized
        
        fp_stats.append((name, fp_rate, level))
    
    # 统计
    print('L1 (高置信度，FP < 5%):  {} 条'.format(len(l1_rules)))
    print('L2 (中置信度，FP 5-20%): {} 条'.format(len(l2_rules)))
    print('L3 (低置信度，FP > 20%): {} 条'.format(len(l3_rules)))
    
    # 写入分级文件
    for level, rules, fname in [
        ('L1', l1_rules, 'l1_high_confidence.yar'),
        ('L2', l2_rules, 'l2_medium_confidence.yar'),
        ('L3', l3_rules, 'l3_low_confidence.yar'),
    ]:
        if rules:
            out_path = os.path.join(OUTPUT_DIR, fname)
            content = '\n\n'.join(sorted(rules.values()))
            open(out_path, 'w', encoding='utf-8').write(content)
            print('写入：{} ({} 条，{:,} bytes)'.format(out_path, len(rules), len(content.encode())))
    
    # 生成详细索引
    index = {
        'summary': {
            'L1': len(l1_rules),
            'L2': len(l2_rules),
            'L3': len(l3_rules),
            'total': len(all_rules),
        },
        'rules': []
    }
    
    for name, fp_rate, level in sorted(fp_stats, key=lambda x: x[1]):
        index['rules'].append({
            'name': name,
            'level': level,
            'estimated_fp': round(fp_rate, 2),
        })
    
    index_path = os.path.join(OUTPUT_DIR, 'rule_index_detailed.json')
    json.dump(index, open(index_path, 'w'), indent=2)
    print('写入：{}'.format(index_path))
    
    # 生成使用建议
    print('\n📋 使用建议:')
    print('  - 生产环境：仅使用 L1 规则 (FP < 5%)')
    print('  - 测试环境：使用 L1 + L2 规则 (FP < 20%)')
    print('  - 研究用途：使用全部规则')
    
    print('\n✅ 规则优化完成!')


if __name__ == '__main__':
    main()
