#!/usr/bin/env python3
"""
Expert Mode - Subprocess Sandbox Executor
沙箱行为检测执行器
"""

import subprocess
import os
import sys
import json
import time
import signal
import tempfile
import shutil
import threading
from pathlib import Path
from typing import Dict, List, Optional

# 行为监控
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class BehaviorMonitor:
    """行为监控器 - 增强版"""
    
    # 危险行为模式
    DANGEROUS_PATTERNS = {
        # 文件操作
        "/etc/shadow": {"risk": 100, "desc": "读取系统凭据"},
        "/etc/passwd": {"risk": 80, "desc": "读取用户信息"},
        "/root": {"risk": 70, "desc": "访问root目录"},
        ".ssh": {"risk": 70, "desc": "SSH相关操作"},
        
        # 网络
        "socket": {"risk": 40, "desc": "网络socket创建"},
        "connect": {"risk": 30, "desc": "网络连接"},
        
        # 进程
        "fork": {"risk": 60, "desc": "创建子进程"},
        "Popen": {"risk": 50, "desc": "执行外部命令"},
        
        # 命令执行
        "system": {"risk": 70, "desc": "执行系统命令"},
        "shell": {"risk": 70, "desc": "Shell命令执行"},
    }
    
    def __init__(self, pid: int):
        self.pid = pid
        self.behaviors = []
        self.monitoring = False
        self._thread = None
        self._seen_pids = set()
        
    def start(self):
        """开始监控"""
        if not PSUTIL_AVAILABLE:
            print("[WARN] psutil not available, skipping behavior monitoring")
            return
            
        self.monitoring = True
        self._seen_pids.add(self.pid)
        self._thread = threading.Thread(target=self._monitor_loop)
        self._thread.daemon = True
        self._thread.start()
        
    def _monitor_loop(self):
        """监控循环"""
        try:
            proc = psutil.Process(self.pid)
            while self.monitoring:
                try:
                    # 监控子进程
                    for child in proc.children(recursive=True):
                        self.behaviors.append({
                            "type": "process",
                            "detail": f"创建子进程 PID={child.pid} {child.name()}",
                            "risk": 30
                        })
                    
                    # 监控文件操作
                    try:
                        for f in proc.open_files():
                            if self._is_suspicious_path(f.path, "read"):
                                self.behaviors.append({
                                    "type": "file",
                                    "detail": f"读取文件 {f.path}",
                                    "risk": 10
                                })
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        pass
                    
                    # 监控网络
                    try:
                        for conn in proc.connections():
                            if conn.status == 'ESTABLISHED' and conn.raddr:
                                self.behaviors.append({
                                    "type": "network",
                                    "detail": f"网络连接 {conn.raddr.ip}:{conn.raddr.port}",
                                    "risk": 40
                                })
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        pass
                        
                except psutil.NoSuchProcess:
                    break
                    
                time.sleep(0.5)
        except Exception as e:
            print(f"[WARN] Monitor error: {e}")
            
    def _is_suspicious_path(self, path: str, operation: str) -> bool:
        """检查可疑路径"""
        suspicious_paths = [
            "/etc/shadow", "/etc/passwd", "/etc/sudoers",
            "/root", "/home/.ssh", "/.ssh"
        ]
        return any(path.startswith(sp) for sp in suspicious_paths)
        
    def stop(self):
        """停止监控"""
        self.monitoring = False
        if self._thread:
            self._thread.join(timeout=2)
            
    def get_behaviors(self) -> List[Dict]:
        """获取行为列表"""
        return self.behaviors


class SubprocessSandbox:
    """Subprocess沙箱执行器"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {
            "max_memory_mb": 256,
            "max_cpu_percent": 50,
            "timeout_seconds": 30,
            "allow_network": False,
            "work_dir": "/tmp/sandbox"
        }
        
    def execute(self, skill_path: str) -> Dict:
        """
        在沙箱中执行Skill
        
        Args:
            skill_path: Skill目录路径
            
        Returns:
            执行结果和行为日志
        """
        # 准备环境 - 使用skill自己的目录
        skill_dir = Path(skill_path)
        
        # 查找要执行的入口文件
        entry_file = self._find_entry_file(skill_path)
        if not entry_file:
            return {
                "success": False,
                "error": "未找到入口文件 (cli.py/main.py/SKILL.md)"
            }
        
        # 构建执行命令
        if entry_file.endswith('.py'):
            cmd = ["python3", entry_file]
        elif entry_file.endswith('.js'):
            cmd = ["node", entry_file]
        elif entry_file.endswith('.sh'):
            cmd = ["bash", entry_file]
        else:
            return {
                "success": False,
                "error": f"不支持的文件类型: {entry_file}"
            }
        
        print(f"[Sandbox] 执行命令: {' '.join(cmd)}")
        print(f"[Sandbox] 工作目录: {work_dir}")
        print(f"[Sandbox] 超时: {self.config['timeout_seconds']}s")
        
        # 执行
        start_time = time.time()
        behavior_log = []
        
        try:
            # 创建子进程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=work_dir,
                env=self._get_safe_env(),
                preexec_fn=os.setsid  # 创建新进程组
            )
            
            # 启动行为监控
            monitor = BehaviorMonitor(process.pid)
            monitor.start()
            
            # 等待执行完成或超时
            try:
                stdout, stderr = process.communicate(
                    timeout=self.config["timeout_seconds"]
                )
                exit_code = process.returncode
            except subprocess.TimeoutExpired:
                # 超时，杀死进程组
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    time.sleep(0.5)
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                except:
                    pass
                exit_code = -1
                stderr = b"Timeout exceeded"
                
            # 停止监控
            monitor.stop()
            behaviors = monitor.get_behaviors()
            
            # 检测危险行为
            risk_score = self._calculate_risk(behaviors)
            
            result = {
                "success": exit_code == 0,
                "exit_code": exit_code,
                "duration": time.time() - start_time,
                "stdout": stdout.decode('utf-8', errors='ignore')[:1000],
                "stderr": stderr.decode('utf-8', errors='ignore')[:1000],
                "behaviors": behaviors,
                "risk_score": risk_score,
                "risk_level": self._get_risk_level(risk_score),
                "recommendation": self._get_recommendation(risk_score)
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "risk_score": 0,
                "risk_level": "UNKNOWN"
            }
            
    def _find_entry_file(self, skill_path: str) -> Optional[str]:
        """查找入口文件"""
        path = Path(skill_path)
        candidates = ["cli.py", "main.py", "index.py", "run.py", "__main__.py"]
        
        for candidate in candidates:
            f = path / candidate
            if f.exists():
                return str(f)
        
        # 如果没找到，返回第一个Python文件
        for f in path.rglob("*.py"):
            if not f.name.startswith('_'):
                return str(f)
                
        return None
        
    def _get_safe_env(self) -> Dict:
        """获取安全的环境变量"""
        env = os.environ.copy()
        
        # 禁止网络
        if not self.config.get("allow_network", False):
            env.pop("HTTP_PROXY", None)
            env.pop("HTTPS_PROXY", None)
            env.pop("http_proxy", None)
            env.pop("https_proxy", None)
            
        return env
        
    def _calculate_risk(self, behaviors: List[Dict]) -> int:
        """计算风险分"""
        risk_rules = {
            # 高风险
            "/etc/shadow": 100,
            "/etc/passwd": 100,
            "shadow": 100,
            "passwd": 100,
            "sudo": 90,
            "su ": 90,
            "wget": 80,
            "curl": 80,
            "nc ": 100,
            "netcat": 100,
            "反弹shell": 100,
            # 中风险
            "/etc/": 50,
            "/tmp/": 20,
            "process": 30,
            "fork": 80,
            "exec": 50,
            # 网络
            "network": 40,
            "connection": 40,
        }
        
        total_risk = 0
        seen = set()
        
        for b in behaviors:
            detail = b.get("detail", "").lower()
            # 规则匹配
            for keyword, score in risk_rules.items():
                if keyword in detail and detail not in seen:
                    total_risk += score
                    seen.add(detail)
                    
            # 使用已有的风险分
            total_risk += b.get("risk", 0)
            
        return min(total_risk, 150)  # 上限150
        
    def _get_risk_level(self, score: int) -> str:
        """获取风险等级"""
        if score > 100:
            return "CRITICAL"
        elif score > 60:
            return "HIGH"
        elif score > 30:
            return "WARNING"
        else:
            return "SAFE"
            
    def _get_recommendation(self, score: int) -> str:
        """获取处置建议"""
        if score > 100:
            return "🚫 严重风险 - 立即拦截"
        elif score > 60:
            return "❌ 高风险 - 建议拦截"
        elif score > 30:
            return "⚠️ 中风险 - 需人工确认"
        else:
            return "✅ 安全 - 允许执行"


async def expert_mode_analyze(skill_path: str) -> Dict:
    """
    专家模式分析
    
    Args:
        skill_path: Skill目录路径
        
    Returns:
        分析结果
    """
    sandbox = SubprocessSandbox()
    result = sandbox.execute(skill_path)
    
    return {
        "expert_mode": True,
        "isolation": "subprocess",
        **result
    }


if __name__ == "__main__":
    # 测试
    import sys
    import asyncio
    if len(sys.argv) > 1:
        result = asyncio.run(expert_mode_analyze(sys.argv[1]))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("用法: python expert_sandbox.py <skill_path>")
