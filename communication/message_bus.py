"""
通信模块 - Agent 间消息总线

使用 Redis 发布/订阅模式实现 Agent 间通信
"""

import json
import asyncio
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid


class MessageType(Enum):
    """消息类型"""
    TASK = "task"
    RESULT = "result"
    STATUS = "status"
    ERROR = "error"
    CONTROL = "control"


@dataclass
class Message:
    """消息结构"""
    id: str
    type: MessageType
    source: str
    target: str
    payload: Dict[str, Any]
    timestamp: float
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'type': self.type.value,
            'source': self.source,
            'target': self.target,
            'payload': self.payload,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        return cls(
            id=data['id'],
            type=MessageType(data['type']),
            source=data['source'],
            target=data['target'],
            payload=data['payload'],
            timestamp=data['timestamp']
        )


class MessageBus:
    """消息总线 - 基于 Redis Pub/Sub"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        self.pubsub = None
        self._running = False
        self._subscribers: Dict[str, list] = {}
    
    async def connect(self):
        """连接到 Redis"""
        try:
            import redis.asyncio as redis
            self.redis = redis.from_url(self.redis_url, decode_responses=True)
            self.pubsub = self.redis.pubsub()
            self._running = True
            print(f"✅ 消息总线已连接：{self.redis_url}")
        except ImportError:
            print("⚠️ Redis 未安装，使用内存模式")
            self._use_memory = True
        except Exception as e:
            print(f"⚠️ Redis 连接失败，使用内存模式：{e}")
            self._use_memory = True
    
    async def disconnect(self):
        """断开连接"""
        self._running = False
        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()
        if self.redis:
            await self.redis.close()
    
    async def publish(self, channel: str, message: Message):
        """发布消息"""
        if hasattr(self, '_use_memory') and self._use_memory:
            # 内存模式
            if channel in self._subscribers:
                for callback in self._subscribers[channel]:
                    await callback(message)
        else:
            # Redis 模式
            await self.redis.publish(channel, json.dumps(message.to_dict()))
    
    async def subscribe(self, channel: str, callback: Callable):
        """订阅频道"""
        if hasattr(self, '_use_memory') and self._use_memory:
            # 内存模式
            if channel not in self._subscribers:
                self._subscribers[channel] = []
            self._subscribers[channel].append(callback)
        else:
            # Redis 模式
            await self.pubsub.subscribe(channel)
            asyncio.create_task(self._listen(channel, callback))
    
    async def _listen(self, channel: str, callback: Callable):
        """监听消息"""
        async for message in self.pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                msg = Message.from_dict(data)
                await callback(msg)
    
    def create_message(self, msg_type: MessageType, source: str, target: str, 
                      payload: Dict[str, Any]) -> Message:
        """创建消息"""
        import time
        return Message(
            id=str(uuid.uuid4()),
            type=msg_type,
            source=source,
            target=target,
            payload=payload,
            timestamp=time.time()
        )


class SharedState:
    """共享状态 - 基于 SQLite"""
    
    def __init__(self, db_path: str = "./data/shared_state.db"):
        self.db_path = db_path
        self._conn = None
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        import sqlite3
        import os
        
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.execute('''
            CREATE TABLE IF NOT EXISTS state (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at REAL
            )
        ''')
        self._conn.commit()
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取状态"""
        import json
        cursor = self._conn.execute(
            "SELECT value FROM state WHERE key = ?", (key,)
        )
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return default
    
    def set(self, key: str, value: Any):
        """设置状态"""
        import json
        import time
        self._conn.execute(
            "INSERT OR REPLACE INTO state (key, value, updated_at) VALUES (?, ?, ?)",
            (key, json.dumps(value), time.time())
        )
        self._conn.commit()
    
    def delete(self, key: str):
        """删除状态"""
        self._conn.execute("DELETE FROM state WHERE key = ?", (key,))
        self._conn.commit()
    
    def clear(self):
        """清空所有状态"""
        self._conn.execute("DELETE FROM state")
        self._conn.commit()
    
    def close(self):
        """关闭连接"""
        if self._conn:
            self._conn.close()
