"""
Agent Security Multi-Agent System - Agent 基类
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Task:
    """任务定义"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = "general"
    status: str = "pending"  # pending, running, completed, failed
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    parameters: Dict = field(default_factory=dict)
    results: List[Any] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class Result:
    """结果定义"""
    task_id: str
    agent_id: str
    success: bool
    data: Any = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metrics: Dict = field(default_factory=dict)


class BaseAgent(ABC):
    """Agent 基类"""
    
    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict] = None):
        self.agent_id = agent_id or f"{self.__class__.__name__}-{uuid.uuid4().hex[:8]}"
        self.config = config or {}
        self.status = "idle"  # idle, busy, error
        self.current_task: Optional[Task] = None
        self.completed_tasks = 0
        self.failed_tasks = 0
    
    @abstractmethod
    def execute(self, task: Task) -> Result:
        """执行任务 - 子类必须实现"""
        pass
    
    def can_handle(self, task_type: str) -> bool:
        """检查是否能处理该类型任务"""
        return task_type in getattr(self, 'supported_types', [])
    
    def update_status(self, status: str):
        """更新状态"""
        self.status = status
        self._publish_status()
    
    def _publish_status(self):
        """发布状态到消息总线"""
        # 子类可以实现具体的发布逻辑
        pass
    
    def _log(self, level: str, message: str):
        """日志记录"""
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] [{level}] [{self.agent_id}] {message}")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            'agent_id': self.agent_id,
            'status': self.status,
            'completed_tasks': self.completed_tasks,
            'failed_tasks': self.failed_tasks,
            'current_task': self.current_task.id if self.current_task else None,
        }
