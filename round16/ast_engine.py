#!/usr/bin/env python3
"""
Round 16: AST 检测引擎

功能:
1. AST 解析
2. 混淆检测
3. 行为分析
4. 相似度检测
"""

import ast
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class ASTParser:
    """AST 解析器"""
    
    def __init__(self):
        self.tree = None
        self.source = ""
    
    def parse(self, source_code: str) -> ast.AST:
        """解析 Python 代码"""
        self.source = source_code
        self.tree = ast.parse(source_code)
        return self.tree
    
    def get_all_nodes(self, node_type: type) -> List[ast.AST]:
        """获取所有指定类型的节点"""
        nodes = []
        for node in ast.walk(self.tree):
            if isinstance(node, node_type):
                nodes.append(node)
        return nodes
    
    def get_ast_hash(self) -> str:
        """生成 AST 指纹"""
        ast_str = ast.dump(self.tree)
        return hashlib.md5(ast_str.encode()).hexdigest()

class ObfuscationDetector:
    """混淆代码检测器"""
    
    def __init__(self):
        self.findings = []
    
    def detect(self, tree: ast.AST, source: str) -> Dict:
        """检测混淆特征"""
        self.findings = []
        
        # 检测 base64 解码
        self._check_base64(tree)
        
        # 检测 eval/exec
        self._check_dynamic_exec(tree)
        
        # 检测动态导入
        self._check_dynamic_import(tree)
        
        # 检测编码混淆
        self._check_encoding(tree)
        
        return {
            'obfuscation_detected': len(self.findings) > 0,
            'confidence': min(1.0, len(self.findings) * 0.25),
            'findings': self.findings
        }
    
    def _check_base64(self, tree: ast.AST):
        """检测 base64 解码"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['decode', 'b64decode']:
                        self.findings.append({
                            'type': 'base64_decode',
                            'line': node.lineno,
                            'severity': 'high'
                        })
    
    def _check_dynamic_exec(self, tree: ast.AST):
        """检测动态执行"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec', 'compile']:
                        self.findings.append({
                            'type': 'dynamic_exec',
                            'line': node.lineno,
                            'severity': 'critical'
                        })
    
    def _check_dynamic_import(self, tree: ast.AST):
        """检测动态导入"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id == '__import__':
                        self.findings.append({
                            'type': 'dynamic_import',
                            'line': node.lineno,
                            'severity': 'high'
                        })
    
    def _check_encoding(self, tree: ast.AST):
        """检测编码混淆"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant):
                if isinstance(node.value, str):
                    # 检测 hex/unicode 编码
                    if node.value.startswith('\\x') or node.value.startswith('\\u'):
                        self.findings.append({
                            'type': 'encoding_obfuscation',
                            'line': getattr(node, 'lineno', 0),
                            'severity': 'medium'
                        })

class BehaviorAnalyzer:
    """行为分析器"""
    
    def __init__(self):
        self.behaviors = []
    
    def analyze(self, tree: ast.AST) -> Dict:
        """分析代码行为"""
        self.behaviors = []
        
        # 文件系统操作
        self._check_filesystem(tree)
        
        # 网络操作
        self._check_network(tree)
        
        # 系统调用
        self._check_system(tree)
        
        # 环境变量
        self._check_environment(tree)
        
        return {
            'behaviors': self.behaviors,
            'risk_score': len(self.behaviors) * 10
        }
    
    def _check_filesystem(self, tree: ast.AST):
        """检测文件系统操作"""
        dangerous_funcs = ['open', 'write', 'read', 'mkdir', 'remove', 'copy']
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in dangerous_funcs:
                        self.behaviors.append({
                            'category': 'filesystem',
                            'action': node.func.id,
                            'line': node.lineno,
                            'risk': 'medium'
                        })
    
    def _check_network(self, tree: ast.AST):
        """检测网络操作"""
        network_modules = ['requests', 'urllib', 'socket', 'http']
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(m in alias.name for m in network_modules):
                        self.behaviors.append({
                            'category': 'network',
                            'action': f'import {alias.name}',
                            'line': node.lineno,
                            'risk': 'medium'
                        })
    
    def _check_system(self, tree: ast.AST):
        """检测系统调用"""
        system_modules = ['os', 'subprocess', 'sys', 'platform']
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(m in alias.name for m in system_modules):
                        self.behaviors.append({
                            'category': 'system',
                            'action': f'import {alias.name}',
                            'line': node.lineno,
                            'risk': 'low'
                        })
    
    def _check_environment(self, tree: ast.AST):
        """检测环境变量访问"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Subscript):
                if isinstance(node.value, ast.Subscript):
                    if hasattr(node.value, 'attr') and node.value.attr == 'environ':
                        self.behaviors.append({
                            'category': 'environment',
                            'action': 'access_env',
                            'line': node.lineno,
                            'risk': 'high'
                        })

class SimilarityDetector:
    """相似度检测器"""
    
    def __init__(self):
        self.signatures = {}
    
    def generate_signature(self, tree: ast.AST) -> Dict:
        """生成代码签名"""
        signature = {
            'ast_hash': hashlib.md5(ast.dump(tree).encode()).hexdigest(),
            'node_counts': {},
            'function_names': [],
            'import_names': []
        }
        
        # 统计节点类型
        for node in ast.walk(tree):
            node_type = type(node).__name__
            signature['node_counts'][node_type] = signature['node_counts'].get(node_type, 0) + 1
        
        # 收集函数名
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                signature['function_names'].append(node.name)
        
        # 收集导入
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    signature['import_names'].append(alias.name)
        
        return signature
    
    def compare(self, sig1: Dict, sig2: Dict) -> float:
        """比较两个签名相似度"""
        # 简单实现：基于节点计数相似度
        nodes1 = set(sig1['node_counts'].keys())
        nodes2 = set(sig2['node_counts'].keys())
        
        intersection = len(nodes1 & nodes2)
        union = len(nodes1 | nodes2)
        
        return intersection / union if union > 0 else 0

class ASTScanner:
    """AST 统一扫描器"""
    
    def __init__(self):
        self.parser = ASTParser()
        self.obfuscation_detector = ObfuscationDetector()
        self.behavior_analyzer = BehaviorAnalyzer()
        self.similarity_detector = SimilarityDetector()
    
    def scan_file(self, file_path: Path) -> Dict:
        """扫描单个文件"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            source = f.read()
        
        try:
            tree = self.parser.parse(source)
        except SyntaxError:
            return {
                'file': str(file_path),
                'error': 'SyntaxError',
                'malicious': False
            }
        
        obfuscation = self.obfuscation_detector.detect(tree, source)
        behavior = self.behavior_analyzer.analyze(tree)
        signature = self.similarity_detector.generate_signature(tree)
        
        # 综合判断
        risk_score = (
            obfuscation['confidence'] * 40 +
            min(1.0, behavior['risk_score'] / 100) * 40 +
            len(obfuscation['findings']) * 5
        )
        
        return {
            'file': str(file_path),
            'ast_hash': signature['ast_hash'],
            'obfuscation': obfuscation,
            'behaviors': behavior['behaviors'],
            'risk_score': min(100, risk_score),
            'malicious': risk_score >= 50,
            'scanned_at': datetime.now().isoformat()
        }
    
    def scan_directory(self, dir_path: Path) -> List[Dict]:
        """扫描目录"""
        results = []
        
        for py_file in dir_path.rglob('*.py'):
            result = self.scan_file(py_file)
            results.append(result)
        
        return results

def main():
    """主函数"""
    import sys
    
    print("=" * 60)
    print("Round 16: AST 检测引擎")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("用法：python3 ast_engine.py <文件/目录>")
        sys.exit(1)
    
    target = Path(sys.argv[1])
    
    if not target.exists():
        print(f"❌ 目标不存在：{target}")
        sys.exit(1)
    
    scanner = ASTScanner()
    
    if target.is_file():
        result = scanner.scan_file(target)
        print(f"\n📄 文件：{result['file']}")
        print(f"🔍 风险评分：{result['risk_score']:.1f}/100")
        print(f"⚠️  混淆检测：{'是' if result['obfuscation']['obfuscation_detected'] else '否'}")
        print(f"🎯 恶意判定：{'是' if result['malicious'] else '否'}")
    else:
        results = scanner.scan_directory(target)
        
        malicious_count = sum(1 for r in results if r['malicious'])
        
        print(f"\n📊 扫描完成:")
        print(f"  总文件：{len(results)}")
        print(f"  恶意文件：{malicious_count}")
        print(f"  安全文件：{len(results) - malicious_count}")
        
        # 保存报告
        report_path = target.parent / 'ast_scan_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 报告：{report_path}")

if __name__ == '__main__':
    main()
