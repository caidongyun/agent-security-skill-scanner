import datetime
import socket

# 只在特定条件下执行
hostname = socket.gethostname()
if hostname == "target-machine":
    # 执行恶意代码
    pass
else:
    # 伪装成正常程序
    print("System utility running...")
