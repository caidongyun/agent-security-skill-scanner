#!/usr/bin/env python3
"""
HE-002: 状态持久化
Checkpoint 机制，支持断点恢复
"""

import json
import pickle
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class Checkpoint:
    """Checkpoint 定义"""
    id: str
    task_id: str
    state: Dict[str, Any]
    created_at: str
    metadata: Dict = None
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'task_id': self.task_id,
            'state': self.state,
            'created_at': self.created_at,
            'metadata': self.metadata or {},
        }


class Checkpointer:
    """状态持久化管理器"""
    
    def __init__(self, storage_path: str = "checkpoints.db"):
        self.storage_path = Path(storage_path)
        self.conn: Optional[sqlite3.Connection] = None
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        self.conn = sqlite3.connect(str(self.storage_path))
        cursor = self.conn.cursor()
        
        # 创建 checkpoints 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checkpoints (
                id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                state TEXT NOT NULL,
                created_at TEXT NOT NULL,
                metadata TEXT
            )
        ''')
        
        # 创建索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_task_id
            ON checkpoints(task_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_created_at
            ON checkpoints(created_at)
        ''')
        
        self.conn.commit()
    
    def save_checkpoint(self, checkpoint: Checkpoint) -> bool:
        """保存 checkpoint"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO checkpoints
                (id, task_id, state, created_at, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                checkpoint.id,
                checkpoint.task_id,
                json.dumps(checkpoint.state),
                checkpoint.created_at,
                json.dumps(checkpoint.metadata or {}),
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ 保存 checkpoint 失败：{e}")
            return False
    
    def load_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """加载 checkpoint"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT id, task_id, state, created_at, metadata
                FROM checkpoints
                WHERE id = ?
            ''', (checkpoint_id,))
            
            row = cursor.fetchone()
            if row:
                return Checkpoint(
                    id=row[0],
                    task_id=row[1],
                    state=json.loads(row[2]),
                    created_at=row[3],
                    metadata=json.loads(row[4]) if row[4] else None,
                )
            return None
        except Exception as e:
            print(f"❌ 加载 checkpoint 失败：{e}")
            return None
    
    def get_latest_checkpoint(self, task_id: str) -> Optional[Checkpoint]:
        """获取最新 checkpoint"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT id, task_id, state, created_at, metadata
                FROM checkpoints
                WHERE task_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            ''', (task_id,))
            
            row = cursor.fetchone()
            if row:
                return Checkpoint(
                    id=row[0],
                    task_id=row[1],
                    state=json.loads(row[2]),
                    created_at=row[3],
                    metadata=json.loads(row[4]) if row[4] else None,
                )
            return None
        except Exception as e:
            print(f"❌ 获取最新 checkpoint 失败：{e}")
            return None
    
    def list_checkpoints(self, task_id: Optional[str] = None) -> list:
        """列出 checkpoints"""
        try:
            cursor = self.conn.cursor()
            if task_id:
                cursor.execute('''
                    SELECT id, task_id, created_at
                    FROM checkpoints
                    WHERE task_id = ?
                    ORDER BY created_at DESC
                ''', (task_id,))
            else:
                cursor.execute('''
                    SELECT id, task_id, created_at
                    FROM checkpoints
                    ORDER BY created_at DESC
                ''')
            
            return [
                {'id': row[0], 'task_id': row[1], 'created_at': row[2]}
                for row in cursor.fetchall()
            ]
        except Exception as e:
            print(f"❌ 列出 checkpoints 失败：{e}")
            return []
    
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """删除 checkpoint"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                DELETE FROM checkpoints
                WHERE id = ?
            ''', (checkpoint_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ 删除 checkpoint 失败：{e}")
            return False
    
    def cleanup_old_checkpoints(self, days: int = 7) -> int:
        """清理旧 checkpoints"""
        try:
            cursor = self.conn.cursor()
            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            cursor.execute('''
                DELETE FROM checkpoints
                WHERE datetime(created_at) < datetime(?)
            ''', (cutoff_date,))
            self.conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ 清理旧 checkpoints 失败：{e}")
            return 0
    
    def close(self):
        """关闭数据库"""
        if self.conn:
            self.conn.close()


class StateManager:
    """状态管理器 (高级封装)"""
    
    def __init__(self, checkpointer: Checkpointer):
        self.checkpointer = checkpointer
        self.current_state: Dict[str, Any] = {}
        self.checkpoint_counter = 0
    
    def update_state(self, key: str, value: Any):
        """更新状态"""
        self.current_state[key] = value
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """获取状态"""
        return self.current_state.get(key, default)
    
    def save_state(self, task_id: str, metadata: Dict = None) -> str:
        """保存状态"""
        self.checkpoint_counter += 1
        checkpoint = Checkpoint(
            id=f"{task_id}_{self.checkpoint_counter}",
            task_id=task_id,
            state=self.current_state,
            created_at=datetime.now().isoformat(),
            metadata=metadata,
        )
        
        if self.checkpointer.save_checkpoint(checkpoint):
            return checkpoint.id
        return None
    
    def restore_state(self, task_id: str) -> bool:
        """恢复状态"""
        checkpoint = self.checkpointer.get_latest_checkpoint(task_id)
        if checkpoint:
            self.current_state = checkpoint.state
            return True
        return False
    
    def clear_state(self):
        """清空状态"""
        self.current_state = {}
        self.checkpoint_counter = 0


def main():
    """主函数 - 演示"""
    print("="*60)
    print("HE-002: 状态持久化演示")
    print("="*60)
    
    # 初始化
    checkpointer = Checkpointer("demo_checkpoints.db")
    state_manager = StateManager(checkpointer)
    
    # 更新状态
    print("\n1. 更新状态...")
    state_manager.update_state("progress", 0.5)
    state_manager.update_state("current_task", "task_1")
    state_manager.update_state("data", {"key": "value"})
    
    print(f"   当前状态：{state_manager.current_state}")
    
    # 保存状态
    print("\n2. 保存状态...")
    checkpoint_id = state_manager.save_state("demo_task")
    print(f"   Checkpoint ID: {checkpoint_id}")
    
    # 清空状态
    print("\n3. 清空状态...")
    state_manager.clear_state()
    print(f"   清空后状态：{state_manager.current_state}")
    
    # 恢复状态
    print("\n4. 恢复状态...")
    if state_manager.restore_state("demo_task"):
        print(f"   恢复后状态：{state_manager.current_state}")
    else:
        print("   ❌ 恢复失败")
    
    # 列出 checkpoints
    print("\n5. 列出 Checkpoints...")
    checkpoints = checkpointer.list_checkpoints()
    for cp in checkpoints:
        print(f"   - {cp['id']} (任务：{cp['task_id']}, 时间：{cp['created_at']})")
    
    # 清理
    checkpointer.close()
    Path("demo_checkpoints.db").unlink(missing_ok=True)
    
    print("\n" + "="*60)
    print("✅ HE-002 状态持久化演示完成")
    print("="*60)


if __name__ == '__main__':
    main()
