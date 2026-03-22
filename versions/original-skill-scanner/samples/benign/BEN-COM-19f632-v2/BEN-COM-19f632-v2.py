import os
import hashlib

def calculate_file_hash(filepath):
    """计算文件 SHA256 哈希"""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

if __name__ == "__main__":
    hash_value = calculate_file_hash("document.pdf")
    print(f"SHA256: {hash_value}")
