import gzip
import shutil

def compress_file(input_path, output_path=None):
    """压缩文件"""
    if output_path is None:
        output_path = input_path + ".gz"
    
    with open(input_path, 'rb') as f_in:
        with gzip.open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    return output_path

def decompress_file(input_path, output_path=None):
    """解压文件"""
    if output_path is None:
        output_path = input_path[:-3] if input_path.endswith('.gz') else input_path + ".decompressed"
    
    with gzip.open(input_path, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    return output_path

if __name__ == "__main__":
    compressed = compress_file("test.txt")
    decompressed = decompress_file(compressed)
