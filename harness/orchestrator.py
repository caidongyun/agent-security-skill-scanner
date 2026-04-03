#!/usr/bin/env python3
"""
HE-001: 任务编排引擎
基于 LangGraph 实现 DAG/状态机任务编排
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("⚠️  LangGraph 未安装，使用简化版任务编排")


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """任务定义"""
    id: str
    name: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 1  # 1-5, 5 最高
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    result: Optional[Any] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'priority': self.priority,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'error': self.error,
            'result': self.result,
            'dependencies': self.dependencies,
            'metadata': self.metadata,
        }


@dataclass
class TaskState:
    """任务状态 (用于 LangGraph)"""
    tasks: Dict[str, Task] = field(default_factory=dict)
    current_task: Optional[str] = None
    completed_tasks: List[str] = field(default_factory=list)
    failed_tasks: List[str] = field(default_factory=list)
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class TaskOrchestrator:
    """任务编排器"""
    
    def __init__(self, use_langgraph: bool = True):
        self.use_langgraph = use_langgraph and LANGGRAPH_AVAILABLE
        self.tasks: Dict[str, Task] = {}
        self.task_handlers: Dict[str, Callable] = {}
        self.state: Optional[TaskState] = None
        
        if self.use_langgraph:
            self._init_langgraph()
        else:
            self._init_simple()
    
    def _init_langgraph(self):
        """初始化 LangGraph 编排"""
        self.workflow = StateGraph(TaskState)
        
        # 添加节点
        self.workflow.add_node("start", self._start_task)
        self.workflow.add_node("execute", self._execute_task)
        self.workflow.add_node("check_deps", self._check_dependencies)
        self.workflow.add_node("complete", self._complete_task)
        self.workflow.add_node("fail", self._fail_task)
        
        # 设置入口
        self.workflow.set_entry_point("start")
        
        # 添加边
        self.workflow.add_edge("start", "check_deps")
        self.workflow.add_conditional_edges(
            "check_deps",
            self._deps_ready,
            {
                "ready": "execute",
                "waiting": "start",
            }
        )
        self.workflow.add_conditional_edges(
            "execute",
            self._task_result,
            {
                "success": "complete",
                "failure": "fail",
            }
        )
        self.workflow.add_edge("complete", "check_deps")
        self.workflow.add_edge("fail", "check_deps")
        
        # 编译
        self.app = self.workflow.compile()
    
    def _init_simple(self):
        """初始化简化版编排"""
        pass
    
    def register_task(self, task: Task, handler: Callable):
        """注册任务"""
        self.tasks[task.id] = task
        self.task_handlers[task.id] = handler
    
    def submit_task(self, task_id: str, name: str, description: str,
                   handler: Callable, dependencies: List[str] = None,
                   priority: int = 1, metadata: Dict = None) -> Task:
        """提交任务"""
        task = Task(
            id=task_id,
            name=name,
            description=description,
            dependencies=dependencies or [],
            priority=priority,
            metadata=metadata or {},
        )
        self.register_task(task, handler)
        return task
    
    def _start_task(self, state: TaskState) -> TaskState:
        """开始任务"""
        if state.start_time is None:
            state.start_time = datetime.now().isoformat()
        
        # 找到下一个待执行任务
        pending_tasks = [
            t for t in state.tasks.values()
            if t.status == TaskStatus.PENDING
        ]
        
        if not pending_tasks:
            state.end_time = datetime.now().isoformat()
            return state
        
        # 按优先级排序
        pending_tasks.sort(key=lambda t: -t.priority)
        next_task = pending_tasks[0]
        
        next_task.status = TaskStatus.RUNNING
        next_task.started_at = datetime.now().isoformat()
        state.current_task = next_task.id
        
        return state
    
    def _check_dependencies(self, state: TaskState) -> TaskState:
        """检查依赖"""
        if state.current_task is None:
            return state
        
        task = state.tasks[state.current_task]
        
        for dep_id in task.dependencies:
            if dep_id not in state.completed_tasks:
                return state
        
        return state
    
    def _deps_ready(self, state: TaskState) -> str:
        """依赖是否就绪"""
        if state.current_task is None:
            return "waiting"
        
        task = state.tasks[state.current_task]
        for dep_id in task.dependencies:
            if dep_id not in state.completed_tasks:
                return "waiting"
        
        return "ready"
    
    def _execute_task(self, state: TaskState) -> TaskState:
        """执行任务"""
        if state.current_task is None:
            return state
        
        task_id = state.current_task
        task = state.tasks[task_id]
        handler = self.task_handlers.get(task_id)
        
        if handler is None:
            task.error = f"No handler for task {task_id}"
            return state
        
        try:
            result = handler(task)
            task.result = result
        except Exception as e:
            task.error = str(e)
        
        return state
    
    def _task_result(self, state: TaskState) -> str:
        """任务结果"""
        if state.current_task is None:
            return "waiting"
        
        task = state.tasks[state.current_task]
        if task.error:
            return "failure"
        return "success"
    
    def _complete_task(self, state: TaskState) -> TaskState:
        """完成任务"""
        if state.current_task is None:
            return state
        
        task = state.tasks[state.current_task]
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now().isoformat()
        
        state.completed_tasks.append(task.id)
        state.current_task = None
        
        return state
    
    def _fail_task(self, state: TaskState) -> TaskState:
        """失败任务"""
        if state.current_task is None:
            return state
        
        task = state.tasks[state.current_task]
        task.status = TaskStatus.FAILED
        task.completed_at = datetime.now().isoformat()
        
        state.failed_tasks.append(task.id)
        state.current_task = None
        
        return state
    
    def run(self) -> Dict:
        """运行任务编排"""
        if self.use_langgraph:
            return self._run_langgraph()
        else:
            return self._run_simple()
    
    def _run_langgraph(self) -> Dict:
        """LangGraph 运行"""
        state = TaskState(tasks=self.tasks)
        final_state = self.app.invoke(state)
        
        return {
            'completed': final_state.completed_tasks,
            'failed': final_state.failed_tasks,
            'start_time': final_state.start_time,
            'end_time': final_state.end_time,
        }
    
    def _run_simple(self) -> Dict:
        """简化版运行"""
        completed = []
        failed = []
        start_time = datetime.now().isoformat()
        
        # 拓扑排序执行
        remaining = set(self.tasks.keys())
        in_progress = set()
        
        while remaining or in_progress:
            # 找到可执行的任务
            ready = []
            for task_id in list(remaining):
                task = self.tasks[task_id]
                deps_met = all(d in completed for d in task.dependencies)
                if deps_met and task_id not in in_progress:
                    ready.append(task_id)
            
            if not ready and not in_progress:
                # 死锁
                break
            
            # 执行就绪任务
            for task_id in ready:
                task = self.tasks[task_id]
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now().isoformat()
                in_progress.add(task_id)
                remaining.discard(task_id)
                
                # 执行
                handler = self.task_handlers.get(task_id)
                try:
                    if handler:
                        handler(task)
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = datetime.now().isoformat()
                    completed.append(task_id)
                except Exception as e:
                    task.status = TaskStatus.FAILED
                    task.error = str(e)
                    task.completed_at = datetime.now().isoformat()
                    failed.append(task_id)
                
                in_progress.discard(task_id)
        
        end_time = datetime.now().isoformat()
        
        return {
            'completed': completed,
            'failed': failed,
            'start_time': start_time,
            'end_time': end_time,
        }
    
    def get_status(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        task = self.tasks.get(task_id)
        if task:
            return task.to_dict()
        return None
    
    def get_all_status(self) -> Dict:
        """获取所有任务状态"""
        return {
            task_id: task.to_dict()
            for task_id, task in self.tasks.items()
        }


# 示例用法
def example_handler(task: Task) -> str:
    """示例任务处理器"""
    print(f"Executing task: {task.name}")
    time.sleep(1)
    return f"Completed {task.name}"


def main():
    """主函数 - 演示"""
    print("="*60)
    print("HE-001: 任务编排引擎演示")
    print("="*60)
    
    orchestrator = TaskOrchestrator(use_langgraph=False)
    
    # 注册任务
    orchestrator.submit_task(
        task_id="task1",
        name="任务 1",
        description="无依赖任务",
        handler=example_handler,
        priority=3,
    )
    
    orchestrator.submit_task(
        task_id="task2",
        name="任务 2",
        description="依赖任务 1",
        handler=example_handler,
        dependencies=["task1"],
        priority=2,
    )
    
    orchestrator.submit_task(
        task_id="task3",
        name="任务 3",
        description="依赖任务 1",
        handler=example_handler,
        dependencies=["task1"],
        priority=1,
    )
    
    orchestrator.submit_task(
        task_id="task4",
        name="任务 4",
        description="依赖任务 2 和 3",
        handler=example_handler,
        dependencies=["task2", "task3"],
        priority=5,
    )
    
    # 运行
    print("\n开始执行任务...")
    result = orchestrator.run()
    
    print(f"\n执行结果:")
    print(f"  完成：{result['completed']}")
    print(f"  失败：{result['failed']}")
    print(f"  开始：{result['start_time']}")
    print(f"  结束：{result['end_time']}")
    
    print("\n" + "="*60)
    print("✅ HE-001 任务编排引擎演示完成")
    print("="*60)


if __name__ == '__main__':
    main()
