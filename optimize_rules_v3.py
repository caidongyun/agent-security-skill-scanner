#!/usr/bin/env python3
"""
规则优化器 v3 - 基于实际规则名称智能分级
"""
import re, os, json

RULES_DIR = 'rules/scanner_v3/yara'
OUTPUT_DIR = 'rules/optimized'

# 基于扫描结果的误报率估计 (规则前缀 -> FP 率)
FP_RATES = {
    # 高 FP 规则前缀
    'Agent_Curl': 0.60,
    'Agent_Credential': 0.55,
    'CRED_': 0.50,
    'Agent_Persistence': 0.45,
    'Agent_Memory': 0.40,
    'Agent_Resource': 0.35,
    'JS_': 0.45,
    'PS_': 0.40,
    'BASH_': 0.35,
    
    # 中等 FP
    'Agent_Data_Exfil': 0.30,
    'EXFIL_': 0.25,
    'Agent_SupplyChain': 0.30,
    'Agent_Evasion': 0.20,
    
    # 低 FP 规则
    'Shell_ReverseShell': 0.05,
    'Shell_PrivEsc': 0.08,
    'Impact_DataDestruction': 0.03,
    'Impact_Ransomware': 0.02,
    'Malicious_Hidden': 0.10,
    'PrivEsc_': 0.08,
    'Impact_': 0.05,
}


def estimate_fp_rate(rule_name):
    """估计规则的误报率"""
    # 检查具体前缀
    for prefix, fp_rate in sorted(FP_RATES.items(), key=lambda x: -len(x[0])):
        if rule_name.startswith(prefix):
            return fp_rate
    
    # 默认中等 FP
    return 0.25


def classify_by_fp(fp_rate):
    if fp_rate < 0.10:
        return 'L1'
    elif fp_rate < 0.30:
        return 'L2'
    else:
        return 'L3'


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


def add_confidence_metadata(rule_name, rule_text, level, fp_estimate):
    m = re.match(r'^(rule\s+\S+\s*\{)', rule_text)
    if m:
        prefix = m.group(1)
        rest = rule_text[len(prefix):]
        
        if 'meta:' not in rest:
            meta_block = '''
    meta:
        confidence_level = "{}"
        estimated_fp_rate = {:.2f}
'''.format(level, fp_estimate)
            return prefix + meta_block + rest
    return rule_text


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
        fp_rate = estimate_fp_rate(name)
        level = classify_by_fp(fp_rate)
        optimized = add_confidence_metadata(name, text, level, fp_rate)
        
        if level == 'L1':
            l1_rules[name] = optimized
        elif level == 'L2':
            l2_rules[name] = optimized
        else:
            l3_rules[name] = optimized
        
        fp_stats.append((name, fp_rate, level))
    
    print('L1 (高置信度，FP < 10%): {} 条'.format(len(l1_rules)))
    print('L2 (中置信度，FP 10-30%): {} 条'.format(len(l2_rules)))
    print('L3 (低置信度，FP > 30%): {} 条'.format(len(l3_rules)))
    
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
    
    # 生成索引
    index = {
        'summary': {'L1': len(l1_rules), 'L2': len(l2_rules), 'L3': len(l3_rules), 'total': len(all_rules)},
        'rules': [{'name': n, 'level': l, 'fp': round(f, 2)} for n, f, l in sorted(fp_stats, key=lambda x: x[1])]
    }
    json.dump(index, open(os.path.join(OUTPUT_DIR, 'rule_index.json'), 'w'), indent=2)
    
    # Top FP 规则
    print('\n⚠️  高 FP 规则 (Top 10):')
    for name, fp, level in sorted(fp_stats, key=lambda x: -x[1])[:10]:
        print('  {} (FP: {:.0f}%, {})'.format(name, fp*100, level))
    
    print('\n✅ 规则优化完成!')
    print('测试命令：python3 scanner-master/ros-scanner-v2.py samples/malicious/ --rules rules/optimized/l1_high_confidence.yar')


if __name__ == '__main__':
    main()
