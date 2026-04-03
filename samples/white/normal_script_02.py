#!/usr/bin/env python3
"""正常 Python 脚本 - 白样本 02 - 文件处理"""

import os
from pathlib import Path

def process_files(directory):
    """处理目录中的文件"""
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"Directory not found: {directory}")
        return
    
    for file_path in dir_path.glob('*.txt'):
        print(f"Processing: {file_path.name}")
        content = file_path.read_text()
        print(f"  Lines: {len(content.splitlines())}")

def main():
    """主函数"""
    process_files('.')

if __name__ == '__main__':
    main()
