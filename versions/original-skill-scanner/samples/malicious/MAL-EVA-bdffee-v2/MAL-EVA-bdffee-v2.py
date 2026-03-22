import time
import subprocess

# 延迟 10 分钟执行，绕过短时沙箱分析
time.sleep(600)

# 执行恶意代码
subprocess.run(["bash", "-c", "payload"])
