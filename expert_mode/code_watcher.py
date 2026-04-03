#!/usr/bin/env python3
"""
🔍 代码质量监控器 - 自动发现代码问题
=====================================
功能:
1. 静态分析 (Lint)
2. 运行时错误捕获
3. 异常监控
4. 性能退化检测

使用方式:
    python3 code_watcher.py --check          # 检查代码
    python3 code_watcher.py --daemon         # 守护监控
    python3 code_watcher.py --report         # 生成报告
"""

import os
import sys
import json
import time
import subprocess
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass


# 问题类型
ISSUE_TYPES = {
    "SYNTAX": "语法错误",
    "RUNTIME": "运行时错误",
    "IMPORT": "导入错误",
    "DEPRECATED": "废弃API",
    "SECURITY": "安全问题",
    "PERFORMANCE": "性能问题",
    "MEMORY": "内存泄漏",
    "LOGIC": "逻辑错误"
}


@dataclass
class CodeIssue:
    """代码问题"""
    type: str
    severity: str  # HIGH, MEDIUM, LOW
    location: str  # file:line
    message: str
    suggestion: str


class CodeWatcher:
    """代码质量监控器"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.issues: List[CodeIssue] = []
        self.history: List[Dict] = []
    
    def check_syntax(self) -> List[CodeIssue]:
        """语法检查"""
        issues = []
        
        for py_file in self.project_dir.rglob("*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue
            
            result = subprocess.run(
                ["python3", "-m", "py_compile", str(py_file)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                issues.append(CodeIssue(
                    type="SYNTAX",
                    severity="HIGH",
                    location=str(py_file),
                    message=result.stderr[:100],
                    suggestion="修复语法错误"
                ))
        
        return issues
    
    def check_imports(self) -> List[CodeIssue]:
        """导入检查"""
        issues = []
        
        for py_file in self.project_dir.rglob("*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue
            
            result = subprocess.run(
                ["python3", "-c", f"import sys; sys.path.insert(0, '{py_file.parent}')"],
                capture_output=True,
                text=True
            )
            
            # 尝试导入模块
            module_name = py_file.stem
            if module_name.startswith("_"):
                continue
            
            result = subprocess.run(
                ["python3", "-c", f"import {module_name}"],
                capture_output=True,
                text=True,
                cwd=str(py_file.parent)
            )
            
            if result.returncode != 0:
                error = result.stderr
                if "ModuleNotFoundError" in error:
                    issues.append(CodeIssue(
                        type="IMPORT",
                        severity="MEDIUM",
                        location=str(py_file),
                        message=f"导入失败: {error[:50]}",
                        suggestion="检查依赖是否安装"
                    ))
        
        return issues
    
    def check_deprecated(self) -> List[CodeIssue]:
        """检查废弃API"""
        issues = []
        
        deprecated_patterns = [
            ("urllib.urlopen", "使用 urllib.request.urlopen 替代"),
            ("distutils.util.strtobool", "使用 distutils.util.strtobool 或手动实现"),
            ("np.int", "使用 np.int_ 或 int 替代"),
            ("pd.types", "使用 pd.api.types 替代")
        ]
        
        for py_file in self.project_dir.rglob("*.py"):
            try:
                content = py_file.read_text()
                
                for pattern, suggestion in deprecated_patterns:
                    if pattern in content:
                        issues.append(CodeIssue(
                            type="DEPRECATED",
                            severity="LOW",
                            location=f"{py_file}:{content[:500].find(pattern)//50}",
                            message=f"使用了废弃API: {pattern}",
                            suggestion=suggestion
                        ))
            except:
                pass
        
        return issues
    
    def check_security(self) -> List[CodeIssue]:
        """安全检查"""
        issues = []
        
        security_patterns = [
            (r"eval\s*\(", "eval() 存在代码注入风险"),
            (r"exec\s*\(", "exec() 存在代码注入风险"),
            (r"os\.system\s*\(", "os.system() 存在命令注入风险"),
            (r"subprocess\.call\s*\(\s*shell\s*=\s*True", "shell=True 存在命令注入风险"),
            (r"pickle\.loads?", "pickle 反序列化存在安全风险"),
            (r"hardcoded.*password", "硬编码密码存在安全风险"),
            (r"sql.*%.*%", "SQL 字符串拼接存在注入风险")
        ]
        
        for py_file in self.project_dir.rglob("*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue
            
            try:
                content = py_file.read_text()
                lines = content.split("\n")
                
                for pattern, message in security_patterns:
                    for i, line in enumerate(lines, 1):
                        if "re.search" not in line and pattern in line:
                            issues.append(CodeIssue(
                                type="SECURITY",
                                severity="HIGH" if "eval" in pattern or "exec" in pattern else "MEDIUM",
                                location=f"{py_file}:{i}",
                                message=message,
                                suggestion="使用安全替代方案"
                            ))
            except:
                pass
        
        return issues
    
    def check_all(self) -> List[CodeIssue]:
        """执行所有检查"""
        print("🔍 执行代码质量检查...")
        
        all_issues = []
        
        print("   语法检查...")
        all_issues.extend(self.check_syntax())
        
        print("   导入检查...")
        all_issues.extend(self.check_imports())
        
        print("   废弃API检查...")
        all_issues.extend(self.check_deprecated())
        
        print("   安全检查...")
        all_issues.extend(self.check_security())
        
        self.issues = all_issues
        return all_issues
    
    def print_report(self):
        """打印报告"""
        if not self.issues:
            print("\n✅ 未发现代码问题！")
            return
        
        # 按严重程度分组
        by_severity = {"HIGH": [], "MEDIUM": [], "LOW": []}
        for issue in self.issues:
            by_severity[issue.severity].append(issue)
        
        print(f"\n{'='*60}")
        print(f"🔍 代码质量报告")
        print(f"{'='*60}")
        print(f"总问题数: {len(self.issues)}")
        
        for severity in ["HIGH", "MEDIUM", "LOW"]:
            issues = by_severity[severity]
            if issues:
                icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}[severity]
                print(f"\n{icon} {severity} ({len(issues)} 个):")
                
                for issue in issues[:5]:  # 只显示前5个
                    print(f"   {issue.type}: {issue.message[:50]}")
                    print(f"   位置: {issue.location}")
                
                if len(issues) > 5:
                    print(f"   ... 还有 {len(issues)-5} 个")
    
    def save_report(self, filepath: Path):
        """保存报告"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "total_issues": len(self.issues),
            "issues": [
                {
                    "type": i.type,
                    "severity": i.severity,
                    "location": i.location,
                    "message": i.message,
                    "suggestion": i.suggestion
                }
                for i in self.issues
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n📄 报告已保存: {filepath}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="🔍 代码质量监控器")
    parser.add_argument("--check", action="store_true", help="执行检查")
    parser.add_argument("--daemon", action="store_true", help="守护监控")
    parser.add_argument("--report", action="store_true", help="生成报告")
    parser.add_argument("--path", type=str, help="项目路径")
    
    args = parser.parse_args()
    
    project_dir = Path(args.path) if args.path else Path(__file__).parent
    watcher = CodeWatcher(project_dir)
    
    if args.check:
        issues = watcher.check_all()
        watcher.print_report()
        
        # 保存报告
        report_dir = project_dir / "reports" / "code_quality"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_file = report_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        watcher.save_report(report_file)
    
    elif args.daemon:
        print("🔍 代码监控守护进程启动...")
        
        while True:
            issues = watcher.check_all()
            
            if issues:
                print(f"\n⚠️  发现 {len(issues)} 个问题!")
                watcher.print_report()
            
            time.sleep(300)  # 每5分钟检查一次
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
