#!/usr/bin/env python3
"""
规则优化器 v5 - 修复规则提取，确保 YARA 语法正确
"""
import re, os, json

RULES_DIR = 'rules/scanner_v3/yara'
OUTPUT_DIR = 'rules/optimized'

# FP 率估计 (规则前缀 -> FP 率)
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

def extract_rules_yara_safe(fpath):
    """使用 YARA 安全的方式提取规则"""
    content = open(fpath, 'rb').read().decode('utf-8', errors='ignore')
    rules = {}
    
    # 匹配完整的 rule 块：从 "rule NAME {" 到匹配的 "}"
    i = 0
    lines = content.split('\n')
    
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^rule\s+(\w+)\s*\{', line.strip())
        if m:
            rule_name = m.group(1)
            rule_lines = [line]
            brace_count = line.count('{') - line.count('}')
            i += 1
            
            # 收集直到 brace_count 为 0
            while i < len(lines) and brace_count > 0:
                line = lines[i]
                rule_lines.append(line)
                brace_count += line.count('{') - line.count('}')
                i += 1
            
            # 验证规则完整性
            rule_text = '\n'.join(rule_lines)
            if brace_count == 0:
                # 验证 YARA 语法
                try:
                    import yara
                    yara.compile(source=rule_text)
                    rules[rule_name] = rule_text
                except:
                    pass  # 跳过无效规则
        else:
            i += 1
    
    return rules

def fix_unicode_escapes(text):
    def replacer(m):
        cp = int(m.group(1), 16)
        char = chr(cp)
        return ''.join('\\x{:02x}'.format(b) for b in char.encode('utf-8'))
    return re.sub(r'\\u([0-9a-fA-F]{4})', replacer, text)

def add_metadata(rule_name, rule_text, level, fp_estimate):
    """添加元数据，YARA meta 不支持浮点数，使用字符串"""
    if 'meta:' not in rule_text:
        m = re.match(r'^(rule\s+\w+\s*\{)', rule_text)
        if m:
            prefix = m.group(1)
            rest = rule_text[len(prefix):]
            meta = '\n    meta:\n        confidence_level = "{}"\n        estimated_fp_rate = "{}"\n'.format(level, fp_estimate)
            return prefix + meta + rest
    return rule_text

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print('='*60)
    print('🔧 规则优化器 v5 - 修复语法错误')
    print('='*60)
    print()
    
    # 收集所有规则
    all_rules = {}
    file_stats = []
    
    for fname in sorted(os.listdir(RULES_DIR)):
        if not fname.endswith('.yar') or 'all_rules' in fname or fname == 'all_rules_v51_dedup.yar':
            continue
        fpath = os.path.join(RULES_DIR, fname)
        rules = extract_rules_yara_safe(fpath)
        added = 0
        for name, text in rules.items():
            if name not in all_rules:
                all_rules[name] = fix_unicode_escapes(text)
                added += 1
        file_stats.append((fname, len(rules), added))
        if added > 0:
            print('  {}: {} 规则，{} 新增'.format(fname, len(rules), added))
    
    print()
    print('总唯一规则数：{}'.format(len(all_rules)))
    print()
    
    # 分类
    l1_rules, l2_rules, l3_rules = {}, {}, {}
    fp_stats = []
    
    for name, text in all_rules.items():
        fp_rate = estimate_fp_rate(name)
        level = classify_by_fp(fp_rate)
        optimized = add_metadata(name, text, level, fp_rate)
        
        if level == 'L1': l1_rules[name] = optimized
        elif level == 'L2': l2_rules[name] = optimized
        else: l3_rules[name] = optimized
        
        fp_stats.append((name, fp_rate, level))
    
    print('L1 (FP < 10%): {} 条'.format(len(l1_rules)))
    print('L2 (FP 10-30%): {} 条'.format(len(l2_rules)))
    print('L3 (FP > 30%): {} 条'.format(len(l3_rules)))
    print()
    
    # 写入并验证
    import yara
    
    for level, rules, fname in [('L1', l1_rules, 'l1_high_confidence.yar'),
                                  ('L2', l2_rules, 'l2_medium_confidence.yar'),
                                  ('L3', l3_rules, 'l3_low_confidence.yar')]:
        if rules:
            out_path = os.path.join(OUTPUT_DIR, fname)
            content = '\n\n'.join(sorted(rules.values()))
            open(out_path, 'w', encoding='utf-8').write(content)
            
            try:
                yara.compile(filepath=out_path)
                print('✅ {} ({} 条，{:,} bytes)'.format(fname, len(rules), len(content.encode())))
            except Exception as e:
                print('❌ {} 验证失败：{}'.format(fname, e))
    
    # 生成索引
    index = {
        'summary': {'L1': len(l1_rules), 'L2': len(l2_rules), 'L3': len(l3_rules), 'total': len(all_rules)},
        'rules': [{'name': n, 'level': l, 'fp': round(f, 2)} for n, f, l in sorted(fp_stats, key=lambda x: x[1])]
    }
    json.dump(index, open(os.path.join(OUTPUT_DIR, 'rule_index.json'), 'w'), indent=2)
    print()
    print('✅ 规则索引：rules/optimized/rule_index.json')
    print()
    print('='*60)
    print('✅ 规则优化 v5 完成!')
    print('='*60)

if __name__ == '__main__':
    main()
