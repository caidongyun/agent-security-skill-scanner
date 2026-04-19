#!/usr/bin/env python3
"""
修复失败的 Patterns
"""

import yaml
import re
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('PatternFixer')

WORKSPACE_DIR = Path('/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/release/v5.8.0')
PATTERNS_FILE = WORKSPACE_DIR / 'rules' / 'v580_patterns_semgrep.yaml'

# 修复映射
FIXES = {
    'V580-P0069': r'\b\w+\.map\s*\([^)]*\)\b',  # .map(...)
    'V580-P0089': r'\bexec\s*\([^)]*\)\b',       # exec(...)
    'V580-P0094': r'\beval\s*\([^)]*\)\b',       # eval(...)
    'V580-P0096': r'\b\w+\.exec_command\s*\([^)]*\)\b',  # .exec_command(...)
    'V580-P0098': r'\blogging\.config\.listen\s*\([^)]*\)\b',  # logging.config.listen(...)
    'V580-P0105': r'\b\w+\.delete\s*\(\s*\)\s*\.where\s*\([^)]*\)\b',  # .delete().where(...)
}

def fix():
    """修复失败的 patterns"""
    logger.info("🔧 开始修复失败的 Patterns")
    
    # 加载 patterns
    with open(PATTERNS_FILE, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    fixed_count = 0
    for pattern in data['patterns']:
        pattern_id = pattern['id']
        
        if pattern_id in FIXES:
            old_pattern = pattern['pattern']
            new_pattern = FIXES[pattern_id]
            
            # 验证新正则
            try:
                re.compile(new_pattern)
                pattern['pattern'] = new_pattern
                logger.info(f"  ✅ {pattern_id}: {old_pattern[:50]}... → {new_pattern[:50]}...")
                fixed_count += 1
            except Exception as e:
                logger.error(f"  ❌ {pattern_id} 修复失败：{str(e)}")
    
    # 保存修复后的 patterns
    with open(PATTERNS_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    
    logger.info(f"✅ 修复完成，共修复 {fixed_count}/{len(FIXES)} 个 patterns")
    
    return {'fixed_count': fixed_count, 'total': len(FIXES)}

if __name__ == '__main__':
    result = fix()
    print(f"修复结果：{result}")
