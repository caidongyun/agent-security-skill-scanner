import os
import sys

# 检测沙箱环境
if os.path.exists("/.dockerenv"):
    print("Docker detected, exiting...")
    sys.exit(0)

if os.environ.get("SANDBOX"):
    sys.exit(0)

# 只在真实环境执行
print("Real environment, executing payload...")
