#!/usr/bin/env python3
"""
威胁情报更新脚本

每日自动更新威胁情报
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
INTEL_DIR = BASE_DIR / "threat_intel"
INTEL_DIR.mkdir(parents=True, exist_ok=True)

def fetch_github_malware():
    """从 GitHub 获取恶意样本情报"""
    print("  📦 GitHub 恶意包情报...")
    
    # 模拟数据（实际应调用 API）
    intel = {
        'source': 'github',
        'updated_at': datetime.now().isoformat(),
        'packages': [
            {'name': 'evil-pkg-1', 'type': 'npm', 'severity': 'high'},
            {'name': 'malware-lib', 'type': 'pypi', 'severity': 'critical'},
        ]
    }
    
    return intel

def fetch_mitre_attack():
    """从 MITRE ATT&CK 获取战术技术"""
    print("  🎯 MITRE ATT&CK 情报...")
    
    intel = {
        'source': 'mitre_attack',
        'updated_at': datetime.now().isoformat(),
        'techniques': [
            {'id': 'T1195', 'name': 'Supply Chain Compromise'},
            {'id': 'T1059', 'name': 'Command and Scripting Interpreter'},
        ]
    }
    
    return intel

def fetch_cve():
    """获取最新 CVE"""
    print("  🦠 CVE 情报...")
    
    intel = {
        'source': 'cve',
        'updated_at': datetime.now().isoformat(),
        'cves': [
            {'id': 'CVE-2026-0001', 'severity': 'critical'},
        ]
    }
    
    return intel

def main():
    print("="*60)
    print("🔄 威胁情报更新")
    print("="*60)
    
    all_intel = {
        'updated_at': datetime.now().isoformat(),
        'sources': {},
    }
    
    # 获取各来源情报
    sources = [
        ('github', fetch_github_malware),
        ('mitre', fetch_mitre_attack),
        ('cve', fetch_cve),
    ]
    
    for name, fetch_func in sources:
        try:
            intel = fetch_func()
            all_intel['sources'][name] = intel
            print(f"  ✅ {name} 完成")
        except Exception as e:
            print(f"  ❌ {name} 失败：{e}")
    
    # 保存情报
    intel_file = INTEL_DIR / f"intel_{datetime.now().strftime('%Y%m%d')}.json"
    with open(intel_file, 'w') as f:
        json.dump(all_intel, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 情报已保存：{intel_file}")
    print("="*60)

if __name__ == '__main__':
    main()
