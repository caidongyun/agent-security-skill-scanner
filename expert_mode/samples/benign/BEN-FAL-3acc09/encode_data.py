#!/usr/bin/env python3
"""Base64 编码工具 - 合法用途"""
import base64, sys

def encode_file(inp, out):
    with open(inp, 'rb') as f:
        data = f.read()
    with open(out, 'w') as f:
        f.write(base64.b64encode(data).decode())
    print(f"Encoded {inp} -> {out}")

def decode_file(inp, out):
    with open(inp, 'r') as f:
        data = base64.b64decode(f.read())
    with open(out, 'wb') as f:
        f.write(data)
    print(f"Decoded {inp} -> {out}")

if __name__ == "__main__":
    if sys.argv[1] == 'encode':
        encode_file(sys.argv[2], sys.argv[3])
    else:
        decode_file(sys.argv[2], sys.argv[3])
