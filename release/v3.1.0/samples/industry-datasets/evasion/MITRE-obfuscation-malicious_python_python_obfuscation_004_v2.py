#!/usr/bin/env python3

"""Obfuscation - obfuscation"""
import base64
import zlib

# Encoded payload
payload = "malicious_code_here"
encoded = base64.b64encode(zlib.compress(payload.encode()))
exec(zlib.decompress(base64.b64decode(encoded)))
