#!/usr/bin/env python3
"""正常 Python 脚本 - 白样本 01"""

import os
import sys
import json

def main():
    """主函数"""
    print("Hello, World!")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    
    data = {
        'name': 'test',
        'value': 42,
        'items': [1, 2, 3]
    }
    
    print(json.dumps(data, indent=2))

if __name__ == '__main__':
    main()
