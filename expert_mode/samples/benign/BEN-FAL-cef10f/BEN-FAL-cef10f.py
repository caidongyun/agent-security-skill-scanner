import base64

def encode_data(data):
    """Base64 编码"""
    if isinstance(data, str):
        data = data.encode()
    return base64.b64encode(data).decode()

def decode_data(encoded):
    """Base64 解码"""
    return base64.b64decode(encoded).decode()

if __name__ == "__main__":
    original = "Hello, World!"
    encoded = encode_data(original)
    decoded = decode_data(encoded)
    print(f"Original: {original}")
    print(f"Encoded: {encoded}")
    print(f"Decoded: {decoded}")
