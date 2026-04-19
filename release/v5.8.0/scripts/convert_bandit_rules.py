#!/usr/bin/env python3
"""
转换 Bandit 插件为 v5.8.0 规则
"""

import os
import sys
import yaml
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('BanditConverter')

WORKSPACE_DIR = Path('/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/release/v5.8.0')
BANDIT_PLUGINS_DIR = Path.home() / '.local/lib/python3.13/site-packages/bandit/plugins/'
OUTPUT_FILE = WORKSPACE_DIR / 'rules' / 'bandit_converted.yaml'

def convert():
    """转换 Bandit 规则"""
    logger.info("🔄 转换 Bandit 插件为规则")
    
    # 手动创建核心 Bandit 规则 (基于插件分析)
    bandit_rules = [
        # exec/eval检测
        {
            'id': 'BANDIT-101',
            'name': 'exec_used',
            'pattern': r'\bexec\s*\([^)]*\)',
            'severity': 'CRITICAL',
            'confidence': 95,
            'source': 'bandit',
            'description': '使用 exec() 可能导致代码注入',
            'ast_check': True
        },
        {
            'id': 'BANDIT-102',
            'name': 'eval_used',
            'pattern': r'\beval\s*\([^)]*\)',
            'severity': 'CRITICAL',
            'confidence': 95,
            'source': 'bandit',
            'description': '使用 eval() 可能导致代码注入',
            'ast_check': True
        },
        
        # Shell 注入
        {
            'id': 'BANDIT-601',
            'name': 'os_system_used',
            'pattern': r'\bos\.system\s*\([^)]*\)',
            'severity': 'CRITICAL',
            'confidence': 90,
            'source': 'bandit',
            'description': 'os.system() 可能导致 shell 注入',
            'ast_check': True
        },
        {
            'id': 'BANDIT-602',
            'name': 'subprocess_without_shell',
            'pattern': r'\bsubprocess\.(call|run|Popen)\s*\([^)]*\)',
            'severity': 'HIGH',
            'confidence': 85,
            'source': 'bandit',
            'description': 'subprocess 调用可能执行系统命令'
        },
        {
            'id': 'BANDIT-603',
            'name': 'shell_injection',
            'pattern': r'\bshell\s*=\s*True\b',
            'severity': 'CRITICAL',
            'confidence': 90,
            'source': 'bandit',
            'description': '使用 shell=True 可能导致注入'
        },
        
        # 硬编码凭据
        {
            'id': 'BANDIT-105',
            'name': 'hardcoded_password',
            'pattern': r'\b(password|passwd|pwd)\s*=\s*["\'][^"\']+["\']',
            'severity': 'HIGH',
            'confidence': 85,
            'source': 'bandit',
            'description': '硬编码密码'
        },
        {
            'id': 'BANDIT-106',
            'name': 'hardcoded_secret',
            'pattern': r'\b(secret|api_key|apikey|token)\s*=\s*["\'][^"\']+["\']',
            'severity': 'HIGH',
            'confidence': 80,
            'source': 'bandit',
            'description': '硬编码密钥'
        },
        
        # SQL 注入
        {
            'id': 'BANDIT-608',
            'name': 'sql_injection',
            'pattern': r'(SELECT|INSERT|UPDATE|DELETE).*\+',
            'severity': 'CRITICAL',
            'confidence': 85,
            'source': 'bandit',
            'description': 'SQL 语句字符串拼接可能导致注入'
        },
        
        # 不安全哈希
        {
            'id': 'BANDIT-303',
            'name': 'weak_cryptographic_hash',
            'pattern': r'\b(MD5|SHA1|md5|sha1)\s*\(',
            'severity': 'MEDIUM',
            'confidence': 80,
            'source': 'bandit',
            'description': '使用弱哈希算法'
        },
        
        # 不安全临时文件
        {
            'id': 'BANDIT-108',
            'name': 'insecure_temp_file',
            'pattern': r'/tmp/|/var/tmp/',
            'severity': 'LOW',
            'confidence': 75,
            'source': 'bandit',
            'description': '使用不安全的临时目录'
        },
    ]
    
    # 保存
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    output_data = {
        'version': 'v5.8.0-Enhanced',
        'source': 'Bandit',
        'created_at': datetime.now().isoformat(),
        'total_rules': len(bandit_rules),
        'rules': bandit_rules
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(output_data, f, allow_unicode=True, default_flow_style=False)
    
    logger.info(f"✅ 转换完成")
    logger.info(f"  规则数：{len(bandit_rules)} 条")
    logger.info(f"  保存至：{OUTPUT_FILE}")
    
    return {'output_file': str(OUTPUT_FILE), 'total_rules': len(bandit_rules)}

if __name__ == '__main__':
    result = convert()
    print(json.dumps(result, indent=2))
