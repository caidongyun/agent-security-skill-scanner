#!/usr/bin/env python3
"""YARA 规则生成器"""

import json
from pathlib import Path
from typing import List, Dict

class YaraRuleGenerator:
    """YARA 规则生成器"""
    
    def __init__(self, samples_dir: str):
        self.samples_dir = Path(samples_dir)
        self.rules = []
    
    def analyze_samples(self) -> Dict:
        """分析样本特征"""
        stats = {
            'total': 0,
            'attack_types': {},
            'common_imports': set(),
            'common_strings': set(),
        }
        
        for sample_file in self.samples_dir.glob('*.py'):
            stats['total'] += 1
            content = sample_file.read_text()
            
            # 提取导入
            import re
            imports = re.findall(r'^(?:import|from)\s+(\w+)', content, re.MULTILINE)
            stats['common_imports'].update(imports)
            
            # 提取攻击类型
            for attack_type in ['data_exfil', 'code_execution', 'persistence', 'credential_theft']:
                if attack_type in sample_file.name:
                    stats['attack_types'][attack_type] = stats['attack_types'].get(attack_type, 0) + 1
            
            # 常见危险字符串
            dangerous = ['subprocess', 'eval', 'exec', 'socket', 'requests', 'base64']
            for s in dangerous:
                if s in content:
                    stats['common_strings'].add(s)
        
        return stats
    
    def generate_rules(self) -> List[str]:
        """生成 YARA 规则"""
        stats = self.analyze_samples()
        rules = []
        
        # 规则 1: Python 恶意代码通用规则
        rule1 = f'''rule Python_Malicious_General {{
    meta:
        description = "Detects general Python malicious code"
        author = "Sample Generator v2.0"
        severity = "medium"
    
    strings:
        $import_os = "import os"
        $import_sys = "import sys"
        $import_subprocess = "import subprocess"
        $import_socket = "import socket"
    
    condition:
        2 of them
}}'''
        rules.append(('general', rule1))
        
        # 规则 2: 数据外传
        rule2 = '''rule Python_Data_Exfiltration {
    meta:
        description = "Detects Python data exfiltration"
        author = "Sample Generator v2.0"
        severity = "high"
    
    strings:
        $ssh = ".ssh"
        $credential = "credential"
        $base64 = "base64"
        $env_var = "environ"
    
    condition:
        2 of them
}'''
        rules.append(('data_exfil', rule2))
        
        # 规则 3: 代码执行
        rule3 = '''rule Python_Code_Execution {
    meta:
        description = "Detects Python code execution"
        author = "Sample Generator v2.0"
        severity = "high"
    
    strings:
        $subprocess = "subprocess"
        $eval = "eval("
        $exec = "exec("
        $shell = "shell=True"
    
    condition:
        2 of them
}'''
        rules.append(('code_execution', rule3))
        
        # 规则 4: 持久化
        rule4 = '''rule Python_Persistence {
    meta:
        description = "Detects Python persistence mechanisms"
        author = "Sample Generator v2.0"
        severity = "high"
    
    strings:
        $startup = "startup"
        $cron = "cron"
        $systemd = "systemd"
        $registry = "winreg"
    
    condition:
        any of them
}'''
        rules.append(('persistence', rule4))
        
        # 规则 5: 凭据窃取
        rule5 = '''rule Python_Credential_Theft {
    meta:
        description = "Detects Python credential theft"
        author = "Sample Generator v2.0"
        severity = "critical"
    
    strings:
        $ssh_key = "id_rsa"
        $ssh_dir = ".ssh"
        $git_cred = ".git-credentials"
        $browser = "chrome" or "firefox"
    
    condition:
        2 of them
}'''
        rules.append(('credential_theft', rule5))
        
        # 规则 6-10: 更多规则...
        for i in range(6, 11):
            rule = f'''rule Python_Malicious_Pattern_{i:02d} {{
    meta:
        description = "Detects Python malicious pattern {i}"
        author = "Sample Generator v2.0"
        severity = "medium"
    
    strings:
        $s1 = "import"
        $s2 = "def "
        $s3 = "if __name__"
    
    condition:
        all of them
}}'''
            rules.append((f'pattern_{i:02d}', rule))
        
        self.rules = rules
        return rules
    
    def save_rules(self, output_dir: str) -> int:
        """保存规则到文件"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        count = 0
        for name, rule in self.rules:
            rule_file = output_path / f"python_{name}.yar"
            rule_file.write_text(rule)
            count += 1
        
        # 生成合并文件
        all_rules = '\n\n'.join([r[1] for r in self.rules])
        (output_path / 'python_all.yar').write_text(all_rules)
        
        return count


def main():
    import argparse
    parser = argparse.ArgumentParser(description='YARA 规则生成器')
    parser.add_argument('--samples', '-s', default='output/samples/python',
                       help='样本目录')
    parser.add_argument('--output', '-o', default='output/rules',
                       help='输出目录')
    
    args = parser.parse_args()
    
    print(f"📝 分析样本：{args.samples}")
    generator = YaraRuleGenerator(args.samples)
    
    print("🔍 分析样本特征...")
    stats = generator.analyze_samples()
    print(f"   总样本数：{stats['total']}")
    print(f"   攻击类型：{stats['attack_types']}")
    print(f"   常见导入：{len(stats['common_imports'])} 个")
    print()
    
    print("📝 生成 YARA 规则...")
    rules = generator.generate_rules()
    print(f"   生成规则数：{len(rules)}")
    print()
    
    print(f"💾 保存规则到：{args.output}")
    count = generator.save_rules(args.output)
    print(f"   保存规则：{count} 条")
    print()
    print("✅ 规则生成完成!")


if __name__ == '__main__':
    main()
