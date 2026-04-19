#!/usr/bin/env python3
"""
Rule Engine V2 - 集成 AST 引擎的增强版
"""

import re
import yaml
from pathlib import Path
from typing import List, Dict
import sys
sys.path.insert(0, str(Path(__file__).parent))
from ast_engine import ASTEngine, ASTHit


class RuleEngineV2:
    """增强版规则引擎 (正则 + AST)"""
    
    def __init__(self, rules_file: str = None):
        self.rules = self.load_rules(rules_file)
        self.ast_engine = ASTEngine()
    
    def load_rules(self, rules_file: str) -> List[Dict]:
        """加载规则"""
        if not rules_file:
            rules_file = Path(__file__).parent.parent / 'rules' / 'v580_enhanced.yaml'
        
        if not Path(rules_file).exists():
            return []
        
        with open(rules_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return data.get('rules', [])
    
    def scan(self, file_path: str, content: str) -> 'ScanResult':
        """
        扫描文件
        
        流程:
        1. Pattern 匹配 (快速)
        2. 正则规则匹配 (如果 Pattern 命中≥2 条)
        3. AST 深度分析 (如果正则命中≥3 条)
        """
        # 1. Pattern 匹配
        pattern_hits = self.pattern_scan(content)
        
        # 2. 正则规则匹配
        regex_hits = []
        if len(pattern_hits) >= 2:
            regex_hits = self.regex_scan(content)
        
        # 3. AST 深度分析
        ast_hits = []
        if len(regex_hits) >= 3:
            ast_hits = self.ast_engine.scan(file_path, content)
        
        # 合并结果
        return ScanResult(
            file_path=file_path,
            pattern_hits=pattern_hits,
            regex_hits=regex_hits,
            ast_hits=ast_hits,
            total_hits=len(pattern_hits) + len(regex_hits) + len(ast_hits),
            risk_level=self.calculate_risk(pattern_hits, regex_hits, ast_hits),
            engines_triggered=self.get_triggered_engines(pattern_hits, regex_hits, ast_hits)
        )
    
    def pattern_scan(self, content: str) -> List[Dict]:
        """Pattern 扫描 (快速)"""
        # 简化实现，实际应加载 patterns 文件
        hits = []
        
        # 示例 patterns
        patterns = [
            (r'\bexec\s*\([^)]*\)', 'PATTERN-EXEC'),
            (r'\beval\s*\([^)]*\)', 'PATTERN-EVAL'),
            (r'\bos\.system\s*\([^)]*\)', 'PATTERN-SYSTEM'),
        ]
        
        for pattern, pattern_id in patterns:
            if re.search(pattern, content):
                hits.append({'id': pattern_id, 'type': 'pattern'})
        
        return hits
    
    def regex_scan(self, content: str) -> List[Dict]:
        """正则规则扫描"""
        hits = []
        
        for rule in self.rules:
            if 'pattern' in rule:
                try:
                    if re.search(rule['pattern'], content):
                        hits.append({
                            'id': rule.get('id', 'UNKNOWN'),
                            'type': 'regex',
                            'severity': rule.get('severity', 'MEDIUM')
                        })
                except:
                    pass
        
        return hits
    
    def calculate_risk(self, pattern_hits: list, regex_hits: list, ast_hits: list) -> str:
        """计算风险等级"""
        total = len(pattern_hits) + len(regex_hits) + len(ast_hits)
        
        # 有 AST 命中 → CRITICAL
        if ast_hits:
            return 'CRITICAL'
        
        # 有多个正则命中 → HIGH
        if len(regex_hits) >= 3:
            return 'HIGH'
        
        # 有 Pattern 命中 → MEDIUM
        if pattern_hits:
            return 'MEDIUM'
        
        return 'SAFE'
    
    def get_triggered_engines(self, pattern_hits: list, regex_hits: list, ast_hits: list) -> List[str]:
        """获取触发的引擎"""
        engines = []
        
        if pattern_hits:
            engines.append('pattern')
        if regex_hits:
            engines.append('regex')
        if ast_hits:
            engines.append('ast')
        
        return engines


class ScanResult:
    """扫描结果"""
    
    def __init__(self, file_path: str, pattern_hits: list, regex_hits: list, 
                 ast_hits: list, total_hits: int, risk_level: str, engines_triggered: list):
        self.file_path = file_path
        self.pattern_hits = pattern_hits
        self.regex_hits = regex_hits
        self.ast_hits = ast_hits
        self.total_hits = total_hits
        self.risk_level = risk_level
        self.engines_triggered = engines_triggered
    
    def to_dict(self) -> Dict:
        """转为字典"""
        return {
            'file': self.file_path,
            'risk_level': self.risk_level,
            'total_hits': self.total_hits,
            'pattern_hits': len(self.pattern_hits),
            'regex_hits': len(self.regex_hits),
            'ast_hits': len(self.ast_hits),
            'engines': self.engines_triggered
        }


# 测试
if __name__ == '__main__':
    engine = RuleEngineV2()
    
    test_code = """
import os
password = "secret123"
exec(user_input)
os.system("ls -la")
"""
    
    result = engine.scan("test.py", test_code)
    print(f"扫描结果: {result.to_dict()}")
