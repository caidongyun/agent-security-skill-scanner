#!/usr/bin/env python3
"""系统信息收集 - 合法使用 subprocess"""
import subprocess, json

def get_info():
    info = {}
    info['hostname'] = subprocess.run(['hostname'], capture_output=True, text=True).stdout.strip()
    info['user'] = subprocess.run(['whoami'], capture_output=True, text=True).stdout.strip()
    return info

if __name__ == "__main__":
    print(json.dumps(get_info(), indent=2))
