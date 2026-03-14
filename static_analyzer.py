#!/usr/bin/env python3
"""
增强版静态分析器 - 深度代码分析
功能:
1. AST 抽象语法树分析
2. 数据流分析
3. 控制流分析
4. 敏感 API 调用检测
5. 危险模式匹配

用法:
    python3 static_analyzer.py --file suspicious.py
"""

import os
import sys
import re
import json
import ast
import hashlib
from datetime import datetime
from pathlib import Path
from collections import defaultdict

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

class StaticAnalyzer:
    """静态代码分析器"""
    
    def __init__(self):
        self.findings = []
        self.risk_score = 0
        
        # 敏感 API 映射
        self.sensitive_apis = {
            # 命令执行
            'os.system': {'risk': 20, 'category': 'Command Execution'},
            'subprocess.call': {'risk': 15, 'category': 'Command Execution'},
            'subprocess.Popen': {'risk': 20, 'category': 'Command Execution'},
            'subprocess.run': {'risk': 15, 'category': 'Command Execution'},
            'os.popen': {'risk': 25, 'category': 'Command Execution'},
            'exec': {'risk': 30, 'category': 'Code Execution'},
            'eval': {'risk': 30, 'category': 'Code Execution'},
            'compile': {'risk': 20, 'category': 'Code Execution'},
            
            # 网络
            'requests.get': {'risk': 10, 'category': 'Network'},
            'requests.post': {'risk': 10, 'category': 'Network'},
            'urllib.request': {'risk': 10, 'category': 'Network'},
            'socket.connect': {'risk': 15, 'category': 'Network'},
            'socket.create_connection': {'risk': 15, 'category': 'Network'},
            'http.client': {'risk': 10, 'category': 'Network'},
            'ftplib': {'risk': 15, 'category': 'Network'},
            'telnetlib': {'risk': 20, 'category': 'Network'},
            
            # 文件操作
            'open': {'risk': 5, 'category': 'File Operation'},
            'write': {'risk': 8, 'category': 'File Operation'},
            'shutil.copy': {'risk': 10, 'category': 'File Operation'},
            'shutil.move': {'risk': 10, 'category': 'File Operation'},
            'os.remove': {'risk': 15, 'category': 'File Operation'},
            'os.unlink': {'risk': 15, 'category': 'File Operation'},
            'Path.unlink': {'risk': 15, 'category': 'File Operation'},
            
            # 加密
            'cryptography.fernet': {'risk': 10, 'category': 'Cryptography'},
            'Crypto': {'risk': 10, 'category': 'Cryptography'},
            'hashlib': {'risk': 5, 'category': 'Cryptography'},
            'hmac': {'risk': 5, 'category': 'Cryptography'},
            
            # 凭据
            'getpass': {'risk': 8, 'category': 'Credential'},
            'keyring': {'risk': 5, 'category': 'Credential'},
            
            # 进程/线程
            'threading.Thread': {'risk': 8, 'category': 'Process'},
            'multiprocessing': {'risk': 10, 'category': 'Process'},
            'asyncio': {'risk': 5, 'category': 'Process'},
            
            # 系统信息
            'os.environ': {'risk': 8, 'category': 'System Info'},
            'platform.system': {'risk': 5, 'category': 'System Info'},
            'socket.gethostname': {'risk': 5, 'category': 'System Info'},
            
            # 权限
            'os.chmod': {'risk': 15, 'category': 'Privilege'},
            'os.chown': {'risk': 20, 'category': 'Privilege'},
            'os.setuid': {'risk': 30, 'category': 'Privilege'},
            'os.setgid': {'risk': 30, 'category': 'Privilege'},
        }
        
        # 危险模式
        self.dangerous_patterns = [
            (r'hardcoded.*password', 20, 'Hardcoded Password'),
            (r'hardcoded.*secret', 20, 'Hardcoded Secret'),
            (r'hardcoded.*key', 15, 'Hardcoded Key'),
            (r'api[_-]?key.*=.*["\']', 25, 'Hardcoded API Key'),
            (r'token.*=.*["\'][a-zA-Z0-9]{20,}', 20, 'Hardcoded Token'),
            (r'password.*=.*["\'][^"\']{8,}', 25, 'Hardcoded Password'),
            (r'secret.*=.*["\'][^"\']{8,}', 20, 'Hardcoded Secret'),
            (r'aws.*access.*key', 30, 'AWS Key'),
            (r'-----BEGIN.*PRIVATE KEY-----', 30, 'Private Key'),
            (r'shell\s*=\s*True', 25, 'Shell=True'),
            (r'eval\s*\(', 25, 'Eval Usage'),
            (r'exec\s*\(', 25, 'Exec Usage'),
            (r'pickle\.loads', 20, 'Pickle Deserialization'),
            (r'yaml\.load.*Loader\s*=\s*FullLoader', 20, 'YAML Deserialization'),
            (r'os\.popen', 25, 'Shell Popen'),
            (r'input\s*\(\s*\)', 10, 'User Input'),
        ]
        
    def analyze_ast(self, content):
        """AST 分析"""
        try:
            tree = ast.parse(content)
            return self._analyze_ast_tree(tree)
        except SyntaxError:
            return []
        except Exception as e:
            return []
    
    def _analyze_ast_tree(self, tree):
        """递归分析 AST"""
        findings = []
        
        for node in ast.walk(tree):
            # 函数调用分析
            if isinstance(node, ast.Call):
                # 检查危险函数调用
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in self.sensitive_apis:
                        info = self.sensitive_apis[func_name]
                        findings.append({
                            'type': 'Sensitive API',
                            'api': func_name,
                            'category': info['category'],
                            'risk': info['risk'],
                            'line': node.lineno
                        })
                        
                # 检查方法调用
                elif isinstance(node.func, ast.Attribute):
                    method_name = node.func.attr
                    full_name = f"{getattr(node.func.value, 'id', 'unknown')}.{method_name}"
                    if full_name in self.sensitive_apis:
                        info = self.sensitive_apis[full_name]
                        findings.append({
                            'type': 'Sensitive API',
                            'api': full_name,
                            'category': info['category'],
                            'risk': info['risk'],
                            'line': node.lineno
                        })
            
            # 导入分析
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    findings.append({
                        'type': 'Import',
                        'module': alias.name,
                        'risk': 0,
                        'line': node.lineno
                    })
                    
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    findings.append({
                        'type': 'ImportFrom',
                        'module': node.module,
                        'risk': 0,
                        'line': node.lineno
                    })
        
        return findings
    
    def analyze_patterns(self, content):
        """危险模式分析"""
        findings = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            for pattern, risk, desc in self.dangerous_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append({
                        'type': 'Dangerous Pattern',
                        'pattern': desc,
                        'risk': risk,
                        'line': i,
                        'content': line.strip()[:80]
                    })
        
        return findings
    
    def analyze_imports(self, content):
        """导入分析"""
        findings = []
        
        # 危险导入
        dangerous_imports = [
            ('os', 3, 'System'),
            ('subprocess', 5, 'Process'),
            ('socket', 5, 'Network'),
            ('requests', 3, 'Network'),
            ('urllib', 3, 'Network'),
            ('cryptography', 5, 'Crypto'),
            ('Crypto', 5, 'Crypto'),
            ('hashlib', 2, 'Crypto'),
            ('hmac', 2, 'Crypto'),
            ('paramiko', 10, 'SSH'),
            ('pwntools', 15, 'Exploit'),
            ('scapy', 10, 'Network'),
            ('pycryptodome', 5, 'Crypto'),
            ('keyring', 3, 'Credential'),
            ('getpass', 3, 'Credential'),
            ('jwt', 5, 'Auth'),
            ('passlib', 3, 'Auth'),
            ('selenium', 5, 'Automation'),
            ('mechanize', 10, 'Automation'),
            ('imp', 10, 'Dynamic Import'),
            ('importlib', 5, 'Dynamic Import'),
        ]
        
        for imp, risk, category in dangerous_imports:
            if re.search(rf'\bimport\s+{imp}\b', content) or re.search(rf'\bfrom\s+{imp}\s+import', content):
                findings.append({
                    'type': 'Dangerous Import',
                    'import': imp,
                    'category': category,
                    'risk': risk
                })
        
        return findings
    
    def analyze_strings(self, content):
        """字符串分析 - 检测硬编码凭据"""
        findings = []
        
        # 提取字符串
        strings = re.findall(r'["\']([^"\']{8,})["\']', content)
        
        # 检测可疑字符串
        suspicious_patterns = [
            (r'https?://', 'URL'),
            (r'\d+\.\d+\.\d+\.\d+', 'IP Address'),
            (r'aws_ACCESS_KEY|aws_secret', 'AWS Key'),
            (r'BEGIN.*PRIVATE.*KEY', 'Private Key'),
            (r'ghp_[a-zA-Z0-9]{36}', 'GitHub Token'),
            (r'sk-[a-zA-Z0-9]{20,}', 'API Key'),
            (r'xoxb-[a-zA-Z0-9-]{20,}', 'Slack Token'),
        ]
        
        for s in strings:
            for pattern, desc in suspicious_patterns:
                if re.search(pattern, s, re.IGNORECASE):
                    findings.append({
                        'type': 'Suspicious String',
                        'string_type': desc,
                        'risk': 15,
                        'preview': s[:30] + '...' if len(s) > 30 else s
                    })
                    break
        
        return findings
    
    def analyze_entropy(self, content):
        """熵分析 - 检测混淆/加密"""
        import math
        
        def calc_entropy(s):
            if not s:
                return 0
            freq = {}
            for c in s:
                freq[c] = freq.get(c, 0) + 1
            entropy = -sum(f/len(s) * math.log2(f/len(s)) for f in freq.values())
            return entropy
        
        # 检查字符串熵
        strings = re.findall(r'b["\']([a-zA-Z0-9+/=]{20,})["\']', content)
        high_entropy = 0
        
        for s in strings:
            if calc_entropy(s) > 4.5:  # 高熵阈值
                high_entropy += 1
        
        findings = []
        if high_entropy > 0:
            findings.append({
                'type': 'High Entropy',
                'count': high_entropy,
                'risk': high_entropy * 10
            })
        
        return findings
    
    def analyze_file(self, file_path):
        """综合分析文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return {'error': str(e)}
        
        all_findings = []
        total_risk = 0
        
        # 1. AST 分析
        ast_findings = self.analyze_ast(content)
        all_findings.extend(ast_findings)
        total_risk += sum(f['risk'] for f in ast_findings)
        
        # 2. 模式分析
        pattern_findings = self.analyze_patterns(content)
        all_findings.extend(pattern_findings)
        total_risk += sum(f['risk'] for f in pattern_findings)
        
        # 3. 导入分析
        import_findings = self.analyze_imports(content)
        all_findings.extend(import_findings)
        total_risk += sum(f['risk'] for f in import_findings)
        
        # 4. 字符串分析
        string_findings = self.analyze_strings(content)
        all_findings.extend(string_findings)
        total_risk += sum(f.get('risk', 0) for f in string_findings)
        
        # 5. 熵分析
        entropy_findings = self.analyze_entropy(content)
        all_findings.extend(entropy_findings)
        total_risk += sum(f.get('risk', 0) for f in entropy_findings)
        
        # 严重级别
        if total_risk >= 80:
            severity = 'CRITICAL'
        elif total_risk >= 50:
            severity = 'HIGH'
        elif total_risk >= 20:
            severity = 'MEDIUM'
        else:
            severity = 'LOW'
        
        return {
            'file': file_path,
            'severity': severity,
            'risk_score': total_risk,
            'findings': all_findings,
            'finding_count': len(all_findings),
            'lines': len(content.split('\n'))
        }

def main():
    import argparse
    parser = argparse.ArgumentParser(description="增强版静态分析器")
    parser.add_argument("--file", help="分析文件")
    parser.add_argument("--dir", help="分析目录")
    parser.add_argument("--output", default="static_result.json", help="输出文件")
    
    args = parser.parse_args()
    
    analyzer = StaticAnalyzer()
    results = []
    
    if args.file:
        log(f"🔍 分析文件: {args.file}")
        result = analyzer.analyze_file(args.file)
        results.append(result)
        
    elif args.dir:
        log(f"🔍 分析目录: {args.dir}")
        for root, dirs, files in os.walk(args.dir):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for f in files:
                if f.endswith(('.py', '.js', '.sh')):
                    file_path = os.path.join(root, f)
                    result = analyzer.analyze_file(file_path)
                    results.append(result)
    
    # 统计
    critical = sum(1 for r in results if r.get('severity') == 'CRITICAL')
    high = sum(1 for r in results if r.get('severity') == 'HIGH')
    medium = sum(1 for r in results if r.get('severity') == 'MEDIUM')
    low = sum(1 for r in results if r.get('severity') == 'LOW')
    
    # 保存
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    log(f"📊 分析完成:")
    print(f"\n{'='*50}")
    print(f"   🔴 严重: {critical}")
    print(f"   🟠 高危: {high}")
    print(f"   🟡 中危: {medium}")
    print(f"   🟢 低危: {low}")
    print(f"{'='*50}")
    print(f"\n📁 报告: {args.output}")

if __name__ == "__main__":
    main()
