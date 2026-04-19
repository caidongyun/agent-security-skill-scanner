#!/usr/bin/env python3
"""
Task 1.1: Semgrep 规则收集
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Task1.1')

WORKSPACE_DIR = Path('/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/release/v5.8.0')
SEMGREP_RULES_DIR = WORKSPACE_DIR / 'semgrep-rules'
OUTPUT_FILE = WORKSPACE_DIR / 'reports' / 'semgrep_python_rules.json'

def collect():
    """收集 Semgrep Python 规则"""
    logger.info("🔍 开始收集 Semgrep Python 规则")
    
    # 1. 克隆规则仓库
    if not SEMGREP_RULES_DIR.exists():
        logger.info("📥 克隆 Semgrep 规则仓库...")
        subprocess.run(
            ['git', 'clone', '--depth', '1', 'https://github.com/returntocorp/semgrep-rules.git', str(SEMGREP_RULES_DIR)],
            check=True,
            cwd=str(WORKSPACE_DIR)
        )
        logger.info("✅ 克隆完成")
    else:
        logger.info("ℹ️ 规则仓库已存在，跳过克隆")
    
    # 2. 统计 Python 规则
    logger.info("📊 统计 Python 规则...")
    python_rules_dir = SEMGREP_RULES_DIR / 'python'
    
    rule_files = list(python_rules_dir.glob('**/*.yaml')) + list(python_rules_dir.glob('**/*.yml'))
    logger.info(f"  发现 {len(rule_files)} 个规则文件")
    
    # 3. 提取规则元数据
    rules_metadata = []
    for rule_file in rule_files[:500]:  # 限制 500 个
        try:
            metadata = extract_rule_metadata(rule_file)
            if metadata:
                rules_metadata.append(metadata)
        except Exception as e:
            logger.warning(f"  跳过 {rule_file}: {str(e)}")
    
    # 4. 保存结果
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    result = {
        'collect_time': datetime.now().isoformat(),
        'total_files': len(rule_files),
        'extracted_rules': len(rules_metadata),
        'rules': rules_metadata
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ 收集完成，保存至 {OUTPUT_FILE}")
    logger.info(f"  总文件数：{len(rule_files)}")
    logger.info(f"  提取规则：{len(rules_metadata)}")
    
    return {'output_file': str(OUTPUT_FILE), 'total_rules': len(rules_metadata)}

def extract_rule_metadata(rule_file: Path) -> dict:
    """提取规则元数据"""
    import yaml
    
    with open(rule_file, 'r', encoding='utf-8') as f:
        content = yaml.safe_load(f)
    
    if not content or 'rules' not in content:
        return None
    
    rules = content['rules']
    if not isinstance(rules, list) or len(rules) == 0:
        return None
    
    rule = rules[0]
    return {
        'id': rule.get('id', 'unknown'),
        'name': rule.get('message', rule.get('id', 'unknown'))[:100],
        'severity': rule.get('severity', 'INFO'),
        'languages': rule.get('languages', []),
        'file': str(rule_file.relative_to(SEMGREP_RULES_DIR)),
        'has_patterns': 'patterns' in rule or 'pattern' in rule,
        'pattern_count': len(rule.get('patterns', [])) if 'patterns' in rule else 1
    }

if __name__ == '__main__':
    result = collect()
    print(json.dumps(result, indent=2))
