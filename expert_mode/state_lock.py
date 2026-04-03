#!/usr/bin/env python3
"""
状态文件锁机制 - 防止并发冲突
"""

import fcntl
import json
import time
import os
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, Dict, Any

class StateLock:
    """文件锁管理器"""
    
    def __init__(self, state_file: str, timeout: int = 30):
        self.state_file = Path(state_file)
        self.lock_file = self.state_file.with_suffix(self.state_file.suffix + '.lock')
        self.timeout = timeout
        self.fd = None
    
    def acquire(self) -> bool:
        """获取锁"""
        start_time = time.time()
        
        while True:
            try:
                self.fd = open(self.lock_file, 'w')
                fcntl.flock(self.fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.fd.write(str(os.getpid()))
                self.fd.flush()
                return True
            except (IOError, OSError):
                if self.fd:
                    self.fd.close()
                    self.fd = None
                
                if time.time() - start_time > self.timeout:
                    return False
                
                time.sleep(0.1)
    
    def release(self):
        """释放锁"""
        if self.fd:
            try:
                fcntl.flock(self.fd.fileno(), fcntl.LOCK_UN)
                self.fd.close()
                self.lock_file.unlink(missing_ok=True)
            except:
                pass
            finally:
                self.fd = None
    
    def __enter__(self):
        if not self.acquire():
            raise TimeoutError(f"无法获取锁：{self.state_file}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False


class AtomicStateWriter:
    """原子状态写入器"""
    
    @staticmethod
    def write(state_file: str, data: Dict[str, Any], timeout: int = 30) -> bool:
        """原子写入状态文件"""
        state_path = Path(state_file)
        temp_file = state_path.with_suffix(state_path.suffix + '.tmp')
        
        with StateLock(state_file, timeout) as lock:
            try:
                # 写入临时文件
                with open(temp_file, 'w') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    f.flush()
                    os.fsync(f.fileno())
                
                # 原子替换
                os.replace(temp_file, state_path)
                return True
            except Exception as e:
                temp_file.unlink(missing_ok=True)
                raise e
    
    @staticmethod
    def read(state_file: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """读取状态文件（带锁）"""
        with StateLock(state_file, timeout):
            try:
                with open(state_file, 'r') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                return None


@contextmanager
def state_lock(state_file: str, timeout: int = 30):
    """上下文管理器装饰器"""
    lock = StateLock(state_file, timeout)
    try:
        lock.acquire()
        yield lock
    finally:
        lock.release()


# ============ 使用示例 ============
if __name__ == "__main__":
    # 示例 1: 使用上下文管理器
    with state_lock(".test_state.json"):
        print("持有锁，可以安全读写")
    
    # 示例 2: 原子写入
    AtomicStateWriter.write(".test_state.json", {"round": 1, "status": "running"})
    
    # 示例 3: 读取
    state = AtomicStateWriter.read(".test_state.json")
    print(f"状态：{state}")
