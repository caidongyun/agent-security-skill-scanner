#!/usr/bin/env python3
"""Merge all valid YARA source files into scanner_master_rules.yar"""
import re, yara, os

def fix_unicode_escapes(text):
    def replacer(m):
        cp = int(m.group(1), 16)
        char = chr(cp)
        return ''.join('\\x{:02x}'.format(b) for b in char.encode('utf-8'))
    return re.sub(r'\\u([0-9a-fA-F]{4})', replacer, text)

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

def main():
    src_dir = 'rules/scanner_v3/yara'
    seen_rules = {}

    for fname in sorted(os.listdir(src_dir)):
        if not fname.endswith('.yar'):
            continue
        if 'all_rules' in fname or fname == 'all_rules_v51_dedup.yar':
            continue
        fpath = os.path.join(src_dir, fname)
        rules = extract_rules_from_file(fpath)
        added = 0
        for name, text in rules.items():
            if name not in seen_rules:
                seen_rules[name] = fix_unicode_escapes(text)
                added += 1
        print('  {}: {} rules, {} new'.format(fname, len(rules), added))

    sorted_rules = sorted(seen_rules.values(),
                          key=lambda r: re.search(r'^rule\s+(\S+)', r).group(1))
    merged = '\n\n'.join(sorted_rules)
    print('\nTotal: {} unique rules'.format(len(sorted_rules)))

    try:
        yara.compile(source=merged)
        print('YARA compile: VALID')
    except Exception as e:
        print('YARA compile FAIL: {}'.format(e))
        return

    out_path = 'scanner-master/output/rules/scanner_master_rules.yar'
    open(out_path, 'w', encoding='utf-8').write(merged)
    size = os.path.getsize(out_path)
    print('Written: {} ({} rules, {:,} bytes)'.format(out_path, len(sorted_rules), size))

if __name__ == '__main__':
    main()
