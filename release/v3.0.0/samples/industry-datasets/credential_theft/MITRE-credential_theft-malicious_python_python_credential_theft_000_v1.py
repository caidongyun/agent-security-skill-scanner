#!/usr/bin/env python3

"""Credential theft - test sample"""
import os

def steal_creds():
    paths = [
        os.path.expanduser("~/.netrc"),
        "/etc/shadow",
    ]
    for p in paths:
        if os.path.exists(p):
            with io.open(p) as f:
                print("Found:", p)

steal_creds()
