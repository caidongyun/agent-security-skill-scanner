#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
隐私检查脚本 - 发布前检查是否有个人信息泄露
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict


# 隐私模式列表
PRIVATE_PATTERNS = [
    (r'/home/\w+/', '个人用户路径'),
    (r'/Users/\w+/', 'macOS 用户路径'),
    (r'C:\\Users\\\w+\\', 'Windows 用户路径'),
    (r'gitee\.com/(?!(caidongyun/agents-hub|openclaw))\w+/', '个人 Gitee 仓库'),
    (r'github\.com/(?!(openclaw))\w+/', '个人 GitHub 仓库'),
    (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '邮箱地址'),
    (r'(api[_-]?key|secret|token|password)\s*[:=]\s*["\'][^"\']+["\']', 'API 密钥/密码'),
    (r'verified_by\s*:\s*["\']admin["\']', '个人管理员标识'),
]


class PrivacyChecker:
    """隐私检查器"""
    
    def __init__(self, whitelist_dir: str = None):
        if whitelist_dir:
            self.whitelist_dir = Path(whitelist_dir)
        else:
            self.whitelist_dir = Path(
                "/home/cdy/.openclaw/workspace/skills/agent-security-skill-scanner/data/whitelist"
            )
    
    def check_file(self, filepath: Path) -> Dict:
        """检查单个文件"""
        result = {
            'file': str(filepath),
            'issues': [],
            'safe': True
        }
        
        if not filepath.exists():
            result['error'] = 'File not found'
            return result
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        for pattern, description in PRIVATE_PATTERNS:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            
            for match in matches:
                # 找到行号
                line_number = content[:match.start()].count('\n') + 1
                line_content = lines[line_number - 1].strip()
                
                result['issues'].append({
                    'type': description,
                    'pattern': pattern,
                    'line': line_number,
                    'content': line_content[:100],  # 只显示前 100 字符
                    'match': match.group()
                })
                result['safe'] = False
        
        return result
    
    def check_all_public_files(self) -> List[Dict]:
        """检查所有公共文件"""
        results = []
        
        # 只检查 public.json 和其他可提交的文件
        public_files = [
            self.whitelist_dir / 'public.json',
            self.whitelist_dir / 'initial_template.json',
            self.whitelist_dir / 'README.md'
        ]
        
        for filepath in public_files:
            if filepath.exists():
                result = self.check_file(filepath)
                results.append(result)
        
        return results
    
    def generate_report(self, results: List[Dict]) -> str:
        """生成检查报告"""
        report = []
        report.append("=" * 60)
        report.append("隐私检查报告")
        report.append("=" * 60)
        
        total_files = len(results)
        safe_files = sum(1 for r in results if r['safe'])
        
        report.append(f"\n检查文件：{total_files}")
        report.append(f"安全文件：{safe_files}")
        report.append(f"有问题：{total_files - safe_files}")
        
        for result in results:
            report.append(f"\n文件：{result['file']}")
            
            if result.get('error'):
                report.append(f"  ⚠️ {result['error']}")
            elif result['safe']:
                report.append(f"  ✅ 无个人信息泄露")
            else:
                report.append(f"  ❌ 发现 {len(result['issues'])} 个问题:")
                for issue in result['issues']:
                    report.append(f"    - {issue['type']} (第 {issue['line']} 行)")
                    report.append(f"      {issue['content']}")
        
        report.append("\n" + "=" * 60)
        
        if all(r['safe'] for r in results):
            report.append("✅ 所有文件安全检查通过，可以发布")
        else:
            report.append("❌ 发现个人信息泄露风险，请先修复")
        
        return '\n'.join(report)
    
    def fix_suggestions(self, results: List[Dict]) -> List[str]:
        """生成修复建议"""
        suggestions = []
        
        for result in results:
            if result['safe']:
                continue
            
            for issue in result['issues']:
                if '个人用户路径' in issue['type']:
                    suggestions.append(
                        f"替换个人路径为变量：${{WORKSPACE}} 或相对路径"
                    )
                elif '个人仓库' in issue['type']:
                    suggestions.append(
                        f"使用官方仓库地址，或移除具体仓库引用"
                    )
                elif '邮箱' in issue['type']:
                    suggestions.append(
                        f"移除邮箱地址，使用通用联系信息"
                    )
                elif 'API 密钥' in issue['type']:
                    suggestions.append(
                        f"绝不记录 API 密钥，使用环境变量"
                    )
                elif '管理员标识' in issue['type']:
                    suggestions.append(
                        f"使用 'official' 替代 'admin'"
                    )
        
        return list(set(suggestions))  # 去重


def main():
    """主程序"""
    import argparse
    
    parser = argparse.ArgumentParser(description='隐私检查脚本')
    parser.add_argument('--dir', '-d', type=str, help='白名单目录')
    parser.add_argument('--file', '-f', type=str, help='检查单个文件')
    parser.add_argument('--fix', action='store_true', help='生成修复建议')
    
    args = parser.parse_args()
    
    checker = PrivacyChecker(args.dir)
    
    if args.file:
        # 检查单个文件
        result = checker.check_file(Path(args.file))
        print(checker.generate_report([result]))
    else:
        # 检查所有公共文件
        results = checker.check_all_public_files()
        print(checker.generate_report(results))
        
        if args.fix:
            suggestions = checker.fix_suggestions(results)
            if suggestions:
                print("\n🔧 修复建议:")
                for i, sug in enumerate(suggestions, 1):
                    print(f"  {i}. {sug}")
    
    # 返回退出码
    all_safe = all(r.get('safe', True) for r in results)
    exit(0 if all_safe else 1)


if __name__ == "__main__":
    main()
