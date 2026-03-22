#!/usr/bin/env python3
"""
Round 12 - 质量检查器

检查代码质量、测试覆盖、文档完整性
"""

import os
import sys
import json
import ast
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# ============== 配置 ==============

BASE_DIR = Path(__file__).parent.parent
ROUND12_DIR = BASE_DIR / "round12"

# ============== 代码质量检查 ==============

class CodeQualityChecker:
    """代码质量检查器"""
    
    def __init__(self, target_dir: Path):
        self.target_dir = target_dir
        self.issues = []
        self.stats = {
            'total_files': 0,
            'total_lines': 0,
            'total_functions': 0,
            'total_classes': 0,
            'docstring_coverage': 0.0,
        }
    
    def check_all(self) -> Dict:
        """执行所有检查"""
        print("=" * 60)
        print("🔍 Round 12 - 代码质量检查")
        print("=" * 60)
        
        # 扫描 Python 文件
        py_files = list(self.target_dir.glob("*.py"))
        self.stats['total_files'] = len(py_files)
        
        print(f"\n📁 发现 {len(py_files)} 个 Python 文件")
        
        # 逐个检查
        for py_file in py_files:
            self._check_file(py_file)
        
        # 计算文档覆盖率
        self._calculate_docstring_coverage()
        
        # 打印摘要
        self._print_summary()
        
        return {
            'stats': self.stats,
            'issues': self.issues,
            'timestamp': datetime.now().isoformat(),
        }
    
    def _check_file(self, file_path: Path):
        """检查单个文件"""
        print(f"\n  检查：{file_path.name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            self.stats['total_lines'] += len(lines)
            
            # AST 分析
            tree = ast.parse(content)
            
            # 统计函数和类
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            
            self.stats['total_functions'] += len(functions)
            self.stats['total_classes'] += len(classes)
            
            # 检查文档字符串
            for func in functions:
                if not ast.get_docstring(func):
                    self.issues.append({
                        'file': file_path.name,
                        'type': 'missing_docstring',
                        'location': f"function '{func.name}'",
                        'severity': 'low',
                    })
            
            for cls in classes:
                if not ast.get_docstring(cls):
                    self.issues.append({
                        'file': file_path.name,
                        'type': 'missing_docstring',
                        'location': f"class '{cls.name}'",
                        'severity': 'low',
                    })
            
            # 检查函数长度
            for func in functions:
                func_lines = func.end_lineno - func.lineno if hasattr(func, 'end_lineno') else 0
                if func_lines > 50:
                    self.issues.append({
                        'file': file_path.name,
                        'type': 'long_function',
                        'location': f"function '{func.name}' ({func_lines} lines)",
                        'severity': 'medium',
                    })
            
            # 检查 import
            imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
            if len(imports) > 20:
                self.issues.append({
                    'file': file_path.name,
                    'type': 'too_many_imports',
                    'location': f"{len(imports)} imports",
                    'severity': 'low',
                })
            
            print(f"    ✅ {len(lines)} 行，{len(functions)} 函数，{len(classes)} 类")
        
        except Exception as e:
            self.issues.append({
                'file': file_path.name,
                'type': 'parse_error',
                'location': str(e),
                'severity': 'high',
            })
            print(f"    ❌ 解析错误：{e}")
    
    def _calculate_docstring_coverage(self):
        """计算文档字符串覆盖率"""
        total_items = self.stats['total_functions'] + self.stats['total_classes']
        missing_docs = len([i for i in self.issues if i['type'] == 'missing_docstring'])
        
        if total_items > 0:
            self.stats['docstring_coverage'] = (total_items - missing_docs) / total_items * 100
    
    def _print_summary(self):
        """打印摘要"""
        print("\n" + "=" * 60)
        print("📊 代码质量摘要")
        print("=" * 60)
        
        print(f"\n基础统计:")
        print(f"  文件数：{self.stats['total_files']}")
        print(f"  总行数：{self.stats['total_lines']}")
        print(f"  函数数：{self.stats['total_functions']}")
        print(f"  类数：{self.stats['total_classes']}")
        print(f"  文档覆盖率：{self.stats['docstring_coverage']:.1f}%")
        
        print(f"\n问题统计:")
        by_severity = {}
        for issue in self.issues:
            severity = issue['severity']
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        for severity in ['high', 'medium', 'low']:
            count = by_severity.get(severity, 0)
            icon = "❌" if severity == 'high' else "⚠️" if severity == 'medium' else "ℹ️"
            print(f"  {icon} {severity}: {count}")
        
        if self.issues:
            print(f"\n详细问题 (前 10 条):")
            for issue in self.issues[:10]:
                print(f"  [{issue['severity']}] {issue['file']}: {issue['type']} @ {issue['location']}")

# ============== 功能完整性检查 ==============

class FeatureCompletenessChecker:
    """功能完整性检查器"""
    
    def __init__(self, round12_dir: Path):
        self.round12_dir = round12_dir
        self.required_files = [
            'database.py',
            'file_watcher.py',
            'alert_notifier.py',
            'rule_manager.py',
            'dashboard/main.py',
        ]
        self.required_features = [
            ('数据库初始化', 'database.py', 'init_database'),
            ('文件监控', 'file_watcher.py', 'FileWatcher'),
            ('告警通知', 'alert_notifier.py', 'AlertNotifier'),
            ('规则热更新', 'rule_manager.py', 'RuleManager'),
            ('Web 仪表板', 'dashboard/main.py', 'app'),
        ]
    
    def check(self) -> Dict:
        """检查功能完整性"""
        print("\n" + "=" * 60)
        print("✅ 功能完整性检查")
        print("=" * 60)
        
        results = {
            'files': {},
            'features': {},
            'completeness': 0.0,
        }
        
        # 检查文件存在性
        print("\n📁 文件检查:")
        for file in self.required_files:
            file_path = self.round12_dir / file
            exists = file_path.exists()
            results['files'][file] = exists
            icon = "✅" if exists else "❌"
            print(f"  {icon} {file}")
        
        # 检查功能实现
        print("\n🔧 功能检查:")
        completed = 0
        for feature_name, file_path, symbol in self.required_features:
            full_path = self.round12_dir / file_path
            if full_path.exists():
                with open(full_path) as f:
                    content = f.read()
                has_symbol = symbol in content
                results['features'][feature_name] = has_symbol
                icon = "✅" if has_symbol else "❌"
                print(f"  {icon} {feature_name}")
                if has_symbol:
                    completed += 1
            else:
                results['features'][feature_name] = False
                print(f"  ❌ {feature_name} (文件不存在)")
        
        results['completeness'] = completed / len(self.required_features) * 100
        
        print(f"\n📊 完成度：{results['completeness']:.1f}% ({completed}/{len(self.required_features)})")
        
        return results

# ============== 测试覆盖检查 ==============

class TestCoverageChecker:
    """测试覆盖检查器"""
    
    def __init__(self, round12_dir: Path):
        self.round12_dir = round12_dir
    
    def check(self) -> Dict:
        """检查测试覆盖"""
        print("\n" + "=" * 60)
        print("🧪 测试覆盖检查")
        print("=" * 60)
        
        results = {
            'has_unit_tests': False,
            'has_integration_tests': False,
            'test_files': [],
            'coverage_estimate': 0.0,
        }
        
        # 查找测试文件
        test_files = list(self.round12_dir.glob("test_*.py")) + list(self.round12_dir.glob("*_test.py"))
        results['test_files'] = [f.name for f in test_files]
        results['has_unit_tests'] = len(test_files) > 0
        
        print(f"\n📁 测试文件:")
        if test_files:
            for f in test_files:
                print(f"  ✅ {f.name}")
        else:
            print(f"  ❌ 无测试文件")
        
        # 检查 __main__ 测试
        py_files = list(self.round12_dir.glob("*.py"))
        files_with_main = 0
        for py_file in py_files:
            with open(py_file) as f:
                content = f.read()
            if 'if __name__ == "__main__"' in content:
                files_with_main += 1
        
        print(f"\n📊 自测覆盖：{files_with_main}/{len(py_files)} 文件")
        results['coverage_estimate'] = files_with_main / len(py_files) * 100 if py_files else 0
        
        return results

# ============== 主函数 ==============

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Round 12 质量检查")
    parser.add_argument('--all', action='store_true', help='执行所有检查')
    parser.add_argument('--code', action='store_true', help='代码质量检查')
    parser.add_argument('--features', action='store_true', help='功能完整性检查')
    parser.add_argument('--tests', action='store_true', help='测试覆盖检查')
    parser.add_argument('--output', '-o', type=str, help='输出报告文件')
    
    args = parser.parse_args()
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'round': '12',
    }
    
    if args.all or args.code:
        code_checker = CodeQualityChecker(ROUND12_DIR)
        results['code_quality'] = code_checker.check_all()
    
    if args.all or args.features:
        feature_checker = FeatureCompletenessChecker(ROUND12_DIR)
        results['feature_completeness'] = feature_checker.check()
    
    if args.all or args.tests:
        test_checker = TestCoverageChecker(ROUND12_DIR)
        results['test_coverage'] = test_checker.check()
    
    # 保存报告
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 报告已保存：{output_path}")
    
    # 总体评估
    print("\n" + "=" * 60)
    print("📋 总体评估")
    print("=" * 60)
    
    if 'code_quality' in results:
        code_stats = results['code_quality']['stats']
        code_issues = len(results['code_quality']['issues'])
        print(f"\n代码质量:")
        print(f"  文档覆盖率：{code_stats['docstring_coverage']:.1f}%")
        print(f"  问题数：{code_issues}")
    
    if 'feature_completeness' in results:
        print(f"\n功能完成度：{results['feature_completeness']['completeness']:.1f}%")
    
    if 'test_coverage' in results:
        print(f"\n测试覆盖：{results['test_coverage']['coverage_estimate']:.1f}%")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
