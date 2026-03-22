#!/usr/bin/env python3
"""
Round 16 - AST 检测引擎

分析代码抽象语法树，检测混淆和变异代码
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent
SAMPLES_DIR = BASE_DIR / "samples"
RULES_DIR = BASE_DIR / "rules" / "optimized"

class ASTAnalyzer:
    """AST 分析器"""
    
    def __init__(self):
        self.suspicious_patterns = []
    
    def analyze_file(self, file_path: Path) -> Dict:
        """分析单个文件"""
        with open(file_path) as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {'error': 'SyntaxError', 'content_length': len(content)}
        
        analysis = {
            'file': str(file_path),
            'content_length': len(content),
            'ast_metrics': self._extract_metrics(tree),
            'suspicious_nodes': [],
            'obfuscation_score': 0,
        }
        
        # 遍历 AST
        for node in ast.walk(tree):
            self._analyze_node(node, analysis)
        
        # 计算混淆分数
        analysis['obfuscation_score'] = self._calculate_obfuscation_score(analysis)
        
        return analysis
    
    def _extract_metrics(self, tree: ast.AST) -> Dict:
        """提取 AST 度量"""
        metrics = {
            'total_nodes': 0,
            'function_defs': 0,
            'class_defs': 0,
            'imports': 0,
            'calls': 0,
            'strings': 0,
            'numbers': 0,
            'max_depth': 0,
        }
        
        depth = 0
        for node in ast.walk(tree):
            metrics['total_nodes'] += 1
            
            if isinstance(node, ast.FunctionDef):
                metrics['function_defs'] += 1
            elif isinstance(node, ast.ClassDef):
                metrics['class_defs'] += 1
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                metrics['imports'] += 1
            elif isinstance(node, ast.Call):
                metrics['calls'] += 1
            elif isinstance(node, ast.Constant):
                if isinstance(node.value, str):
                    metrics['strings'] += 1
                elif isinstance(node.value, (int, float)):
                    metrics['numbers'] += 1
        
        return metrics
    
    def _analyze_node(self, node: ast.AST, analysis: Dict):
        """分析节点"""
        suspicious = []
        
        # 检测可疑调用
        if isinstance(node, ast.Call):
            suspicious.extend(self._check_call(node))
        
        # 检测可疑字符串
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            suspicious.extend(self._check_string(node.value))
        
        # 检测动态执行
        if isinstance(node, ast.Expr):
            suspicious.extend(self._check_dynamic_exec(node))
        
        if suspicious:
            analysis['suspicious_nodes'].append({
                'node_type': type(node).__name__,
                'line': node.lineno if hasattr(node, 'lineno') else 0,
                'issues': suspicious,
            })
    
    def _check_call(self, node: ast.Call) -> List[str]:
        """检查可疑调用"""
        issues = []
        
        # 检测 eval/exec
        if isinstance(node.func, ast.Name):
            if node.func.id in ['eval', 'exec', 'compile']:
                issues.append(f'dangerous_func:{node.func.id}')
        
        # 检测 subprocess
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ['system', 'popen', 'call', 'run']:
                issues.append(f'dangerous_method:{node.func.attr}')
        
        return issues
    
    def _check_string(self, value: str) -> List[str]:
        """检查可疑字符串"""
        issues = []
        
        # 检测恶意模式
        dangerous_patterns = [
            ('curl', 'curl_command'),
            ('wget', 'wget_command'),
            ('bash', 'bash_command'),
            ('/dev/tcp', 'reverse_shell'),
            ('base64', 'base64_encoding'),
        ]
        
        for pattern, label in dangerous_patterns:
            if pattern in value.lower():
                issues.append(f'suspicious_string:{label}')
        
        # 检测长随机字符串（可能是混淆）
        if len(value) > 100 and len(set(value)) < 10:
            issues.append('possible_obfuscation')
        
        return issues
    
    def _check_dynamic_exec(self, node: ast.Expr) -> List[str]:
        """检查动态执行"""
        issues = []
        
        # 检测字符串拼接后执行
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name):
                if node.value.func.id == 'exec':
                    issues.append('dynamic_exec')
        
        return issues
    
    def _calculate_obfuscation_score(self, analysis: Dict) -> float:
        """计算混淆分数"""
        score = 0.0
        
        metrics = analysis['ast_metrics']
        suspicious = analysis['suspicious_nodes']
        
        # 基于可疑节点数量
        score += len(suspicious) * 10
        
        # 基于字符串/代码比例
        if metrics['total_nodes'] > 0:
            string_ratio = metrics['strings'] / metrics['total_nodes']
            if string_ratio > 0.5:  # 字符串过多
                score += 20
        
        # 基于函数/代码比例
        if metrics['function_defs'] > 0:
            avg_func_size = metrics['total_nodes'] / metrics['function_defs']
            if avg_func_size > 50:  # 函数过大
                score += 15
        
        # 基于动态执行
        for node in suspicious:
            for issue in node.get('issues', []):
                if 'dynamic_exec' in issue or 'dangerous_func' in issue:
                    score += 30
        
        return min(score, 100)  # 0-100

class ASTRuleGenerator:
    """AST 规则生成器"""
    
    def __init__(self):
        self.analyzer = ASTAnalyzer()
    
    def generate_rules_from_samples(self, attack_type: str) -> List[Dict]:
        """从样本生成 AST 规则"""
        sample_dir = SAMPLES_DIR / "malicious" / attack_type
        
        if not sample_dir.exists():
            return []
        
        ast_signatures = []
        
        for sample_dir in sample_dir.iterdir():
            if not sample_dir.is_dir():
                continue
            
            sample_file = sample_dir / "sample.py"
            if not sample_file.exists():
                continue
            
            analysis = self.analyzer.analyze_file(sample_file)
            
            if analysis['obfuscation_score'] > 30:
                ast_signatures.append({
                    'sample_id': sample_dir.name,
                    'metrics': analysis['ast_metrics'],
                    'suspicious_nodes': analysis['suspicious_nodes'],
                    'obfuscation_score': analysis['obfuscation_score'],
                })
        
        # 生成规则
        rules = self._create_ast_rules(attack_type, ast_signatures)
        
        return rules
    
    def _create_ast_rules(self, attack_type: str, signatures: List[Dict]) -> List[Dict]:
        """创建 AST 规则"""
        rules = []
        
        # 基于共同特征生成规则
        if len(signatures) > 0:
            # 规则 1: 高混淆分数
            rules.append({
                'id': f'R16-AST-{attack_type[:3].upper()}-001',
                'name': f'[AST] {attack_type} 混淆检测',
                'metadata': {
                    'attack_type': attack_type,
                    'rule_type': 'ast_obfuscation',
                    'tier': 'L3',
                    'severity': 'high',
                    'version': '16.0',
                },
                'condition': {
                    'ast_obfuscation_score': {'min': 50},
                },
                'action': 'alert',
            })
            
            # 规则 2: 动态执行
            rules.append({
                'id': f'R16-AST-{attack_type[:3].upper()}-002',
                'name': f'[AST] {attack_type} 动态执行检测',
                'metadata': {
                    'attack_type': attack_type,
                    'rule_type': 'ast_dynamic_exec',
                    'tier': 'L3',
                    'severity': 'critical',
                    'version': '16.0',
                },
                'condition': {
                    'ast_suspicious_nodes': {
                        'contains': ['dynamic_exec', 'dangerous_func:eval', 'dangerous_func:exec'],
                    },
                },
                'action': 'alert',
            })
        
        return rules

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Round 16 AST 检测引擎')
    parser.add_argument('--sample', type=str, help='分析单个样本文件')
    parser.add_argument('--attack-type', type=str, help='攻击类型')
    parser.add_argument('--generate-rules', action='store_true', help='生成 AST 规则')
    
    args = parser.parse_args()
    
    print("="*60)
    print("🌳 Round 16 - AST 检测引擎")
    print("="*60)
    
    analyzer = ASTAnalyzer()
    
    if args.sample:
        # 分析单个文件
        file_path = Path(args.sample)
        analysis = analyzer.analyze_file(file_path)
        
        print(f"\n📄 文件：{file_path}")
        print(f"📊 AST 度量:")
        for k, v in analysis['ast_metrics'].items():
            print(f"  {k}: {v}")
        print(f"🔍 可疑节点：{len(analysis['suspicious_nodes'])}")
        print(f"🎯 混淆分数：{analysis['obfuscation_score']}/100")
        
        if analysis['suspicious_nodes']:
            print(f"\n⚠️  可疑内容:")
            for node in analysis['suspicious_nodes'][:5]:
                print(f"  行{node['line']}: {', '.join(node['issues'])}")
    
    elif args.generate_rules:
        # 生成规则
        attack_types = ['tool_poisoning', 'remote_load', 'data_exfil',
                       'prompt_injection', 'resource_exhaustion', 'memory_pollution']
        
        all_rules = []
        for attack_type in attack_types:
            print(f"\n📋 生成 [{attack_type}] AST 规则...")
            rule_gen = ASTRuleGenerator()
            rules = rule_gen.generate_rules_from_samples(attack_type)
            all_rules.extend(rules)
            print(f"  ✅ 生成 {len(rules)} 条规则")
        
        # 保存规则
        if all_rules:
            import yaml
            output_file = RULES_DIR / "L3_rules_ast_r16.yaml"
            with open(output_file, 'w') as f:
                yaml.dump({
                    'version': '16.0',
                    'tier': 'L3',
                    'rule_count': len(all_rules),
                    'rules': all_rules,
                }, f, allow_unicode=True)
            
            print(f"\n💾 规则已保存：{output_file}")
    
    else:
        # 批量分析示例
        print("\n📊 批量分析恶意样本...")
        
        malicious_dir = SAMPLES_DIR / "malicious"
        results = []
        
        for attack_dir in list(malicious_dir.iterdir())[:3]:  # 前 3 类
            if not attack_dir.is_dir():
                continue
            
            for sample_dir in list(attack_dir.iterdir())[:5]:  # 每类前 5 个
                if not sample_dir.is_dir():
                    continue
                
                sample_file = sample_dir / "sample.py"
                if sample_file.exists():
                    analysis = analyzer.analyze_file(sample_file)
                    results.append({
                        'sample': str(sample_dir),
                        'obfuscation_score': analysis['obfuscation_score'],
                    })
        
        # 显示结果
        print(f"\n分析 {len(results)} 个样本:")
        high_obfuscation = [r for r in results if r['obfuscation_score'] > 50]
        print(f"  高混淆 (>50): {len(high_obfuscation)} 个")
        
        if high_obfuscation:
            print(f"\n🔍 高混淆样本:")
            for r in high_obfuscation[:5]:
                print(f"  {r['sample']} (分数：{r['obfuscation_score']})")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    main()
