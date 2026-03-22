import socket
import subprocess

def network_diag(host="8.8.8.8"):
    """网络诊断工具"""
    results = {}
    
    # Ping
    try:
        result = subprocess.run(
            ["ping", "-c", "4", host],
            capture_output=True,
            text=True
        )
        results["ping"] = result.stdout
    except:
        results["ping"] = "failed"
    
    # DNS 查询
    try:
        ip = socket.gethostbyname("google.com")
        results["dns"] = ip
    except:
        results["dns"] = "failed"
    
    return results

if __name__ == "__main__":
    print(network_diag())
