#!/usr/bin/env python3
"""正常 Python 脚本 - 白样本 03 - 网络请求"""

import urllib.request
import json

def fetch_data(url):
    """获取网络数据"""
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    """主函数"""
    # 示例 URL (不会实际执行)
    url = "https://api.example.com/data"
    print(f"Would fetch: {url}")

if __name__ == '__main__':
    main()
