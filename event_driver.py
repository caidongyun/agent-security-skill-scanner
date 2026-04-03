#!/usr/bin/env python3
"""
🎯 P2 事件驱动架构核心引擎
Event-Driven Architecture Engine

功能:
1. 事件总线 (Event Bus)
2. 智能触发器 (Smart Triggers)
3. 事件路由 (Event Routing)
4. 优先级调度 (Priority Scheduling)
5. 实时监控 (Real-time Monitoring)
"""

import json
import asyncio
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict
import threading

WORKSPACE = Path('/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master')

class EventType(Enum):
    """事件类型"""
    THREAT_INTEL_NEW = "threat_intel_new"  # 新威胁情报
    DETECTION_RATE_DROP = "detection_rate_drop"  # 检测率下降
    RULE_COMMIT = "rule_commit"  # 新规则提交
    SCHEDULED_EVAL = "scheduled_eval"  # 定时评估
    EMERGENCY_OPTIMIZE = "emergency_optimize"  # 紧急优化
    BENCHMARK_COMPLETE = "benchmark_complete"  # 基准测试完成

class Priority(Enum):
    """事件优先级"""
    CRITICAL = 1  # 紧急 (检测率<90%)
    HIGH = 2  # 高 (检测率<95%)
    MEDIUM = 3  # 中 (定期评估)
    LOW = 4  # 低 (情报采集)

@dataclass
class Event:
    """事件对象"""
    id: str
    type: EventType
    priority: Priority
    timestamp: str
    data: Dict
    source: str
    handled: bool = False

class EventBus:
    """事件总线"""
    
    def __init__(self):
        self.subscribers: Dict[EventType, List[Callable]] = defaultdict(list)
        self.event_queue: List[Event] = []
        self.history: List[Event] = []
        self.lock = threading.Lock()
        
        # 统计
        self.stats = {
            'total_events': 0,
            'handled_events': 0,
            'pending_events': 0
        }
    
    def subscribe(self, event_type: EventType, handler: Callable):
        """订阅事件
        
        Args:
            event_type: 事件类型
            handler: 处理函数
        """
        self.subscribers[event_type].append(handler)
        print(f"  📬 订阅事件：{event_type.value}")
    
    def publish(self, event: Event):
        """发布事件
        
        Args:
            event: 事件对象
        """
        with self.lock:
            self.event_queue.append(event)
            self.stats['total_events'] += 1
            self.stats['pending_events'] += 1
        
        print(f"\n🔔 发布事件：{event.type.value} (优先级：{event.priority.name})")
        
        # 异步处理
        asyncio.create_task(self._handle_event(event))
    
    async def _handle_event(self, event: Event):
        """处理事件
        
        Args:
            event: 事件对象
        """
        handlers = self.subscribers.get(event.type, [])
        
        if not handlers:
            print(f"  ⚠️  无订阅者")
            event.handled = True
            return
        
        try:
            # 按优先级排序处理
            for handler in handlers:
                print(f"  📤 调用处理函数：{handler.__name__}")
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            
            event.handled = True
            self.stats['handled_events'] += 1
            self.stats['pending_events'] -= 1
            
            # 保存到历史
            self.history.append(event)
            
        except Exception as e:
            print(f"  ❌ 处理失败：{e}")
    
    def get_pending_events(self) -> List[Event]:
        """获取待处理事件"""
        return sorted(
            [e for e in self.event_queue if not e.handled],
            key=lambda e: e.priority.value
        )
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            'queue_size': len(self.get_pending_events()),
            'history_size': len(self.history)
        }

class EventTrigger:
    """事件触发器"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.last_check = {}
    
    def check_detection_rate(self, metrics: Dict):
        """检测率监控触发器"""
        detection_rate = metrics.get('detection_rate', 100)
        cycle_num = metrics.get('cycle_num', 0)
        
        # 获取上次检测率
        last_rate = self.last_check.get('detection_rate', detection_rate)
        drop = last_rate - detection_rate
        
        print(f"\n📊 检测率检查：{last_rate:.1f}% → {detection_rate:.1f}% (变化：{drop:+.1f}%)")
        
        # 紧急优化 (检测率<90%)
        if detection_rate < 90:
            event = Event(
                id=f"emergency_{cycle_num}",
                type=EventType.EMERGENCY_OPTIMIZE,
                priority=Priority.CRITICAL,
                timestamp=datetime.now().isoformat(),
                data={'detection_rate': detection_rate, 'drop': drop},
                source='detection_monitor'
            )
            self.event_bus.publish(event)
        
        # 检测率下降 (下降>2%)
        elif drop > 2:
            event = Event(
                id=f"rate_drop_{cycle_num}",
                type=EventType.DETECTION_RATE_DROP,
                priority=Priority.HIGH,
                timestamp=datetime.now().isoformat(),
                data={'detection_rate': detection_rate, 'drop': drop},
                source='detection_monitor'
            )
            self.event_bus.publish(event)
        
        # 更新记录
        self.last_check['detection_rate'] = detection_rate
    
    def check_threat_intel(self, intel_count: int = 0):
        """威胁情报触发器"""
        if intel_count > 0:
            event = Event(
                id=f"threat_intel_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                type=EventType.THREAT_INTEL_NEW,
                priority=Priority.MEDIUM,
                timestamp=datetime.now().isoformat(),
                data={'intel_count': intel_count},
                source='threat_intel_collector'
            )
            self.event_bus.publish(event)
    
    def check_schedule(self, schedule_type: str):
        """定时调度触发器"""
        event = Event(
            id=f"scheduled_{schedule_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            type=EventType.SCHEDULED_EVAL,
            priority=Priority.LOW,
            timestamp=datetime.now().isoformat(),
            data={'schedule_type': schedule_type},
            source='scheduler'
        )
        self.event_bus.publish(event)

class PriorityScheduler:
    """优先级调度器"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.running = False
    
    async def run(self):
        """运行调度器"""
        print("\n⚙️ 启动优先级调度器...")
        self.running = True
        
        while self.running:
            # 获取待处理事件 (按优先级排序)
            pending = self.event_bus.get_pending_events()
            
            if pending:
                print(f"\n📋 待处理事件：{len(pending)} 个")
                for event in pending[:3]:  # 显示前 3 个
                    print(f"  - {event.type.value} (优先级：{event.priority.name})")
            
            await asyncio.sleep(5)  # 每 5 秒检查一次
    
    def stop(self):
        """停止调度器"""
        self.running = False

# === 事件处理器示例 ===

async def handle_threat_intel(event: Event):
    """处理威胁情报事件"""
    print(f"  🤖 自动分析 {event.data.get('intel_count', 0)} 条威胁情报...")
    # 实际应调用 auto_optimizer
    await asyncio.sleep(1)
    print(f"  ✅ 威胁情报分析完成")

async def handle_detection_drop(event: Event):
    """处理检测率下降事件"""
    drop = event.data.get('drop', 0)
    rate = event.data.get('detection_rate', 0)
    print(f"  🚨 检测率下降 {drop:.1f}% (当前：{rate:.1f}%)")
    print(f"  🤖 触发紧急优化...")
    await asyncio.sleep(2)
    print(f"  ✅ 紧急优化完成")

async def handle_emergency(event: Event):
    """处理紧急优化事件"""
    rate = event.data.get('detection_rate', 0)
    print(f"  🚨 紧急优化！检测率降至 {rate:.1f}%")
    # 调用 P1 自动优化器
    await asyncio.sleep(1)
    print(f"  ✅ 紧急优化完成")

def handle_scheduled(event: Event):
    """处理定时评估事件"""
    print(f"  📅 定时评估：{event.data.get('schedule_type', 'unknown')}")

# === 主函数 ===

class EventDrivenSystem:
    """事件驱动系统"""
    
    def __init__(self):
        self.event_bus = EventBus()
        self.trigger = EventTrigger(self.event_bus)
        self.scheduler = PriorityScheduler(self.event_bus)
        
        # 注册事件处理器
        self._register_handlers()
    
    def _register_handlers(self):
        """注册事件处理器"""
        print("\n📬 注册事件处理器...")
        self.event_bus.subscribe(EventType.THREAT_INTEL_NEW, handle_threat_intel)
        self.event_bus.subscribe(EventType.DETECTION_RATE_DROP, handle_detection_drop)
        self.event_bus.subscribe(EventType.EMERGENCY_OPTIMIZE, handle_emergency)
        self.event_bus.subscribe(EventType.SCHEDULED_EVAL, handle_scheduled)
    
    async def run(self):
        """运行系统"""
        print("\n🚀 启动事件驱动系统...")
        
        # 启动调度器
        scheduler_task = asyncio.create_task(self.scheduler.run())
        
        # 模拟事件触发
        for i in range(5):
            await asyncio.sleep(10)
            
            # 模拟检测率监控
            if i == 2:
                self.trigger.check_detection_rate({'detection_rate': 93.5, 'cycle_num': i})
            else:
                self.trigger.check_detection_rate({'detection_rate': 95.8, 'cycle_num': i})
            
            # 模拟威胁情报采集
            if i == 3:
                self.trigger.check_threat_intel(intel_count=5)
        
        # 运行 60 秒后停止
        await asyncio.sleep(60)
        self.scheduler.stop()
        scheduler_task.cancel()
    
    def get_stats(self) -> Dict:
        """获取系统统计"""
        return self.event_bus.get_stats()

# === CLI ===

async def main():
    """主函数"""
    print("="*70)
    print("🎯 P2 事件驱动架构演示")
    print("="*70)
    
    system = EventDrivenSystem()
    
    # 运行系统
    await system.run()
    
    # 输出统计
    print("\n" + "="*70)
    print("📊 系统统计")
    print("="*70)
    stats = system.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

if __name__ == '__main__':
    asyncio.run(main())
