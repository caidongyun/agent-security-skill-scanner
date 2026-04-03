#!/usr/bin/env python3
"""
规则优化器 - 降低误报率，实现规则分级
"""
import re, os, json
from collections import defaultdict

RULES_DIR = 'rules/scanner_v3/yara'
OUTPUT_DIR = 'rules/optimized'

# 规则分级标准
# L1: 高置信度 - 直接告警 (FP < 1%)
# L2: 中置信度 - 标记审查 (FP 1-10%)
# L3: 低置信度 - 仅日志 (FP > 10%)

L1_PATTERNS = [
    # 明确的恶意行为
    r'curl.*\|.*bash',
    r'wget.*\|.*sh',
    r'eval\(.*base64',
    r'exec\(.*fromCharCode',
    r'new Function\(.*fetch',
    r'subprocess.*shell=True.*curl',
    r'os.system.*wget',
    r'Import-Expression.*DownloadString',
    r'Invoke-WebRequest.*-Uri.*-OutFile',
]

L2_PATTERNS = [
    # 可疑但可能有合法用途
    r'curl.*http',
    r'wget.*http',
    r'eval\(',
    r'exec\(',
    r'base64',
    r'fromCharCode',
]

# 需要优化的规则（高频误报）
HIGH_FP_RULES = [
    'agent_curl_remote_exec',
    'credential_theft',
    'persistence',
    'cred_cloudcred',
    'malicious_general',
]


def classify_rule(rule_name, rule_text):
    """根据规则内容分类"""
    text_lower = rule_text.lower()
    
    # 检查 L1 模式
    for pattern in L1_PATTERNS:
        if re.search(pattern, text_lower):
            return 'L1'
    
    # 检查 L2 模式
    for pattern in L2_PATTERNS:
        if re.search(pattern, text_lower):
            return 'L2'
    
    # 默认 L3
    return 'L3'


def optimize_rule(rule_name, rule_text):
    """优化单条规则 - 添加例外条件"""
    # 针对高频误报规则的优化
    if 'curl' in rule_name.lower() and 'remote' in rule_name.lower():
        # curl 规则：添加管道到 shell 的条件
        if 'condition:' in rule_text:
            # 查找 condition 部分
            parts = rule_text.split('condition:')
            if len(parts) == 2:
                meta_strings = parts[0]
                condition = parts[1].strip()
                
                # 增强条件：必须包含管道或执行
                new_condition = '''
    condition:
        (curl_cmd or wget_cmd) and (pipe_to_shell or exec_flag)
'''
                # 添加新的字符串匹配
                if 'curl_cmd' not in meta_strings:
                    meta_strings = meta_strings.rstrip() + '''
        $curl_cmd = "curl" nocase
        $wget_cmd = "wget" nocase
        $pipe_to_shell = "| bash" nocase or "| sh" nocase
        $exec_flag = "-o /tmp" nocase or "-O /tmp" nocase
'''
                return meta_strings + new_condition
    
    # credential_theft 规则优化：添加上下文要求
    if 'credential' in rule_name.lower() or 'theft' in rule_name.lower():
        if 'condition:' in rule_text:
            parts = rule_text.split('condition:')
            if len(parts) == 2:
                meta_strings = parts[0]
                condition = parts[1].strip()
                
                # 要求多个凭证关键词同时出现
                new_condition = '''
    condition:
        (password or passwd or pwd) and (secret or token or api_key) and (exfil or send or upload)
'''
                if 'password' not in meta_strings:
                    meta_strings = meta_strings.rstrip() + '''
        $password = "password" nocase or "passwd" nocase or "pwd" nocase
        $secret = "secret" nocase or "token" nocase or "api_key" nocase
        $exfil = "exfil" nocase or "send" nocase or "upload" nocase
'''
                return meta_strings + new_condition
    
    return rule_text


def extract_rules_from_file(fpath):
    """提取规则"""
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
    """修复 Unicode 转义"""
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
    
    # 分类和优化
    l1_rules = {}
    l2_rules = {}
    l3_rules = {}
    
    for name, text in all_rules.items():
        level = classify_rule(name, text)
        optimized = optimize_rule(name, text)
        
        if level == 'L1':
            l1_rules[name] = optimized
        elif level == 'L2':
            l2_rules[name] = optimized
        else:
            l3_rules[name] = optimized
    
    print('L1 (高置信度): {} 条'.format(len(l1_rules)))
    print('L2 (中置信度): {} 条'.format(len(l2_rules)))
    print('L3 (低置信度): {} 条'.format(len(l3_rules)))
    
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
    
    # 生成规则索引
    index = {
        'L1': list(l1_rules.keys()),
        'L2': list(l2_rules.keys()),
        'L3': list(l3_rules.keys()),
        'total': len(all_rules),
    }
    index_path = os.path.join(OUTPUT_DIR, 'rule_index.json')
    json.dump(index, open(index_path, 'w'), indent=2)
    print('写入：{}'.format(index_path))
    
    print('\n✅ 规则优化完成!')
    print('下一步：使用 L1 规则进行扫描，验证误报率是否降低')


if __name__ == '__main__':
    main()
