#!/usr/bin/env python3
"""
修复测试用例 JSON 文件中的 Python 语法
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
TEST_CASES_DIR = BASE_DIR / "tests" / "cases"

def fix_json_file(file_path):
    """修复 JSON 文件中的 Python 语法"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original = content
    
    # 修复列表推导式 -> 替换为实际列表
    # 模式 1：["xxx" for _ in range(N)]
    list_comp_pattern1 = r'\[(["\'].*?["\'])\s+for\s+_ in range\((\d+)\)\]'
    
    def replace_list_comp1(match):
        item = match.group(1)
        count = int(match.group(2))
        items = ", ".join([item] * count)
        return f"[{items}]"
    
    content = re.sub(list_comp_pattern1, replace_list_comp1, content)
    
    # 模式 2：["xxx" + str(i) for i in range(N)]
    list_comp_pattern2 = r'\[(["\'].*?["\'])\s*\+\s*str\(i\)\s+for\s+i\s+in\s+range\((\d+)\)\]'
    
    def replace_list_comp2(match):
        base = match.group(1)
        count = int(match.group(2))
        items = ", ".join([f'"{base}"' for _ in range(count)])
        return f"[{items}]"
    
    content = re.sub(list_comp_pattern2, replace_list_comp2, content)
    
    # 修复字符串乘法："xxx" * N -> 重复的字符串
    str_mult_pattern = r'(["\'].*?["\'])\s*\*\s*(\d+)'
    
    def replace_str_mult(match):
        s = match.group(1)
        count = int(match.group(2))
        # 移除引号，重复，再加引号
        inner = s[1:-1]  # 去掉首尾引号
        repeated = inner * count
        return f'"{repeated}"'
    
    content = re.sub(str_mult_pattern, replace_str_mult, content)
    
    if content != original:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    print("🔧 修复测试用例 JSON 文件")
    print("=" * 50)
    
    fixed = []
    for json_file in TEST_CASES_DIR.glob("*.json"):
        if fix_json_file(json_file):
            fixed.append(json_file.name)
            print(f"✅ 修复：{json_file.name}")
    
    if not fixed:
        print("ℹ️  无需修复的文件")
    else:
        print(f"\n✨ 修复完成：{len(fixed)} 个文件")

if __name__ == "__main__":
    main()
