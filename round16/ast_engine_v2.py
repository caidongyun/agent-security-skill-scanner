#!/usr/bin/env python3
"""
Round 16 v2: AST 检测引擎 (优化版)

优化内容:
1. 调整风险评分权重
2. 新增检测规则
3. 白名单机制
4. 阈值优化
"""

import ast
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime

# 白名单 (常见安全库)
SAFE_MODULES = {
    'json', 'os', 'sys', 're', 'math', 'random', 'time', 'datetime',
    'collections', 'itertools', 'functools', 'pathlib', 'typing'
}

# 危险模块
DANGEROUS_MODULES = {
    'subprocess': 30,
    'socket': 25,
    'requests': 20,
    'urllib': 20,
    'http': 20,
    'base64': 25,
    'pickle': 30,
    'marshal': 30,
    'ctypes': 35,
}

# 危险函数
DANGEROUS_FUNCS = {
    'eval': 40,
    'exec': 40,
    'compile': 35,
    '__import__': 25,
    'open': 12,
    'write': 12,
    'read': 10,
}

class OptimizedASTScanner:
    """优化版 AST 扫描器"""
    
    def __init__(self):
        self.findings = []
    
    def scan_file(self, file_path: Path) -> Dict:
        """扫描单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()
            tree = ast.parse(source)
        except SyntaxError:
            return {
                'file': str(file_path),
                'error': 'SyntaxError',
                'malicious': False,
                'risk_score': 0
            }
        
        risk_score = 0
        findings = []
        
        # 1. 检测危险导入
        imports = self._check_imports(tree)
        risk_score += imports['score']
        findings.extend(imports['findings'])
        
        # 2. 检测危险函数调用
        calls = self._check_calls(tree)
        risk_score += calls['score']
        findings.extend(calls['findings'])
        
        # 3. 检测字符串混淆
        strings = self._check_strings(tree)
        risk_score += strings['score']
        findings.extend(strings['findings'])
        
        # 4. 检测异常处理隐藏
        exceptions = self._check_exceptions(tree)
        risk_score += exceptions['score']
        findings.extend(exceptions['findings'])
        
        # 5. 检测加密相关
        crypto = self._check_crypto(tree)
        risk_score += crypto['score']
        findings.extend(crypto['findings'])
        
        # 综合判断 (阈值 55)
        malicious = risk_score >= 55
        
        return {
            'file': str(file_path),
            'risk_score': min(100, risk_score),
            'malicious': malicious,
            'findings': findings,
            'scanned_at': datetime.now().isoformat()
        }
    
    def _check_imports(self, tree: ast.AST) -> Dict:
        """检测危险导入"""
        score = 0
        findings = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in DANGEROUS_MODULES:
                        pts = DANGEROUS_MODULES[alias.name]
                        score += pts
                        findings.append({
                            'type': 'dangerous_import',
                            'module': alias.name,
                            'line': node.lineno,
                            'score': pts
                        })
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module in DANGEROUS_MODULES:
                    pts = DANGEROUS_MODULES[node.module]
                    score += pts
                    findings.append({
                        'type': 'dangerous_import',
                        'module': node.module,
                        'line': node.lineno,
                        'score': pts
                    })
        
        return {'score': score, 'findings': findings}
    
    def _check_calls(self, tree: ast.AST) -> Dict:
        """检测危险函数调用"""
        score = 0
        findings = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in DANGEROUS_FUNCS:
                        pts = DANGEROUS_FUNCS[func_name]
                        score += pts
                        findings.append({
                            'type': 'dangerous_call',
                            'function': func_name,
                            'line': node.lineno,
                            'score': pts
                        })
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['decode', 'b64decode', 'loads']:
                        score += 20
                        findings.append({
                            'type': 'suspicious_method',
                            'method': node.func.attr,
                            'line': node.lineno,
                            'score': 20
                        })
        
        return {'score': score, 'findings': findings}
    
    def _check_strings(self, tree: ast.AST) -> Dict:
        """检测字符串混淆"""
        score = 0
        findings = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant):
                if isinstance(node.value, str):
                    # 长 base64 字符串
                    if len(node.value) > 100 and node.value.endswith('=='):
                        score += 25
                        findings.append({
                            'type': 'base64_string',
                            'line': getattr(node, 'lineno', 0),
                            'score': 25
                        })
                    # hex 编码
                    elif node.value.startswith('\\x') or '\\x' in node.value:
                        score += 20
                        findings.append({
                            'type': 'hex_encoding',
                            'line': getattr(node, 'lineno', 0),
                            'score': 20
                        })
        
        return {'score': score, 'findings': findings}
    
    def _check_exceptions(self, tree: ast.AST) -> Dict:
        """检测异常处理隐藏"""
        score = 0
        findings = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                # 空的 except 块 (隐藏错误)
                for handler in node.handlers:
                    if handler.body and len(handler.body) == 1:
                        if isinstance(handler.body[0], ast.Pass):
                            score += 15
                            findings.append({
                                'type': 'silent_exception',
                                'line': node.lineno,
                                'score': 15
                            })
        
        return {'score': score, 'findings': findings}
    
    def _check_crypto(self, tree: ast.AST) -> Dict:
        """检测加密相关"""
        score = 0
        findings = []
        
        crypto_modules = {'cryptography', 'pycrypto', 'Cryptodome', 'hashlib'}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(c in alias.name for c in crypto_modules):
                        score += 10
                        findings.append({
                            'type': 'crypto_import',
                            'module': alias.name,
                            'line': node.lineno,
                            'score': 10
                        })
        
        return {'score': score, 'findings': findings}
    
    def scan_directory(self, dir_path: Path) -> List[Dict]:
        """扫描目录"""
        results = []
        py_files = list(dir_path.rglob('*.py'))
        
        for i, py_file in enumerate(py_files, 1):
            result = self.scan_file(py_file)
            results.append(result)
            
            if i % 50 == 0:
                print(f"  已扫描 {i}/{len(py_files)}")
        
        return results

def main():
    import sys
    
    print("=" * 60)
    print("Round 16 v2: AST 检测引擎 (优化版)")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("用法：python3 ast_engine_v2.py <文件/目录>")
        sys.exit(1)
    
    target = Path(sys.argv[1])
    
    if not target.exists():
        print(f"❌ 目标不存在：{target}")
        sys.exit(1)
    
    scanner = OptimizedASTScanner()
    
    if target.is_file():
        result = scanner.scan_file(target)
        print(f"\n📄 文件：{result['file']}")
        print(f"🔍 风险评分：{result['risk_score']:.1f}/100")
        print(f"🎯 恶意判定：{'是' if result['malicious'] else '否'}")
        print(f"⚠️  发现：{len(result['findings'])} 个")
    else:
        print(f"\n🔍 扫描目录：{target}")
        results = scanner.scan_directory(target)
        
        malicious_count = sum(1 for r in results if r['malicious'])
        error_count = sum(1 for r in results if r.get('error'))
        
        print(f"\n📊 扫描完成:")
        print(f"  总文件：{len(results)}")
        print(f"  恶意文件：{malicious_count} ({malicious_count/len(results)*100:.1f}%)")
        print(f"  安全文件：{len(results) - malicious_count - error_count}")
        print(f"  解析错误：{error_count}")
        
        # 保存报告
        report_path = target.parent / 'ast_scan_v2_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 报告：{report_path}")

if __name__ == '__main__':
    main()
