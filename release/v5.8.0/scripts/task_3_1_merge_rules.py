#!/usr/bin/env python3
"""
Task 3.1: 规则库合并
融合 Semgrep/Bandit/Trivy 规则到 v5.8.0
"""

import os
import sys
import json
import yaml
import re
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Task3.1')

WORKSPACE_DIR = Path('/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/release/v5.8.0')

# 输入文件
CURRENT_RULES = WORKSPACE_DIR / 'rules' / 'v580_current.yaml'
SEMGREP_PATTERNS = WORKSPACE_DIR / 'rules' / 'v580_patterns_semgrep.yaml'
BANDIT_RULES = WORKSPACE_DIR / 'rules' / 'bandit_converted.yaml'  # 待生成
TRIVY_RULES = WORKSPACE_DIR / 'rules' / 'trivy_converted.yaml'    # 待生成

# 输出文件
ENHANCED_RULES = WORKSPACE_DIR / 'rules' / 'v580_enhanced.yaml'

def merge():
    """合并规则库"""
    logger.info("🔀 开始规则库合并")
    
    all_rules = []
    
    # 1. 加载当前规则 (如果有)
    if CURRENT_RULES.exists():
        with open(CURRENT_RULES, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        current = data.get('rules', [])
        logger.info(f"  加载当前规则：{len(current)} 条")
        all_rules.extend(current)
    else:
        logger.info("  ℹ️ 当前规则文件不存在，跳过")
    
    # 2. 加载 Semgrep Patterns
    if SEMGREP_PATTERNS.exists():
        with open(SEMGREP_PATTERNS, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        semgrep = data.get('patterns', [])
        logger.info(f"  加载 Semgrep Patterns: {len(semgrep)} 个")
        # 转为规则格式
        for p in semgrep:
            all_rules.append({
                'id': p['id'],
                'pattern': p['pattern'],
                'severity': p['severity'],
                'confidence': p.get('confidence', 85),
                'source': 'semgrep',
                'type': 'pattern'
            })
    else:
        logger.info("  ℹ️ Semgrep Patterns 文件不存在，跳过")
    
    # 3. 加载 Bandit 规则 (如果有)
    if BANDIT_RULES.exists():
        with open(BANDIT_RULES, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        bandit = data.get('rules', [])
        logger.info(f"  加载 Bandit 规则：{len(bandit)} 条")
        all_rules.extend(bandit)
    else:
        logger.info("  ℹ️ Bandit 规则文件不存在，跳过")
    
    # 4. 加载 Trivy 规则 (如果有)
    if TRIVY_RULES.exists():
        with open(TRIVY_RULES, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        trivy = data.get('rules', [])
        logger.info(f"  加载 Trivy 规则：{len(trivy)} 条")
        all_rules.extend(trivy)
    else:
        logger.info("  ℹ️ Trivy 规则文件不存在，跳过")
    
    # 5. 去重
    logger.info(f"  去重前：{len(all_rules)} 条")
    all_rules = deduplicate_rules(all_rules)
    logger.info(f"  去重后：{len(all_rules)} 条")
    
    # 6. 保存
    ENHANCED_RULES.parent.mkdir(parents=True, exist_ok=True)
    
    output_data = {
        'version': 'v5.8.0-Enhanced',
        'created_at': datetime.now().isoformat(),
        'total_rules': len(all_rules),
        'sources': {
            'current': len([r for r in all_rules if r.get('source') == 'native']),
            'semgrep': len([r for r in all_rules if r.get('source') == 'semgrep']),
            'bandit': len([r for r in all_rules if r.get('source') == 'bandit']),
            'trivy': len([r for r in all_rules if r.get('source') == 'trivy'])
        },
        'rules': all_rules
    }
    
    with open(ENHANCED_RULES, 'w', encoding='utf-8') as f:
        yaml.dump(output_data, f, allow_unicode=True, default_flow_style=False)
    
    logger.info(f"✅ 规则库合并完成")
    logger.info(f"  总规则数：{len(all_rules)} 条")
    logger.info(f"  保存至：{ENHANCED_RULES}")
    
    return {'output_file': str(ENHANCED_RULES), 'total_rules': len(all_rules), 'sources': output_data['sources']}

def deduplicate_rules(rules: list) -> list:
    """去重规则"""
    seen = set()
    unique = []
    
    for rule in rules:
        # 基于 pattern 去重
        pattern = rule.get('pattern', '')
        rule_id = rule.get('id', '')
        key = f"{pattern}:{rule_id}"
        
        if key not in seen:
            seen.add(key)
            unique.append(rule)
    
    return unique

if __name__ == '__main__':
    result = merge()
    print(json.dumps(result, indent=2))
