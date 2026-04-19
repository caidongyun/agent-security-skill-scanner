#!/usr/bin/env python3
"""
最终 Pattern 修复 - 去掉末尾错误的 \b
"""

import yaml
import re
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('FinalPatternFix')

WORKSPACE_DIR = Path('/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/release/v5.8.0')
PATTERNS_FILE = WORKSPACE_DIR / 'rules' / 'v580_patterns_semgrep.yaml'

def fix():
    """修复 patterns"""
    logger.info("🔧 最终 Pattern 修复")
    
    # 加载 patterns
    with open(PATTERNS_FILE, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    fixed = []
    for pattern in data['patterns']:
        old = pattern['pattern']
        
        # 修复：去掉函数调用 pattern 末尾的 \b
        if old.endswith(r'\b') and r'\(' in old:
            new = old[:-2]  # 去掉 \b
            try:
                re.compile(new)
                pattern['pattern'] = new
                fixed.append((pattern['id'], old, new))
                logger.info(f"  ✅ {pattern['id']}: 已修复")
            except:
                pass
    
    # 保存
    with open(PATTERNS_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    
    logger.info(f"✅ 修复完成，共修复 {len(fixed)} 个 patterns")
    
    for pid, old, new in fixed[:10]:
        logger.debug(f"  {pid}: {old[:50]} → {new[:50]}")
    
    return len(fixed)

if __name__ == '__main__':
    count = fix()
    print(f"修复数量：{count}")
