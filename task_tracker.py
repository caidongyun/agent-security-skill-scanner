#!/usr/bin/env python3
"""
任务跟踪系统
跟踪任务进度，管理待办事项
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"       # 待办
    IN_PROGRESS = "in_progress"  # 进行中
    BLOCKED = "blocked"       # 被阻塞
    REVIEW = "review"         # 审查中
    COMPLETED = "completed"   # 已完成
    CANCELLED = "cancelled"   # 已取消


class Priority(Enum):
    """优先级"""
    P0 = "P0"  # 紧急
    P1 = "P1"  # 高优
    P2 = "P2"  # 普通
    P3 = "P3"  # 低优


@dataclass
class Task:
    """任务定义"""
    id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority = Priority.P2
    assignee: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    due_date: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # 依赖的任务 ID
    subtasks: List[str] = field(default_factory=list)  # 子任务 ID
    progress: float = 0.0  # 进度 0-100%
    notes: str = ""
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status.value,
            'priority': self.priority.value,
            'assignee': self.assignee,
            'created_at': self.created_at,
            'due_date': self.due_date,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'tags': self.tags,
            'dependencies': self.dependencies,
            'subtasks': self.subtasks,
            'progress': self.progress,
            'notes': self.notes,
        }


class TaskTracker:
    """任务跟踪器"""
    
    def __init__(self, storage_file: str = "logs/task_tracker.json"):
        self.storage_file = Path(storage_file)
        self.tasks: Dict[str, Task] = {}
        self.load()
    
    def load(self):
        """加载任务"""
        if self.storage_file.exists():
            with open(self.storage_file) as f:
                data = json.load(f)
                for task_id, task_data in data.get('tasks', {}).items():
                    task = Task(
                        id=task_data['id'],
                        title=task_data['title'],
                        description=task_data['description'],
                        status=TaskStatus(task_data['status']),
                        priority=Priority(task_data['priority']),
                        assignee=task_data.get('assignee'),
                        created_at=task_data.get('created_at'),
                        due_date=task_data.get('due_date'),
                        started_at=task_data.get('started_at'),
                        completed_at=task_data.get('completed_at'),
                        tags=task_data.get('tags', []),
                        dependencies=task_data.get('dependencies', []),
                        subtasks=task_data.get('subtasks', []),
                        progress=task_data.get('progress', 0.0),
                        notes=task_data.get('notes', ''),
                    )
                    self.tasks[task_id] = task
            print(f"✅ 已加载 {len(self.tasks)} 个任务")
    
    def save(self):
        """保存任务"""
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            'tasks': {task_id: task.to_dict() for task_id, task in self.tasks.items()},
            'updated_at': datetime.now().isoformat(),
        }
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_task(self, title: str, description: str, **kwargs) -> Task:
        """创建任务"""
        task_id = kwargs.pop('id', f"TASK-{len(self.tasks) + 1:03d}")
        task = Task(
            id=task_id,
            title=title,
            description=description,
            **kwargs
        )
        self.tasks[task_id] = task
        self.save()
        print(f"✅ 创建任务：{task_id} - {title}")
        return task
    
    def update_status(self, task_id: str, status: TaskStatus):
        """更新任务状态"""
        if task_id not in self.tasks:
            print(f"❌ 任务不存在：{task_id}")
            return
        
        task = self.tasks[task_id]
        old_status = task.status
        task.status = status
        
        # 自动设置时间
        if status == TaskStatus.IN_PROGRESS and old_status == TaskStatus.PENDING:
            task.started_at = datetime.now().isoformat()
        elif status == TaskStatus.COMPLETED:
            task.completed_at = datetime.now().isoformat()
            task.progress = 100.0
        
        self.save()
        print(f"📝 更新任务状态：{task_id} {old_status.value} → {status.value}")
    
    def update_progress(self, task_id: str, progress: float):
        """更新任务进度"""
        if task_id not in self.tasks:
            print(f"❌ 任务不存在：{task_id}")
            return
        
        task = self.tasks[task_id]
        task.progress = min(100.0, max(0.0, progress))
        self.save()
    
    def add_dependency(self, task_id: str, depends_on: str):
        """添加任务依赖"""
        if task_id not in self.tasks:
            print(f"❌ 任务不存在：{task_id}")
            return
        if depends_on not in self.tasks:
            print(f"❌ 依赖任务不存在：{depends_on}")
            return
        
        task = self.tasks[task_id]
        if depends_on not in task.dependencies:
            task.dependencies.append(depends_on)
            self.save()
            print(f"🔗 添加依赖：{task_id} 依赖于 {depends_on}")
    
    def can_start(self, task_id: str) -> bool:
        """检查任务是否可以开始 (依赖是否完成)"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                return False
            if self.tasks[dep_id].status != TaskStatus.COMPLETED:
                return False
        return True
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """按状态获取任务"""
        return [task for task in self.tasks.values() if task.status == status]
    
    def get_tasks_by_priority(self, priority: Priority) -> List[Task]:
        """按优先级获取任务"""
        return [task for task in self.tasks.values() if task.priority == priority]
    
    def get_blocked_tasks(self) -> List[Task]:
        """获取被阻塞的任务"""
        return [task for task in self.tasks.values() 
                if task.status == TaskStatus.IN_PROGRESS and not self.can_start(task.id)]
    
    def get_summary(self) -> Dict:
        """获取任务摘要"""
        summary = {
            'total': len(self.tasks),
            'by_status': {},
            'by_priority': {},
            'blocked': 0,
            'avg_progress': 0.0,
        }
        
        # 按状态统计
        for status in TaskStatus:
            count = len(self.get_tasks_by_status(status))
            summary['by_status'][status.value] = count
        
        # 按优先级统计
        for priority in Priority:
            count = len(self.get_tasks_by_priority(priority))
            summary['by_priority'][priority.value] = count
        
        # 被阻塞任务
        summary['blocked'] = len(self.get_blocked_tasks())
        
        # 平均进度
        if self.tasks:
            summary['avg_progress'] = sum(t.progress for t in self.tasks.values()) / len(self.tasks)
        
        return summary
    
    def print_dashboard(self):
        """打印任务看板"""
        print("\n" + "="*80)
        print("📋 任务跟踪看板")
        print("="*80)
        
        summary = self.get_summary()
        print(f"\n总任务数：{summary['total']}")
        print(f"平均进度：{summary['avg_progress']:.1f}%")
        print(f"被阻塞：{summary['blocked']} 个")
        
        print("\n按状态:")
        for status, count in summary['by_status'].items():
            bar = "█" * int(count / max(1, summary['total']) * 20)
            print(f"  {status:12} {count:3} {bar}")
        
        print("\n按优先级:")
        for priority, count in summary['by_priority'].items():
            bar = "█" * int(count / max(1, summary['total']) * 20)
            print(f"  {priority:12} {count:3} {bar}")
        
        # 显示进行中的任务
        in_progress = self.get_tasks_by_status(TaskStatus.IN_PROGRESS)
        if in_progress:
            print("\n进行中的任务:")
            for task in in_progress[:5]:
                print(f"  [{task.priority.value}] {task.id} - {task.title} ({task.progress:.0f}%)")
        
        # 显示被阻塞的任务
        blocked = self.get_blocked_tasks()
        if blocked:
            print("\n⚠️  被阻塞的任务:")
            for task in blocked:
                deps = ", ".join(task.dependencies)
                print(f"  [{task.priority.value}] {task.id} - {task.title} (依赖：{deps})")
        
        print("\n" + "="*80)


def init_lingshun_tasks() -> TaskTracker:
    """初始化灵顺融合版任务"""
    
    tracker = TaskTracker()
    
    # ===== 短期任务 (1-2 周) =====
    
    # P0 紧急任务
    tracker.create_task(
        id="P0-001",
        title="完成全量测试",
        description="完成 65,533 样本的全量测试，获取真实检测率",
        priority=Priority.P0,
        status=TaskStatus.IN_PROGRESS,
        progress=0.4,
        tags=['测试', '验证'],
        due_date="2026-04-03",
    )
    
    # P1 高优任务
    tracker.create_task(
        id="P1-001",
        title="集成 AST 分析",
        description="将 round16/ast_analyzer.py 集成到 fused_scanner_auto_rd.py",
        priority=Priority.P1,
        status=TaskStatus.PENDING,
        tags=['多层架构', 'AST'],
        due_date="2026-04-05",
        dependencies=["P0-001"],
    )
    
    tracker.create_task(
        id="P1-002",
        title="集成意图识别",
        description="创建 intent_analyzer.py 并集成",
        priority=Priority.P1,
        status=TaskStatus.PENDING,
        tags=['多层架构', '意图识别'],
        due_date="2026-04-06",
        dependencies=["P1-001"],
    )
    
    tracker.create_task(
        id="P1-003",
        title="集成控制流分析",
        description="创建 cfg_analyzer.py 并集成",
        priority=Priority.P1,
        status=TaskStatus.PENDING,
        tags=['多层架构', '控制流'],
        due_date="2026-04-07",
        dependencies=["P1-002"],
    )
    
    # P2 普通任务
    tracker.create_task(
        id="P2-001",
        title="实现 Agent 执行逻辑",
        description="为 8 大 Agent 模板实现真实的执行逻辑",
        priority=Priority.P2,
        status=TaskStatus.PENDING,
        tags=['Agent', '执行'],
        due_date="2026-04-10",
    )
    
    tracker.create_task(
        id="P2-002",
        title="集成质量门禁到 CI/CD",
        description="将质量门禁集成到提交流程，强制执行",
        priority=Priority.P2,
        status=TaskStatus.PENDING,
        tags=['质量', 'CI/CD'],
        due_date="2026-04-08",
    )
    
    tracker.create_task(
        id="P2-003",
        title="集成语义分析",
        description="创建 semantic_detector.py 并集成",
        priority=Priority.P2,
        status=TaskStatus.PENDING,
        tags=['多层架构', '语义分析'],
        due_date="2026-04-09",
    )
    
    # P3 低优任务
    tracker.create_task(
        id="P3-001",
        title="实现 LLM 分析",
        description="集成 LLM 进行深度分析",
        priority=Priority.P3,
        status=TaskStatus.PENDING,
        tags=['多层架构', 'LLM'],
        due_date="2026-04-15",
    )
    
    tracker.create_task(
        id="P3-002",
        title="实现自学习能力",
        description="从历史任务中学习，自动优化流程",
        priority=Priority.P3,
        status=TaskStatus.PENDING,
        tags=['自学习', '优化'],
        due_date="2026-04-20",
    )
    
    tracker.save()
    return tracker


def main():
    """主函数"""
    
    # 初始化任务
    print("="*80)
    print("🦸 灵顺融合版 v3.0 - 任务跟踪系统")
    print("="*80)
    
    tracker = init_lingshun_tasks()
    
    # 打印看板
    tracker.print_dashboard()
    
    # 演示任务更新
    print("\n" + "="*80)
    print("演示任务更新")
    print("="*80)
    
    # 更新全量测试进度
    tracker.update_progress("P0-001", 50.0)
    print(f"\n更新 P0-001 进度到 50%")
    
    # 完成全量测试
    # tracker.update_status("P0-001", TaskStatus.COMPLETED)
    # print("\n完成 P0-001 全量测试")
    
    # 打印更新后的看板
    tracker.print_dashboard()
    
    print("\n✅ 任务跟踪系统初始化完成")
    print(f"📁 任务文件：{tracker.storage_file}")


if __name__ == '__main__':
    main()
