#!/usr/bin/env python3
"""
Round 14 - 灵顺守护进程

7x24 持续运行，支持健康检查、自动重启、日志轮转
"""

import os
import sys
import time
import signal
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

# ============== 配置 ==============

BASE_DIR = Path(__file__).parent
PID_FILE = BASE_DIR / ".lingshun.pid"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "lingshun_daemon.log"
CONFIG_FILE = BASE_DIR / "daemon_config.yaml"

# 确保日志目录存在
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============== 守护进程 ==============

class LingshunDaemon:
    """灵顺守护进程"""
    
    def __init__(self):
        self.running = True
        self.last_health_check = time.time()
        self.last_intel_update = time.time()
        self.health_check_interval = 60  # 60 秒健康检查
        self.intel_update_interval = 3600  # 1 小时情报更新
        
        # 注册信号处理
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理"""
        logger.info(f"收到信号 {signum}，准备退出...")
        self.running = False
    
    def start(self):
        """启动守护进程"""
        logger.info("="*60)
        logger.info("🚀 灵顺守护进程启动")
        logger.info("="*60)
        
        # 写入 PID 文件
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))
        
        logger.info(f"PID: {os.getpid()}")
        logger.info(f"日志：{LOG_FILE}")
        
        try:
            self._main_loop()
        except Exception as e:
            logger.error(f"守护进程异常：{e}", exc_info=True)
        finally:
            self._cleanup()
    
    def _main_loop(self):
        """主循环"""
        logger.info("进入主循环...")
        
        while self.running:
            try:
                # 健康检查
                if time.time() - self.last_health_check > self.health_check_interval:
                    self._health_check()
                    self.last_health_check = time.time()
                
                # 情报更新
                if time.time() - self.last_intel_update > self.intel_update_interval:
                    self._update_threat_intel()
                    self.last_intel_update = time.time()
                
                # 执行检测任务
                self._run_detection()
                
                # 短暂休眠
                time.sleep(5)
            
            except Exception as e:
                logger.error(f"主循环错误：{e}", exc_info=True)
                time.sleep(10)
    
    def _health_check(self):
        """健康检查"""
        logger.info("❤️  健康检查...")
        
        # 检查内存使用
        import resource
        mem_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024  # MB
        logger.info(f"  内存：{mem_usage:.1f} MB")
        
        if mem_usage > 1024:  # 超过 1GB 警告
            logger.warning(f"  ⚠️  内存使用过高：{mem_usage:.1f} MB")
        
        # 检查磁盘空间
        stat = os.statvfs(BASE_DIR)
        disk_free = stat.f_bavail * stat.f_frsize / 1024 / 1024 / 1024  # GB
        logger.info(f"  磁盘：{disk_free:.1f} GB 可用")
        
        if disk_free < 1:  # 少于 1GB 警告
            logger.warning(f"  ⚠️  磁盘空间不足：{disk_free:.1f} GB")
        
        # 检查日志文件大小
        if LOG_FILE.exists():
            log_size = LOG_FILE.stat().st_size / 1024 / 1024  # MB
            logger.info(f"  日志：{log_size:.1f} MB")
            
            if log_size > 100:  # 超过 100MB 轮转
                self._rotate_logs()
        
        logger.info("  ✅ 健康检查完成")
    
    def _update_threat_intel(self):
        """更新威胁情报"""
        logger.info("🔄 更新威胁情报...")
        
        try:
            # 调用情报更新脚本
            intel_script = BASE_DIR / "update_threat_intel.py"
            if intel_script.exists():
                result = subprocess.run(
                    ['python3', str(intel_script)],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                logger.info(f"  输出：{result.stdout[:200]}")
                if result.returncode != 0:
                    logger.error(f"  错误：{result.stderr[:200]}")
            else:
                logger.info("  ⚠️  情报脚本不存在，跳过")
        except subprocess.TimeoutExpired:
            logger.error("  ❌ 情报更新超时")
        except Exception as e:
            logger.error(f"  ❌ 情报更新失败：{e}")
        
        logger.info("  ✅ 情报更新完成")
    
    def _run_detection(self):
        """执行检测任务"""
        # 这里可以集成实际的检测逻辑
        # 目前只是占位
        pass
    
    def _rotate_logs(self):
        """日志轮转"""
        logger.info("📝 日志轮转...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rotated_file = LOG_DIR / f"lingshun_daemon_{timestamp}.log"
        
        try:
            LOG_FILE.rename(rotated_file)
            logger.info(f"  轮转：{rotated_file}")
            
            # 压缩旧日志
            import gzip
            with open(rotated_file, 'rb') as f_in:
                with gzip.open(f"{rotated_file}.gz", 'wb') as f_out:
                    f_out.writelines(f_in)
            
            rotated_file.unlink()  # 删除未压缩文件
            logger.info(f"  压缩：{rotated_file}.gz")
            
            # 清理旧日志（保留最近 7 个）
            old_logs = sorted(LOG_DIR.glob("lingshun_daemon_*.log.gz"))
            for old_log in old_logs[:-7]:
                old_log.unlink()
                logger.info(f"  清理：{old_log}")
        
        except Exception as e:
            logger.error(f"  日志轮转失败：{e}")
    
    def _cleanup(self):
        """清理资源"""
        logger.info("清理资源...")
        
        if PID_FILE.exists():
            PID_FILE.unlink()
        
        logger.info("守护进程已停止")

# ============== 管理命令 ==============

def start_daemon():
    """启动守护进程"""
    if PID_FILE.exists():
        with open(PID_FILE) as f:
            pid = int(f.read())
        
        # 检查进程是否运行
        try:
            os.kill(pid, 0)
            print(f"❌ 守护进程已在运行 (PID: {pid})")
            return False
        except ProcessLookupError:
            print(f"⚠️  检测到残留 PID 文件，清理中...")
            PID_FILE.unlink()
    
    daemon = LingshunDaemon()
    daemon.start()
    return True

def stop_daemon():
    """停止守护进程"""
    if not PID_FILE.exists():
        print("⚠️  守护进程未运行")
        return False
    
    with open(PID_FILE) as f:
        pid = int(f.read())
    
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"✅ 已发送停止信号 (PID: {pid})")
        
        # 等待进程退出
        for _ in range(10):
            time.sleep(1)
            if not PID_FILE.exists():
                print("✅ 守护进程已停止")
                return True
        
        # 强制停止
        os.kill(pid, signal.SIGKILL)
        PID_FILE.unlink()
        print("⚠️  强制停止守护进程")
        return True
    
    except ProcessLookupError:
        print("⚠️  进程不存在，清理 PID 文件")
        PID_FILE.unlink()
        return False

def status_daemon():
    """查看状态"""
    if not PID_FILE.exists():
        print("❌ 守护进程未运行")
        return False
    
    with open(PID_FILE) as f:
        pid = int(f.read())
    
    try:
        os.kill(pid, 0)
        print(f"✅ 守护进程运行中 (PID: {pid})")
        
        # 显示日志最后 10 行
        if LOG_FILE.exists():
            print(f"\n📝 最近日志:")
            with open(LOG_FILE) as f:
                lines = f.readlines()[-10:]
                for line in lines:
                    print(f"  {line.strip()}")
        
        return True
    
    except ProcessLookupError:
        print(f"⚠️  进程不存在 (残留 PID: {pid})")
        PID_FILE.unlink()
        return False

# ============== 主函数 ==============

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='灵顺守护进程管理')
    parser.add_argument('command', choices=['start', 'stop', 'restart', 'status', 'run'],
                       help='管理命令')
    
    args = parser.parse_args()
    
    if args.command == 'start':
        # 后台启动
        if os.fork() == 0:
            os.setsid()
            if os.fork() == 0:
                start_daemon()
            os._exit(0)
        print("✅ 守护进程已启动")
    
    elif args.command == 'stop':
        stop_daemon()
    
    elif args.command == 'restart':
        stop_daemon()
        time.sleep(2)
        if os.fork() == 0:
            os.setsid()
            if os.fork() == 0:
                start_daemon()
            os._exit(0)
        print("✅ 守护进程已重启")
    
    elif args.command == 'status':
        status_daemon()
    
    elif args.command == 'run':
        # 前台运行（调试用）
        daemon = LingshunDaemon()
        daemon.start()

if __name__ == '__main__':
    main()
