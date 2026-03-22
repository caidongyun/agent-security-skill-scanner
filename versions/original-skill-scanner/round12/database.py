#!/usr/bin/env python3
"""
Round 12 - 数据库模块

存储检测事件、告警记录、规则版本等
"""

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

# ============== 配置 ==============

BASE_DIR = Path(__file__).parent.parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATABASE_DIR / "security.db"

# ============== 数据库初始化 ==============

def init_database(db_path: Optional[Path] = None):
    """初始化数据库"""
    if db_path is None:
        db_path = DB_PATH
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # 创建检测事件表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detection_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_hash TEXT,
            file_size INTEGER,
            attack_type TEXT,
            severity TEXT,
            rule_id TEXT,
            rule_name TEXT,
            confidence REAL,
            action TEXT,
            status TEXT DEFAULT 'new',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建告警记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            timestamp TEXT NOT NULL,
            level TEXT NOT NULL,
            channel TEXT,
            status TEXT DEFAULT 'pending',
            sent_at TEXT,
            acknowledged_at TEXT,
            acknowledged_by TEXT,
            message TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES detection_events(id)
        )
    """)
    
    # 创建规则版本表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rule_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT NOT NULL UNIQUE,
            rule_count INTEGER,
            l1_count INTEGER,
            l2_count INTEGER,
            l3_count INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            changelog TEXT,
            is_active INTEGER DEFAULT 0
        )
    """)
    
    # 创建监控目录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watch_directories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL UNIQUE,
            enabled INTEGER DEFAULT 1,
            recursive INTEGER DEFAULT 0,
            exclude_patterns TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建通知配置表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notification_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel TEXT NOT NULL UNIQUE,
            enabled INTEGER DEFAULT 0,
            config TEXT,
            last_test_at TEXT,
            last_test_status TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建统计缓存表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stats_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            metric_value TEXT,
            period TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON detection_events(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_severity ON detection_events(severity)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_attack_type ON detection_events(attack_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status)")
    
    conn.commit()
    conn.close()
    
    print(f"✅ 数据库初始化完成：{db_path}")
    return db_path

# ============== 数据模型 ==============

class DetectionEvent:
    """检测事件"""
    
    def __init__(self, file_path: str, attack_type: str, severity: str,
                 rule_id: str, rule_name: str, confidence: float = 0.0,
                 file_hash: Optional[str] = None, file_size: Optional[int] = None):
        self.file_path = file_path
        self.file_hash = file_hash
        self.file_size = file_size
        self.attack_type = attack_type
        self.severity = severity
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.confidence = confidence
        self.timestamp = datetime.now().isoformat()
        self.status = 'new'
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp,
            'file_path': self.file_path,
            'file_hash': self.file_hash,
            'file_size': self.file_size,
            'attack_type': self.attack_type,
            'severity': self.severity,
            'rule_id': self.rule_id,
            'rule_name': self.rule_name,
            'confidence': self.confidence,
            'status': self.status,
        }
    
    def save(self, db_path: Optional[Path] = None) -> int:
        """保存到数据库"""
        if db_path is None:
            db_path = DB_PATH
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO detection_events 
            (timestamp, file_path, file_hash, file_size, attack_type, severity, 
             rule_id, rule_name, confidence, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.timestamp, self.file_path, self.file_hash, self.file_size,
            self.attack_type, self.severity, self.rule_id, self.rule_name,
            self.confidence, self.status
        ))
        
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return event_id

class Alert:
    """告警记录"""
    
    def __init__(self, event_id: int, level: str, channel: str, message: str):
        self.event_id = event_id
        self.level = level
        self.channel = channel
        self.message = message
        self.timestamp = datetime.now().isoformat()
        self.status = 'pending'
    
    def save(self, db_path: Optional[Path] = None) -> int:
        """保存到数据库"""
        if db_path is None:
            db_path = DB_PATH
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO alerts 
            (event_id, timestamp, level, channel, status, message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            self.event_id, self.timestamp, self.level, 
            self.channel, self.status, self.message
        ))
        
        alert_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return alert_id

# ============== 查询操作 ==============

class DatabaseQuery:
    """数据库查询"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
    
    def get_recent_events(self, limit: int = 100) -> List[Dict]:
        """获取最近的检测事件"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM detection_events 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        events = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return events
    
    def get_alerts(self, status: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """获取告警记录"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if status:
            cursor.execute("""
                SELECT * FROM alerts 
                WHERE status = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (status, limit))
        else:
            cursor.execute("""
                SELECT * FROM alerts 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
        
        alerts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return alerts
    
    def get_stats(self, period: str = '24h') -> Dict:
        """获取统计数据"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 计算时间范围
        now = datetime.now()
        if period == '24h':
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == '7d':
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            start_time = start_time.replace(day=start_time.day - 7)
        else:
            start_time = now
        
        start_str = start_time.isoformat()
        
        # 总事件数
        cursor.execute("""
            SELECT COUNT(*) as count FROM detection_events 
            WHERE timestamp >= ?
        """, (start_str,))
        total_events = cursor.fetchone()['count']
        
        # 按严重程度统计
        cursor.execute("""
            SELECT severity, COUNT(*) as count FROM detection_events 
            WHERE timestamp >= ?
            GROUP BY severity
        """, (start_str,))
        by_severity = {row['severity']: row['count'] for row in cursor.fetchall()}
        
        # 按攻击类型统计
        cursor.execute("""
            SELECT attack_type, COUNT(*) as count FROM detection_events 
            WHERE timestamp >= ?
            GROUP BY attack_type
        """, (start_str,))
        by_attack_type = {row['attack_type']: row['count'] for row in cursor.fetchall()}
        
        # 告警统计
        cursor.execute("""
            SELECT status, COUNT(*) as count FROM alerts 
            WHERE timestamp >= ?
            GROUP BY status
        """, (start_str,))
        alerts_by_status = {row['status']: row['count'] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'period': period,
            'total_events': total_events,
            'by_severity': by_severity,
            'by_attack_type': by_attack_type,
            'alerts_by_status': alerts_by_status,
        }
    
    def update_alert_status(self, alert_id: int, status: str, acknowledged_by: Optional[str] = None):
        """更新告警状态"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        if status == 'acknowledged':
            cursor.execute("""
                UPDATE alerts 
                SET status = ?, acknowledged_at = ?, acknowledged_by = ?
                WHERE id = ?
            """, (status, datetime.now().isoformat(), acknowledged_by, alert_id))
        else:
            cursor.execute("""
                UPDATE alerts 
                SET status = ?
                WHERE id = ?
            """, (status, alert_id))
        
        conn.commit()
        conn.close()

# ============== 主函数 ==============

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Round 12 数据库模块")
    parser.add_argument('--init', action='store_true', help='初始化数据库')
    parser.add_argument('--test', action='store_true', help='测试数据库')
    parser.add_argument('--db-path', type=str, help='数据库路径')
    
    args = parser.parse_args()
    
    db_path = Path(args.db_path) if args.db_path else DB_PATH
    
    if args.init:
        init_database(db_path)
    
    if args.test:
        print("🧪 测试数据库...")
        
        # 初始化
        init_database(db_path)
        
        # 插入测试数据
        event = DetectionEvent(
            file_path="/tmp/test_malware.py",
            attack_type="remote_load",
            severity="high",
            rule_id="RULE-TEST-001",
            rule_name="测试规则",
            confidence=0.95,
            file_hash="abc123",
            file_size=1024
        )
        event_id = event.save(db_path)
        print(f"  ✅ 插入测试事件：ID={event_id}")
        
        # 插入测试告警
        alert = Alert(
            event_id=event_id,
            level="P1",
            channel="feishu",
            message="测试告警"
        )
        alert_id = alert.save(db_path)
        print(f"  ✅ 插入测试告警：ID={alert_id}")
        
        # 查询测试
        query = DatabaseQuery(db_path)
        events = query.get_recent_events(limit=10)
        print(f"  ✅ 查询最近事件：{len(events)} 条")
        
        stats = query.get_stats(period='24h')
        print(f"  ✅ 统计数据：{stats}")
        
        print("\n✅ 数据库测试完成")

if __name__ == "__main__":
    main()
