#!/usr/bin/env python3
"""
规则优化器 v4 - 修复规则提取逻辑
"""
import re, os, json

RULES_DIR = 'rules/scanner_v3/yara'
OUTPUT_DIR = 'rules/optimized'

FP_RATES = {
    'Agent_Curl': 0.60, 'Agent_Credential': 0.55, 'CRED_': 0.50,
    'Agent_Persistence': 0.45, 'Agent_Memory': 0.40, 'Agent_Resource': 0.35,
    'JS_': 0.45, 'PS_': 0.40, 'BASH_': 0.35,
    'Agent_Data_Exfil': 0.30, 'EXFIL_': 0.25, 'Agent_SupplyChain': 0.30,
    'Agent_Evasion': 0.20,
    'Shell_ReverseShell': 0.05, 'Shell_PrivEsc': 0.08,
    'Impact_DataDestruction': 0.03, 'Impact_Ransomware': 0.02,
    'Malicious_Hidden': 0.10, 'PrivEsc_': 0.08, 'Impact_': 0.05,
}

def estimate_fp_rate(rule_name):
    for prefix, fp_rate in sorted(FP_RATES.items(), key=lambda x: -len(x[0])):
        if rule_name.startswith(prefix):
            return fp_rate
    return 0.25

def classify_by_fp(fp_rate):
    if fp_rate < 0.10: return 'L1'
    elif fp_rate < 0.30: return 'L2'
    else: return 'L3'

def extract_rules_from_file(fpath):
    """改进的规则提取 - 使用正则匹配完整规则块"""
    content = open(fpath, 'rb').read().decode('utf-8', errors='ignore')
    rules = {}
    
    # 匹配 rule NAME { ... } 结构
    pattern = re.compile(r'^(rule\s+\w+)\s*\{(.*?)^\}', re.MULTILINE | re.DOTALL)
    for m in pattern.finditer(content):
        rule_start = m.group(1)  # "rule RuleName"
        rule_body = m.group(2)   # 规则内容
        rule_name = rule_start.split()[1]
        rule_text = rule_start + ' {' + rule_body + '\n}'
        rules[rule_name] = rule_text
    
    return rules

def fix_unicode_escapes(text):
    def replacer(m):
        cp = int(m.group(1), 16)
        char = chr(cp)
        return ''.join('\\x{:02x}'.format(b) for b in char.encode('utf-8'))
    return re.sub(r'\\u([0-9a-fA-F]{4})', replacer, text)

def add_confidence_metadata(rule_name, rule_text, level, fp_estimate):
    if 'meta:' not in rule_text:
        # 在 rule NAME { 后插入 meta
        m = re.match(r'^(rule\s+\w+\s*\{)', rule_text)
        if m:
            prefix = m.group(1)
            rest = rule_text[len(prefix):]
            meta = '\n    meta:\n        confidence_level = "{}"\n        estimated_fp_rate = {:.2f}\n'.format(level, fp_estimate)
            return prefix + meta + rest
    return rule_text

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
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
    
    l1_rules, l2_rules, l3_rules = {}, {}, {}
    fp_stats = []
    
    for name, text in all_rules.items():
        fp_rate = estimate_fp_rate(name)
        level = classify_by_fp(fp_rate)
        optimized = add_confidence_metadata(name, text, level, fp_rate)
        
        if level == 'L1': l1_rules[name] = optimized
        elif level == 'L2': l2_rules[name] = optimized
        else: l3_rules[name] = optimized
        
        fp_stats.append((name, fp_rate, level))
    
    print('L1 (FP < 10%): {} 条'.format(len(l1_rules)))
    print('L2 (FP 10-30%): {} 条'.format(len(l2_rules)))
    print('L3 (FP > 30%): {} 条'.format(len(l3_rules)))
    
    # 验证并写入
    for level, rules, fname in [('L1', l1_rules, 'l1_high_confidence.yar'),
                                  ('L2', l2_rules, 'l2_medium_confidence.yar'),
                                  ('L3', l3_rules, 'l3_low_confidence.yar')]:
        if rules:
            out_path = os.path.join(OUTPUT_DIR, fname)
            content = '\n\n'.join(sorted(rules.values()))
            open(out_path, 'w', encoding='utf-8').write(content)
            
            # 验证
            try:
                import yara
                yara.compile(filepath=out_path)
                print('✅ {} ({} 条，{:,} bytes)'.format(fname, len(rules), len(content.encode())))
            except Exception as e:
                print('❌ {} 验证失败：{}'.format(fname, e))
    
    # 索引
    index = {'summary': {'L1': len(l1_rules), 'L2': len(l2_rules), 'L3': len(l3_rules)},
             'rules': [{'name': n, 'level': l, 'fp': round(f, 2)} for n, f, l in sorted(fp_stats, key=lambda x: x[1])]}
    json.dump(index, open(os.path.join(OUTPUT_DIR, 'rule_index.json'), 'w'), indent=2)
    
    print('\n✅ 规则优化完成!')

if __name__ == '__main__':
    main()
