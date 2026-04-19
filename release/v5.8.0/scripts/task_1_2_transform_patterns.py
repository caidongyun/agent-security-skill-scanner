#!/usr/bin/env python3
"""
Task 1.2: Pattern 转化 (Semgrep → v5.8.0)
"""

import os
import sys
import json
import re
import yaml
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Task1.2')

WORKSPACE_DIR = Path('/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/release/v5.8.0')
SEMGREP_RULES_FILE = WORKSPACE_DIR / 'reports' / 'semgrep_python_rules.json'
SEMGREP_RULES_DIR = WORKSPACE_DIR / 'semgrep-rules'
OUTPUT_FILE = WORKSPACE_DIR / 'rules' / 'v580_patterns_semgrep.yaml'

def transform():
    """转化 Semgrep 规则为 v5.8.0 Patterns"""
    logger.info("🔄 开始转化 Semgrep 规则为 Patterns")
    
    # 1. 加载 Semgrep 规则元数据
    with open(SEMGREP_RULES_FILE, 'r', encoding='utf-8') as f:
        semgrep_data = json.load(f)
    
    logger.info(f"  加载 {len(semgrep_data['rules'])} 条 Semgrep 规则")
    
    # 2. 转化规则
    patterns = []
    pattern_id_start = 36  # 从 V580-P0036 开始
    
    for rule_meta in semgrep_data['rules']:
        try:
            # 读取完整规则文件
            rule_file = SEMGREP_RULES_DIR / rule_meta['file']
            if not rule_file.exists():
                continue
            
            with open(rule_file, 'r', encoding='utf-8') as f:
                rule_content = yaml.safe_load(f)
            
            if not rule_content or 'rules' not in rule_content:
                continue
            
            rules = rule_content['rules']
            if not isinstance(rules, list) or len(rules) == 0:
                continue
            
            rule = rules[0]
            
            # 提取 pattern
            semgrep_patterns = extract_patterns(rule)
            
            if not semgrep_patterns:
                continue
            
            # 转化为 v5.8.0 pattern
            for i, semgrep_pattern in enumerate(semgrep_patterns):
                v580_pattern = convert_to_v580_pattern(
                    semgrep_pattern,
                    rule,
                    pattern_id_start + len(patterns)
                )
                
                if v580_pattern:
                    patterns.append(v580_pattern)
                    
        except Exception as e:
            logger.warning(f"  跳过 {rule_meta['file']}: {str(e)}")
        
        # 限制 200 个 patterns
        if len(patterns) >= 200:
            break
    
    # 3. 保存结果
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    output_content = {
        'version': 'v5.8.0-Enhanced',
        'source': 'Semgrep',
        'created_at': datetime.now().isoformat(),
        'total_patterns': len(patterns),
        'patterns': patterns
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(output_content, f, allow_unicode=True, default_flow_style=False)
    
    logger.info(f"✅ 转化完成，保存至 {OUTPUT_FILE}")
    logger.info(f"  转化 Patterns: {len(patterns)} 个")
    
    return {'output_file': str(OUTPUT_FILE), 'total_patterns': len(patterns)}

def extract_patterns(rule: dict) -> List[str]:
    """从 Semgrep 规则提取 patterns"""
    patterns = []
    
    # 直接 pattern
    if 'pattern' in rule:
        patterns.append(rule['pattern'])
    
    # patterns 列表
    if 'patterns' in rule:
        for p in rule['patterns']:
            if isinstance(p, str):
                patterns.append(p)
            elif isinstance(p, dict) and 'pattern' in p:
                patterns.append(p['pattern'])
    
    return patterns

def convert_to_v580_pattern(semgrep_pattern: str, rule: dict, pattern_id: int) -> dict:
    """将 Semgrep pattern 转化为 v5.8.0 pattern"""
    
    # Semgrep pattern 示例：exec($ARG)
    # 转化为正则：exec\s*\([^)]*\)
    
    try:
        # 转义特殊字符
        regex = re.escape(semgrep_pattern)
        
        # 替换 Semgrep 变量 ($ARG, $X, etc) 为正则
        regex = re.sub(r'\\\$[A-Z_]+', r'[^)]*', regex)
        
        # 替换省略号 (...) 为 .*
        regex = re.sub(r'\\\.\.\.', r'.*', regex)
        
        # 添加单词边界
        regex = r'\b' + regex + r'\b'
        
        # 测试正则是否有效
        re.compile(regex)
        
        return {
            'id': f'V580-P{pattern_id:04d}',
            'name': rule.get('id', 'unknown')[:50],
            'pattern': regex,
            'severity': map_severity(rule.get('severity', 'WARNING')),
            'confidence': 85,
            'source': 'semgrep',
            'original_id': rule.get('id', 'unknown'),
            'description': rule.get('message', '')[:200]
        }
    
    except Exception as e:
        logger.warning(f"  Pattern 转化失败：{str(e)}")
        return None

def map_severity(semgrep_severity: str) -> str:
    """映射严重级别"""
    mapping = {
        'ERROR': 'CRITICAL',
        'WARNING': 'HIGH',
        'INFO': 'MEDIUM',
        'UNKNOWN': 'LOW'
    }
    return mapping.get(semgrep_severity, 'MEDIUM')

if __name__ == '__main__':
    result = transform()
    print(json.dumps(result, indent=2))
