#!/usr/bin/env python3
"""
AST 引擎 - 基于 Python AST 的深度检测
"""

import ast
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ASTHit:
    """AST 检测结果"""
    rule_id: str
    line: int
    column: int
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    message: str
    code_snippet: str


class ASTEngine:
    """AST 检测引擎"""
    
    def __init__(self):
        self.rules = self.load_rules()
    
    def load_rules(self) -> List[Dict]:
        """加载 AST 规则"""
        # 核心 AST 规则 (50-100 条)
        return [
            # === 代码执行检测 ===
            {
                'id': 'AST-EXEC-001',
                'name': 'exec_call',
                'check': 'call',
                'func_names': ['exec'],
                'severity': 'CRITICAL',
                'message': '使用 exec() 可能导致代码注入'
            },
            {
                'id': 'AST-EVAL-001',
                'name': 'eval_call',
                'check': 'call',
                'func_names': ['eval'],
                'severity': 'CRITICAL',
                'message': '使用 eval() 可能导致代码注入'
            },
            {
                'id': 'AST-COMPILE-001',
                'name': 'compile_call',
                'check': 'call',
                'func_names': ['compile'],
                'severity': 'HIGH',
                'message': '使用 compile() 可能动态生成代码'
            },
            
            # === Shell 注入检测 ===
            {
                'id': 'AST-SYSTEM-001',
                'name': 'os_system_call',
                'check': 'call',
                'attr_names': ['system'],
                'module': 'os',
                'severity': 'CRITICAL',
                'message': 'os.system() 可能导致 shell 注入'
            },
            {
                'id': 'AST-SUBPROCESS-001',
                'name': 'subprocess_call',
                'check': 'call',
                'attr_names': ['call', 'run', 'Popen', 'check_output', 'check_call'],
                'module': 'subprocess',
                'severity': 'HIGH',
                'message': 'subprocess 调用可能执行系统命令'
            },
            
            # === 危险导入检测 ===
            {
                'id': 'AST-IMPORT-001',
                'name': 'dangerous_import',
                'check': 'import',
                'modules': ['os', 'sys', 'subprocess', 'socket', 'ctypes'],
                'severity': 'LOW',
                'message': '导入危险模块'
            },
            
            # === 硬编码凭据检测 ===
            {
                'id': 'AST-PASSWORD-001',
                'name': 'hardcoded_password',
                'check': 'assign',
                'keywords': ['password', 'passwd', 'pwd', 'secret', 'api_key', 'token'],
                'severity': 'HIGH',
                'message': '可能包含硬编码凭据'
            },
            
            # === SQL 注入检测 ===
            {
                'id': 'AST-SQL-001',
                'name': 'sql_string_format',
                'check': 'binop',
                'operators': ['%', '+'],
                'keywords': ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'FROM', 'WHERE'],
                'severity': 'CRITICAL',
                'message': 'SQL 语句字符串拼接可能导致注入'
            },
        ]
    
    def scan(self, file_path: str, content: str) -> List[ASTHit]:
        """扫描文件"""
        hits = []
        
        try:
            # 解析 AST
            tree = ast.parse(content)
            
            # 遍历 AST
            for node in ast.walk(tree):
                # Call 节点检测
                if isinstance(node, ast.Call):
                    hits.extend(self.check_call(node, content))
                
                # Import 节点检测
                elif isinstance(node, ast.Import):
                    hits.extend(self.check_import(node))
                
                elif isinstance(node, ast.ImportFrom):
                    hits.extend(self.check_import_from(node))
                
                # Assign 节点检测
                elif isinstance(node, ast.Assign):
                    hits.extend(self.check_assign(node, content))
                
                # BinOp 节点检测 (SQL 拼接)
                elif isinstance(node, ast.BinOp):
                    hits.extend(self.check_binop(node, content))
            
            return hits
        
        except SyntaxError:
            # Python 文件语法错误，跳过
            return []
        except Exception as e:
            # 其他错误，记录日志
            return []
    
    def check_call(self, node: ast.Call, content: str) -> List[ASTHit]:
        """检查函数调用"""
        hits = []
        
        for rule in self.rules:
            if rule['check'] != 'call':
                continue
            
            # 检查函数名
            if isinstance(node.func, ast.Name):
                if node.func.id in rule.get('func_names', []):
                    hits.append(self.create_hit(rule, node, content))
            
            # 检查属性调用 (如 os.system)
            elif isinstance(node.func, ast.Attribute):
                if node.func.attr in rule.get('attr_names', []):
                    # 检查模块名
                    if isinstance(node.func.value, ast.Name):
                        if node.func.value.id == rule.get('module', ''):
                            hits.append(self.create_hit(rule, node, content))
        
        return hits
    
    def check_import(self, node: ast.Import) -> List[ASTHit]:
        """检查导入语句"""
        hits = []
        
        for rule in self.rules:
            if rule['check'] != 'import':
                continue
            
            for alias in node.names:
                if alias.name in rule.get('modules', []):
                    hits.append(self.create_hit(rule, node, ''))
        
        return hits
    
    def check_import_from(self, node: ast.ImportFrom) -> List[ASTHit]:
        """检查 from import 语句"""
        hits = []
        
        for rule in self.rules:
            if rule['check'] != 'import':
                continue
            
            if node.module in rule.get('modules', []):
                hits.append(self.create_hit(rule, node, ''))
        
        return hits
    
    def check_assign(self, node: ast.Assign, content: str) -> List[ASTHit]:
        """检查赋值语句"""
        hits = []
        
        for rule in self.rules:
            if rule['check'] != 'assign':
                continue
            
            # 检查目标变量名
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id.lower()
                    for keyword in rule.get('keywords', []):
                        if keyword in var_name:
                            # 检查值是否为字符串常量
                            if isinstance(node.value, ast.Constant):
                                if isinstance(node.value.value, str):
                                    hits.append(self.create_hit(rule, node, content))
        
        return hits
    
    def check_binop(self, node: ast.BinOp, content: str) -> List[ASTHit]:
        """检查二元操作 (SQL 拼接)"""
        hits = []
        
        for rule in self.rules:
            if rule['check'] != 'binop':
                continue
            
            # 检查操作符
            op_name = type(node.op).__name__
            if op_name in ['Mod', 'Add']:  # % 或 +
                # 检查是否包含 SQL 关键词
                code = ast.unparse(node) if hasattr(ast, 'unparse') else content
                for keyword in rule.get('keywords', []):
                    if keyword in code.upper():
                        hits.append(self.create_hit(rule, node, content))
                        break
        
        return hits
    
    def create_hit(self, rule: Dict, node: ast.AST, content: str) -> ASTHit:
        """创建检测结果"""
        # 提取代码片段
        code_snippet = ''
        if content:
            lines = content.split('\n')
            if hasattr(node, 'lineno') and node.lineno <= len(lines):
                code_snippet = lines[node.lineno - 1].strip()[:100]
        
        return ASTHit(
            rule_id=rule['id'],
            line=getattr(node, 'lineno', 0),
            column=getattr(node, 'col_offset', 0),
            severity=rule['severity'],
            message=rule['message'],
            code_snippet=code_snippet
        )
    
    def scan_file(self, file_path: str) -> List[ASTHit]:
        """扫描文件 (便捷方法)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.scan(file_path, content)
        except Exception:
            return []


# 测试
if __name__ == '__main__':
    engine = ASTEngine()
    
    # 测试代码
    test_code = """
import os
import subprocess

password = "secret123"
exec(user_input)
os.system("ls -la")
subprocess.call(["echo", "hello"])

query = "SELECT * FROM users WHERE id=" + user_id
"""
    
    hits = engine.scan("test.py", test_code)
    
    print(f"检测到 {len(hits)} 个问题:")
    for hit in hits:
        print(f"  {hit.rule_id} [{hit.severity}] 行{hit.line}: {hit.message}")
