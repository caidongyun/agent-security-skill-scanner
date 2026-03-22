import subprocess
import platform

def get_system_info():
    """收集系统信息 (用于诊断)"""
    info = {}
    
    # 操作系统
    info["platform"] = platform.system()
    info["release"] = platform.release()
    info["version"] = platform.version()
    
    # CPU
    try:
        result = subprocess.run(["nproc"], capture_output=True, text=True)
        info["cpu_cores"] = int(result.stdout.strip())
    except:
        info["cpu_cores"] = "unknown"
    
    # 内存
    try:
        with open("/proc/meminfo") as f:
            meminfo = f.read()
        info["memory"] = meminfo.split("\n")[0]
    except:
        info["memory"] = "unknown"
    
    return info

if __name__ == "__main__":
    print(get_system_info())
