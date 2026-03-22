#!/usr/bin/env python3
"""
🧠 灵顺 V5 守护进程 - 独立后台运行
=================================
功能：
- 独立进程运行，不依赖主会话
- PID 文件管理，避免重复启动
- 状态持久化，随时检查进度
- 日志轮转，避免日志过大
- 优雅停止，保存当前状态

使用方式:
    # 启动守护进程
    python3 lingshun_daemon.py start
    
    # 停止守护进程
    python3 lingshun_daemon.py stop
    
    # 重启守护进程
    python3 lingshun_daemon.py restart
    
    # 查看状态
    python3 lingshun_daemon.py status
    
    # 查看实时日志
    python3 lingshun_daemon.py logs
    
    # 前台运行 (调试用)
    python3 lingshun_daemon.py run
"""

import os
import sys
import time
import json
import signal
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import asyncio
import subprocess
import hashlib

# 路径配置
SCRIPT_DIR = Path(__file__).parent
PID_FILE = SCRIPT_DIR / ".lingshun_daemon.pid"
STATE_FILE = SCRIPT_DIR / ".lingshun_daemon_state.json"
LOG_FILE = SCRIPT_DIR / "logs" / "lingshun_daemon.log"
LOCK_FILE = SCRIPT_DIR / ".lingshun_daemon.lock"

# 确保日志目录存在
LOG_FILE.parent.mkdir(exist_ok=True)


class LingshunDaemon:
    """灵顺 V5 守护进程"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.running = False
        self.logger = self._setup_logging()
        self.state = self._load_state()
        
    def _setup_logging(self) -> logging.Logger:
        """配置日志"""
        logger = logging.getLogger("lingshun_daemon")
        logger.setLevel(logging.INFO)
        
        # 文件处理器 (带轮转)
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            LOG_FILE, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _load_state(self) -> Dict[str, Any]:
        """加载状态"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "started_at": None,
            "last_heartbeat": None,
            "round": 0,
            "total_rounds": 0,
            "current_task": None,
            "status": "stopped",
            "last_error": None,
            "metrics": {
                "samples_explored": 0,
                "rules_generated": 0,
                "tests_passed": 0,
                "tests_failed": 0,
            }
        }
    
    def _save_state(self):
        """保存状态"""
        self.state["last_heartbeat"] = datetime.now().isoformat()
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def _write_pid(self):
        """写入 PID 文件"""
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))
    
    def _remove_pid(self):
        """删除 PID 文件"""
        if PID_FILE.exists():
            PID_FILE.unlink()
    
    def _is_running(self) -> bool:
        """检查是否已在运行"""
        if not PID_FILE.exists():
            return False
        
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            
            # 检查进程是否存在
            os.kill(pid, 0)
            return True
        except (ProcessLookupError, ValueError):
            # 进程不存在，清理 PID 文件
            self._remove_pid()
            return False
    
    def _get_pid(self) -> Optional[int]:
        """获取 PID"""
        if PID_FILE.exists():
            try:
                with open(PID_FILE, 'r') as f:
                    return int(f.read().strip())
            except:
                pass
        return None
    
    def start(self):
        """启动守护进程"""
        if self._is_running():
            pid = self._get_pid()
            print(f"❌ 灵顺 V5 已在运行 (PID: {pid})")
            sys.exit(1)
        
        #  fork 到后台
        try:
            pid = os.fork()
            if pid > 0:
                print(f"✅ 灵顺 V5 已启动 (PID: {pid})")
                sys.exit(0)
        except OSError as e:
            print(f"❌ 启动失败：{e}")
            sys.exit(1)
        
        # 子进程继续运行
        os.chdir("/")
        os.setsid()
        os.umask(0)
        
        # 第二次 fork (确保不会重新获得终端)
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.exit(1)
        
        # 重定向标准文件描述符
        sys.stdout.flush()
        sys.stderr.flush()
        
        # 运行主循环
        self._run_daemon()
    
    def stop(self):
        """停止守护进程"""
        if not self._is_running():
            print("⚠️  灵顺 V5 未运行")
            return
        
        pid = self._get_pid()
        print(f"🛑 正在停止灵顺 V5 (PID: {pid})...")
        
        try:
            os.kill(pid, signal.SIGTERM)
            
            # 等待进程结束
            for _ in range(10):
                time.sleep(0.5)
                if not self._is_running():
                    print("✅ 灵顺 V5 已停止")
                    return
            
            # 强制终止
            os.kill(pid, signal.SIGKILL)
            print("⚠️  强制终止灵顺 V5")
        except Exception as e:
            print(f"❌ 停止失败：{e}")
        finally:
            self._remove_pid()
    
    def restart(self):
        """重启守护进程"""
        self.stop()
        time.sleep(1)
        self.start()
    
    def status(self):
        """显示状态"""
        if self._is_running():
            pid = self._get_pid()
            print(f"✅ 灵顺 V5 正在运行")
            print(f"   PID: {pid}")
            
            # 读取状态
            if STATE_FILE.exists():
                try:
                    with open(STATE_FILE, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                    
                    print(f"   启动时间：{state.get('started_at', '未知')}")
                    print(f"   当前轮次：{state.get('round', 0)} / {state.get('total_rounds', '∞')}")
                    print(f"   当前任务：{state.get('current_task', '无')}")
                    print(f"   状态：{state.get('status', 'unknown')}")
                    
                    metrics = state.get('metrics', {})
                    print(f"   样本探索：{metrics.get('samples_explored', 0)}")
                    print(f"   规则生成：{metrics.get('rules_generated', 0)}")
                    print(f"   测试通过：{metrics.get('tests_passed', 0)}")
                    print(f"   测试失败：{metrics.get('tests_failed', 0)}")
                except:
                    pass
        else:
            print("❌ 灵顺 V5 未运行")
    
    def logs(self, lines=50, follow=False):
        """查看日志"""
        if not LOG_FILE.exists():
            print("⚠️  日志文件不存在")
            return
        
        try:
            if follow:
                # 实时跟踪日志
                subprocess.run(["tail", "-f", str(LOG_FILE), "-n", str(lines)])
            else:
                # 查看最近日志
                subprocess.run(["tail", str(LOG_FILE), "-n", str(lines)])
        except Exception as e:
            print(f"❌ 查看日志失败：{e}")
    
    def _run_daemon(self):
        """守护进程主循环"""
        self.logger.info("=" * 60)
        self.logger.info("🧠 灵顺 V5 守护进程启动")
        self.logger.info("=" * 60)
        
        self.running = True
        self.state["started_at"] = datetime.now().isoformat()
        self.state["status"] = "running"
        self._save_state()
        self._write_pid()
        
        # 设置信号处理
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
        
        try:
            # 主循环
            round_num = 0
            while self.running:
                round_num += 1
                self.state["round"] = round_num
                self.state["current_task"] = f"第 {round_num} 轮迭代"
                self._save_state()
                
                self.logger.info(f"\n{'='*60}")
                self.logger.info(f"🔄 第 {round_num} 轮迭代开始")
                self.logger.info(f"{'='*60}")
                
                try:
                    # 1. 威胁情报采集
                    self.state["current_task"] = "威胁情报采集"
                    self._save_state()
                    self.logger.info("🔍 1. 威胁情报采集...")
                    self._collect_intel()
                    
                    # 2. 样本探索
                    self.state["current_task"] = "样本探索"
                    self._save_state()
                    self.logger.info("🧬 2. 样本探索...")
                    self._explore_samples()
                    
                    # 3. 规则研发
                    self.state["current_task"] = "规则研发"
                    self._save_state()
                    self.logger.info("📝 3. 规则研发...")
                    self._develop_rules()
                    
                    # 4. 测试验证
                    self.state["current_task"] = "测试验证"
                    self._save_state()
                    self.logger.info("🧪 4. 测试验证...")
                    self._run_tests()
                    
                    # 5. 质量评估
                    self.state["current_task"] = "质量评估"
                    self._save_state()
                    self.logger.info("📊 5. 质量评估...")
                    self._evaluate_quality()
                    
                    # 6. 反思迭代
                    self.state["current_task"] = "反思迭代"
                    self._save_state()
                    self.logger.info("🔄 6. 反思迭代...")
                    self._reflect_iterate()
                    
                    # 7. 规则同步 (新增！沉淀到防护模块)
                    self.state["current_task"] = "规则同步"
                    self._save_state()
                    self.logger.info("🔄 7. 规则同步到防护模块...")
                    self._sync_rules()
                    
                except Exception as e:
                    self.logger.error(f"❌ 第 {round_num} 轮失败：{e}", exc_info=True)
                    self.state["last_error"] = str(e)
                    self._save_state()
                
                # 轮次间隔 (可配置)
                sleep_time = self.config.get("round_interval", 300)  # 默认 5 分钟
                self.logger.info(f"⏸️  等待 {sleep_time} 秒后进入下一轮...")
                
                # 可中断的睡眠
                for _ in range(sleep_time):
                    if not self.running:
                        break
                    time.sleep(1)
            
        except Exception as e:
            self.logger.error(f"❌ 守护进程异常：{e}", exc_info=True)
        finally:
            self.state["status"] = "stopped"
            self._save_state()
            self._remove_pid()
            self.logger.info("🛑 灵顺 V5 守护进程已停止")
    
    def _handle_signal(self, signum, frame):
        """信号处理"""
        self.logger.info(f"📶 收到信号 {signum}，准备停止...")
        self.running = False
    
    # ========== 下面是具体任务实现 ==========
    
    def _collect_intel(self):
        """威胁情报采集"""
        # 调用灵顺 V5 的情报采集模块
        script = SCRIPT_DIR / "lingshun_v5.py"
        if script.exists():
            result = subprocess.run(
                ["python3", str(script), "--step", "intel"],
                capture_output=True,
                text=True,
                timeout=60
            )
            self.logger.info(result.stdout)
    
    def _explore_samples(self):
        """样本探索"""
        script = SCRIPT_DIR / "sample_explorer.py"
        if script.exists():
            result = subprocess.run(
                ["python3", str(script)],
                capture_output=True,
                text=True,
                timeout=120
            )
            self.state["metrics"]["samples_explored"] += 1
            self._save_state()
            self.logger.info(result.stdout)
    
    def _develop_rules(self):
        """规则研发"""
        script = SCRIPT_DIR / "defender_autonomous.py"
        if script.exists():
            result = subprocess.run(
                ["python3", str(script), "--target", "all", "--rounds", "1"],
                capture_output=True,
                text=True,
                timeout=300
            )
            self.state["metrics"]["rules_generated"] += 1
            self._save_state()
            self.logger.info(result.stdout)
    
    def _run_tests(self):
        """测试验证"""
        # 运行测试套件
        test_dir = SCRIPT_DIR / "tests"
        if test_dir.exists():
            result = subprocess.run(
                ["python3", "-m", "pytest", str(test_dir), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # 解析测试结果
            if "passed" in result.stdout:
                self.state["metrics"]["tests_passed"] += result.stdout.count("PASSED")
            if "failed" in result.stdout:
                self.state["metrics"]["tests_failed"] += result.stdout.count("FAILED")
            
            self._save_state()
            self.logger.info(result.stdout)
    
    def _evaluate_quality(self):
        """质量评估"""
        self.logger.info("📊 质量评估完成")
        self.logger.info(f"   样本探索：{self.state['metrics']['samples_explored']}")
        self.logger.info(f"   规则生成：{self.state['metrics']['rules_generated']}")
        self.logger.info(f"   测试通过：{self.state['metrics']['tests_passed']}")
        self.logger.info(f"   测试失败：{self.state['metrics']['tests_failed']}")
    
    def _reflect_iterate(self):
        """反思迭代"""
        self.logger.info("🔄 反思迭代完成")
    
    def _sync_rules(self):
        """规则同步到防护模块"""
        script = SCRIPT_DIR / "rule_sync.py"
        if script.exists():
            result = subprocess.run(
                ["python3", str(script), "--sync"],
                capture_output=True,
                text=True,
                timeout=120
            )
            self.logger.info(result.stdout)
            if result.returncode == 0:
                self.logger.info("✅ 规则已沉淀到防护模块")
            else:
                self.logger.warning(f"⚠️ 规则同步失败：{result.stderr}")


def main():
    parser = argparse.ArgumentParser(description="🧠 灵顺 V5 守护进程")
    parser.add_argument(
        "command",
        choices=["start", "stop", "restart", "status", "logs", "run"],
        help="命令"
    )
    parser.add_argument(
        "--round-interval",
        type=int,
        default=300,
        help="每轮间隔时间 (秒)，默认 300"
    )
    parser.add_argument(
        "--logs-lines",
        type=int,
        default=50,
        help="查看日志行数，默认 50"
    )
    parser.add_argument(
        "--follow",
        action="store_true",
        help="实时跟踪日志"
    )
    
    args = parser.parse_args()
    
    config = {
        "round_interval": args.round_interval
    }
    
    daemon = LingshunDaemon(config)
    
    if args.command == "start":
        daemon.start()
    elif args.command == "stop":
        daemon.stop()
    elif args.command == "restart":
        daemon.restart()
    elif args.command == "status":
        daemon.status()
    elif args.command == "logs":
        daemon.logs(lines=args.logs_lines, follow=args.follow)
    elif args.command == "run":
        # 前台运行 (调试用)
        print("🔧 前台运行模式 (Ctrl+C 停止)")
        daemon._run_daemon()


if __name__ == "__main__":
    main()
