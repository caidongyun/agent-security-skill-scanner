#!/usr/bin/env python3
"""
Gitleaks 规则转换器

将 gitleaks.toml 转换为 Scanner v5.8.0 的 PatternEngine 格式
"""

import json
import re
from pathlib import Path

# 配置
GITLEAKS_TOML = Path(__file__).parent.parent / 'external-rules' / 'gitleaks.toml'
OUTPUT_JSON = Path(__file__).parent.parent / 'rules' / 'gitleaks_patterns.json'

# 攻击类型映射（根据 Gitleaks 规则 ID 分类）
ATTACK_TYPE_MAP = {
    # 凭证窃取类
    '1password': 'credential_theft',
    'adafruit': 'credential_theft',
    'adobe': 'credential_theft',
    'age': 'credential_theft',
    'airtable': 'credential_theft',
    'algolia': 'credential_theft',
    'alibaba': 'credential_theft',
    'asana': 'credential_theft',
    'atlassian': 'credential_theft',
    'authress': 'credential_theft',
    'aws': 'credential_theft',
    'azure': 'credential_theft',
    'beamer': 'credential_theft',
    'bitbucket': 'credential_theft',
    'bittrex': 'credential_theft',
    'clojars': 'credential_theft',
    'cloudflare': 'credential_theft',
    'codecov': 'credential_theft',
    'coinbase': 'credential_theft',
    'confluent': 'credential_theft',
    'contentful': 'credential_theft',
    'databricks': 'credential_theft',
    'datadog': 'credential_theft',
    'definednetworking': 'credential_theft',
    'digitalocean': 'credential_theft',
    'discord': 'credential_theft',
    'doppler': 'credential_theft',
    'droneci': 'credential_theft',
    'dropbox': 'credential_theft',
    'duffel': 'credential_theft',
    'dynatrace': 'credential_theft',
    'easypost': 'credential_theft',
    'etsy': 'credential_theft',
    'facebook': 'credential_theft',
    'fastly': 'credential_theft',
    'finicity': 'credential_theft',
    'finnhub': 'credential_theft',
    'flickr': 'credential_theft',
    'flutterwave': 'credential_theft',
    'frameio': 'credential_theft',
    'freshbooks': 'credential_theft',
    'gcp': 'credential_theft',
    'github': 'credential_theft',
    'gitlab': 'credential_theft',
    'gitter': 'credential_theft',
    'gocardless': 'credential_theft',
    'grafana': 'credential_theft',
    'hashicorp': 'credential_theft',
    'heroku': 'credential_theft',
    'hubspot': 'credential_theft',
    'huggingface': 'credential_theft',
    'infracost': 'credential_theft',
    'intercom': 'credential_theft',
    'jfrog': 'credential_theft',
    'jwt': 'credential_theft',
    'kraken': 'credential_theft',
    'kucoin': 'credential_theft',
    'launchdarkly': 'credential_theft',
    'linear': 'credential_theft',
    'linkedin': 'credential_theft',
    'lob': 'credential_theft',
    'mailchimp': 'credential_theft',
    'mailgun': 'credential_theft',
    'mapbox': 'credential_theft',
    'mattermost': 'credential_theft',
    'messagebird': 'credential_theft',
    'microsoft': 'credential_theft',
    'netlify': 'credential_theft',
    'newrelic': 'credential_theft',
    'npm': 'credential_theft',
    'nuget': 'credential_theft',
    'nytimes': 'credential_theft',
    'octopusdeploy': 'credential_theft',
    'okta': 'credential_theft',
    'openai': 'credential_theft',
    'openshift': 'credential_theft',
    'plaid': 'credential_theft',
    'planetscale': 'credential_theft',
    'postman': 'credential_theft',
    'prefect': 'credential_theft',
    'privatekey': 'credential_theft',
    'pulumi': 'credential_theft',
    'pypi': 'credential_theft',
    'rapidapi': 'credential_theft',
    'rubygems': 'credential_theft',
    'scalingo': 'credential_theft',
    'sendbird': 'credential_theft',
    'sendgrid': 'credential_theft',
    'sendinblue': 'credential_theft',
    'sentry': 'credential_theft',
    'shippo': 'credential_theft',
    'shopify': 'credential_theft',
    'sidekiq': 'credential_theft',
    'slack': 'credential_theft',
    'snyk': 'credential_theft',
    'square': 'credential_theft',
    'squareup': 'credential_theft',
    'stripe': 'credential_theft',
    'sumologic': 'credential_theft',
    'teams': 'credential_theft',
    'telegram': 'credential_theft',
    'travisci': 'credential_theft',
    'twitch': 'credential_theft',
    'twitter': 'credential_theft',
    'typeform': 'credential_theft',
    'vault': 'credential_theft',
    'yandex': 'credential_theft',
    'zendesk': 'credential_theft',
    
    # 通用/其他
    'generic': 'obfuscation',
}

# 权重映射（根据熵值和严重程度）
def calculate_weight(rule: dict) -> int:
    """根据规则特征计算权重"""
    entropy = rule.get('entropy', 0)
    # 熵值可能是字符串，需要转换
    try:
        entropy = float(entropy) if entropy else 0
    except (ValueError, TypeError):
        entropy = 0
    
    keywords = rule.get('keywords', [])
    secret_group = rule.get('secret_group', 0)
    
    # 基础权重
    base_weight = 40
    
    # 熵值加成（高熵值=更可能是真密钥）
    if entropy >= 4.5:
        base_weight += 15
    elif entropy >= 4.0:
        base_weight += 10
    elif entropy >= 3.5:
        base_weight += 5
    
    # 关键词加成
    if keywords:
        base_weight += min(len(keywords) * 2, 10)
    
    # 限制在 40-60 之间
    return min(max(base_weight, 40), 60)


def parse_toml_manual(content: str) -> list:
    """
    手动解析 TOML（避免依赖 toml 库）
    提取 [[rules]] 块
    """
    rules = []
    current_rule = {}
    in_rules = False
    in_array = False
    array_key = None
    array_values = []
    
    for line in content.split('\n'):
        line = line.strip()
        
        # 跳过注释和空行
        if not line or line.startswith('#'):
            continue
        
        # 新的 rules 块开始
        if line == '[[rules]]':
            if current_rule:
                rules.append(current_rule)
            current_rule = {}
            in_rules = True
            continue
        
        if not in_rules:
            continue
        
        # 键值对
        if '=' in line and not line.startswith('['):
            if in_array:
                # 结束之前的数组
                current_rule[array_key] = array_values
                in_array = False
            
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # 解析值
            if value.startswith('['):
                # 数组开始
                if value.endswith(']'):
                    # 单行数组
                    value = value[1:-1]
                    current_rule[key] = [v.strip().strip('"\'') for v in value.split(',') if v.strip()]
                else:
                    # 多行数组
                    in_array = True
                    array_key = key
                    array_values = [value[1:].strip().strip('"\'')]
            elif value.startswith('"') or value.startswith("'"):
                # 字符串
                current_rule[key] = value.strip('"\'')
            elif value.isdigit():
                # 数字
                current_rule[key] = int(value)
            elif value == 'true':
                current_rule[key] = True
            elif value == 'false':
                current_rule[key] = False
            else:
                current_rule[key] = value
        
        elif in_array and line.startswith(']'):
            # 数组结束
            array_values.append(line[:-1].strip().strip('"\''))
            current_rule[array_key] = array_values
            in_array = False
        elif in_array:
            # 数组内容
            array_values.append(line.rstrip(',').strip('"\''))
    
    # 最后一个规则
    if current_rule:
        if in_array and array_key:
            current_rule[array_key] = array_values
        rules.append(current_rule)
    
    return rules


def convert_rules(gitleaks_rules: list) -> dict:
    """转换为 Scanner PatternEngine 格式"""
    patterns = []
    
    for rule in gitleaks_rules:
        rule_id = rule.get('id', 'UNKNOWN')
        description = rule.get('description', '')
        regex = rule.get('regex', '')
        keywords = rule.get('keywords', [])
        entropy = rule.get('entropy', 0)
        
        # 跳过没有 regex 的规则
        if not regex:
            continue
        
        # 确定攻击类型
        attack_type = 'credential_theft'  # 默认
        for key, atype in ATTACK_TYPE_MAP.items():
            if key in rule_id.lower():
                attack_type = atype
                break
        
        # 计算权重
        weight = calculate_weight(rule)
        
        # 创建 pattern
        pattern = {
            'attack_type': attack_type,
            'pattern': regex,
            'weight': weight,
            'source': f'gitleaks/{rule_id}',
            'description': description,
            'entropy': entropy,
            'keywords': keywords
        }
        
        patterns.append(pattern)
    
    return {'patterns': patterns, 'total': len(patterns)}


def main():
    print(f"📄 读取 Gitleaks 规则：{GITLEAKS_TOML}")
    
    if not GITLEAKS_TOML.exists():
        print(f"❌ 文件不存在：{GITLEAKS_TOML}")
        return 1
    
    # 读取 TOML
    with open(GITLEAKS_TOML, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析规则
    print("🔍 解析 TOML...")
    gitleaks_rules = parse_toml_manual(content)
    print(f"✅ 解析到 {len(gitleaks_rules)} 条规则")
    
    # 转换
    print("🔄 转换为 Scanner 格式...")
    converted = convert_rules(gitleaks_rules)
    
    # 统计
    attack_type_counts = {}
    for p in converted['patterns']:
        atype = p['attack_type']
        attack_type_counts[atype] = attack_type_counts.get(atype, 0) + 1
    
    print(f"\n📊 攻击类型分布:")
    for atype, count in sorted(attack_type_counts.items(), key=lambda x: -x[1]):
        print(f"  {atype}: {count} 条")
    
    # 保存
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(converted, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 已保存：{OUTPUT_JSON}")
    print(f"   总计：{converted['total']} 条 patterns")
    
    # 显示前 5 条示例
    print(f"\n📋 前 5 条示例:")
    for i, p in enumerate(converted['patterns'][:5], 1):
        print(f"  {i}. [{p['attack_type']}] {p['source']}")
        print(f"     权重：{p['weight']}, 熵值：{p.get('entropy', 0)}")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main() or 0)
