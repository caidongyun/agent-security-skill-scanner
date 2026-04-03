# Business scenario: webdev
# Generated: 2026-04-02 10:47:53.106108

#!/usr/bin/env python3
# API 客户端
import requests
import base64
auth = base64.b64encode(b"user:pass").decode()
response = requests.get("https://api.example.com/data")
print("API 调用完成")
