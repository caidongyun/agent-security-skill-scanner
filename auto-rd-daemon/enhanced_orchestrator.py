#!/usr/bin/env python3
"""
增强版融合编排器
优先级队列 + 人工审核 + 故障处理
"""
import os, sys, json, time, signal, heapq, subprocess
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, List

# 优先级定义
PRIORITY_MAP = {
    'P0': 0,  # 紧急 (立即执行)
    'P1': 1,  # 高 (优先执行)
    'P2': 2,  # 中 (正常执行)
    'P3': 3,  # 低 (空闲时执行)
}

@dataclass(order=True)
class PrioritizedTask:
    priority: int
    created_at: float
    task: Dict = field(compare=False)

class EnhancedOrchestrator:
    def __init__(self):
        self.log_file = 'logs/enhanced_orchestrator.log'
        self.status_file = 'logs/enhanced_status.json'
        self.session_dir = 'sessions/enhanced'
        self.skills_dir = 'skills'
        
        # 优先级队列 (堆实现)
        self.task_queue: List[PrioritizedTask] = []
        self.execution_history = []
        
        # 故障处理
        self.failed_tasks = []
        self.retry_queue = []
        self.max_retries = 3
        self.circuit_breaker = {}  # 熔断器
        
        # 人工审核
        self.pending_approval = []
        self.approval_required = ['P0', 'security', 'production']
        
        # Skill 服务池
        self.skill_services = {
            'development': ['feature-dev', 'code-generator'],
            'testing': ['ros_test', 'quality-gate'],
            'research': ['self-improving-agent', 'data-analyzer'],
            'security': ['ultra-review', 'security-sample-generator'],
            'automation': ['workflow-automator', 'pipeline-builder'],
        }
        
        # 确保目录
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        os.makedirs(self.session_dir, exist_ok=True)
        
        # 加载历史状态
        self.load_state()
        
    def load_state(self):
        """加载历史状态"""
        state_file = 'logs/orchestrator_state.json'
        if os.path.exists(state_file):
            with open(state_file) as f:
                state = json.load(f)
                self.failed_tasks = state.get('failed_tasks', [])
                self.circuit_breaker = state.get('circuit_breaker', {})
                self.log("✅ 已加载历史状态")
                
    def save_state(self):
        """保存历史状态"""
        state_file = 'logs/orchestrator_state.json'
        state = {
            'failed_tasks': self.failed_tasks[-100:],  # 保留最近 100 个
            'circuit_breaker': self.circuit_breaker,
            'saved_at': datetime.now().isoformat(),
        }
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
            
    def log(self, message):
        timestamp = datetime.now().isoformat()
        log_line = f"[{timestamp}] {message}\n"
        with open(self.log_file, 'a') as f:
            f.write(log_line)
        print(log_line.strip())
        
    def add_task(self, task_desc: str, priority: str = 'P1', 
                 category: str = 'auto', requires_approval: bool = False):
        """添加任务到优先级队列"""
        
        # 检查是否需要人工审核
        if requires_approval or self.needs_approval(priority, category):
            self.log(f"⏳ 任务等待人工审核：{task_desc}")
            self.pending_approval.append({
                'task': task_desc,
                'priority': priority,
                'category': category,
                'requested_at': datetime.now().isoformat(),
            })
            return
            
        # 添加到优先级队列
        task = {
            'id': len(self.execution_history) + len(self.task_queue) + 1,
            'task': task_desc,
            'priority': priority,
            'category': category,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'retries': 0,
        }
        
        prioritized = PrioritizedTask(
            priority=PRIORITY_MAP.get(priority, 2),
            created_at=time.time(),
            task=task,
        )
        
        heapq.heappush(self.task_queue, prioritized)
        self.log(f"✅ 任务已添加 [P{priority}]: {task_desc}")
        
    def needs_approval(self, priority: str, category: str) -> bool:
        """判断是否需要人工审核"""
        return (priority in self.approval_required or 
                category in self.approval_required)
                
    def approve_task(self, index: int):
        """人工审核通过"""
        if 0 <= index < len(self.pending_approval):
            pending = self.pending_approval.pop(index)
            self.add_task(
                pending['task'],
                priority=pending['priority'],
                category=pending['category'],
                requires_approval=False,  # 已通过
            )
            self.log(f"✅ 任务已审核通过：{pending['task']}")
        else:
            self.log(f"❌ 无效审核索引：{index}")
            
    def reject_task(self, index: int, reason: str):
        """人工审核拒绝"""
        if 0 <= index < len(self.pending_approval):
            pending = self.pending_approval.pop(index)
            self.log(f"❌ 任务已拒绝：{pending['task']} - {reason}")
        else:
            self.log(f"❌ 无效审核索引：{index}")
            
    def select_skill(self, task_desc: str) -> Optional[str]:
        """选择 Skill (带熔断检查)"""
        skill_name = self._select_skill_logic(task_desc)
        
        # 检查熔断器
        if skill_name in self.circuit_breaker:
            cb = self.circuit_breaker[skill_name]
            if cb['failures'] >= 5:  # 5 次失败触发熔断
                self.log(f"⚠️  Skill {skill_name} 已熔断，跳过")
                return None
                
        return skill_name
        
    def _select_skill_logic(self, task_desc: str) -> str:
        """Skill 选择逻辑"""
        task_lower = task_desc.lower()
        
        if '开发' in task_lower or 'develop' in task_lower:
            return 'feature-dev'
        elif '测试' in task_lower or 'test' in task_lower:
            return 'ros_test'
        elif '优化' in task_lower or 'optimize' in task_lower:
            return 'self-improving-agent'
        elif '审查' in task_lower or 'review' in task_lower:
            return 'ultra-review'
        elif '扫描' in task_lower or 'scan' in task_lower:
            return 'scanner'
        elif '样本' in task_lower or 'sample' in task_lower:
            return 'security-sample-generator'
        elif '规则' in task_lower or 'rule' in task_lower:
            return 'yara-rule-builder'
        elif '报告' in task_lower or 'report' in task_lower:
            return 'progress'
        else:
            return 'self-improving-agent'
            
    def execute_task(self, task: Dict) -> Dict:
        """执行任务 (带故障处理)"""
        self.log(f"📋 执行任务 [尝试 {task.get('retries', 0)+1}/{self.max_retries}]: {task['task']}")
        
        # 选择 Skill
        skill_name = self.select_skill(task['task'])
        if not skill_name:
            return {'status': 'skipped', 'reason': 'Skill circuit breaker open'}
            
        task['skill_used'] = skill_name
        
        try:
            # 设置超时
            timeout = 300  # 5 分钟超时
            
            # 执行 Skill
            result = self._execute_skill(skill_name, task['task'], timeout)
            
            # 成功
            task['status'] = 'completed'
            task['result'] = result
            task['completed_at'] = datetime.now().isoformat()
            
            # 重置熔断器
            if skill_name in self.circuit_breaker:
                self.circuit_breaker[skill_name]['failures'] = 0
                
            self.log(f"✅ 任务完成：{task['task']}")
            
        except TimeoutError as e:
            self.log(f"❌ 任务超时：{task['task']}")
            return self._handle_failure(task, 'timeout', str(e))
            
        except Exception as e:
            self.log(f"❌ 任务失败：{task['task']} - {e}")
            return self._handle_failure(task, 'error', str(e))
            
        self.execution_history.append(task)
        return task
        
    def _execute_skill(self, skill_name: str, task_desc: str, timeout: int) -> Dict:
        """执行 Skill (简化版)"""
        if skill_name == 'scanner':
            # 调用扫描器
            result = subprocess.run(
                ['python3', 'scanner-master/ros-scanner-v2.py', 'samples/malicious/', '--workers', '2'],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {'status': 'scanned', 'returncode': result.returncode}
            
        elif skill_name == 'feature-dev':
            from skills.feature_dev.main import FeatureDevAgent
            agent = FeatureDevAgent()
            return agent.develop({
                'name': f"task_{len(self.execution_history)}",
                'description': task_desc,
            })
            
        elif skill_name == 'self-improving-agent':
            from skills.self_improving_agent.main import SelfImprovingAgent
            agent = SelfImprovingAgent()
            return agent.execute(task_desc)
            
        elif skill_name == 'ultra-review':
            from skills.ultra_review.main import UltraReview
            reviewer = UltraReview()
            return reviewer.review(task_desc, type='all', deep=True)
            
        elif skill_name == 'progress':
            subprocess.run(['python3', 'scripts/progress_reporter.py'], 
                          capture_output=True, timeout=60)
            return {'status': 'reported'}
            
        else:
            return {'status': 'completed', 'skill': skill_name}
            
    def _handle_failure(self, task: Dict, error_type: str, error_msg: str) -> Dict:
        """故障处理"""
        skill_name = task.get('skill_used', 'unknown')
        
        # 更新熔断器
        if skill_name not in self.circuit_breaker:
            self.circuit_breaker[skill_name] = {'failures': 0, 'last_failure': None}
        self.circuit_breaker[skill_name]['failures'] += 1
        self.circuit_breaker[skill_name]['last_failure'] = datetime.now().isoformat()
        
        # 重试逻辑
        task['retries'] = task.get('retries', 0) + 1
        
        if task['retries'] < self.max_retries:
            # 加入重试队列 (指数退避)
            delay = min(60 * (2 ** task['retries']), 600)  # 最多 10 分钟
            task['retry_at'] = (datetime.now().timestamp() + delay)
            self.retry_queue.append(task)
            self.log(f"🔄 任务将重试 [延迟 {delay}s]: {task['task']}")
        else:
            # 超过最大重试次数
            task['status'] = 'failed'
            task['error'] = f"{error_type}: {error_msg}"
            task['failed_at'] = datetime.now().isoformat()
            self.failed_tasks.append(task)
            self.log(f"❌ 任务最终失败：{task['task']}")
            
        # 保存状态
        self.save_state()
        
        return task
        
    def process_retry_queue(self):
        """处理重试队列"""
        now = datetime.now().timestamp()
        ready = []
        still_waiting = []
        
        for task in self.retry_queue:
            if task.get('retry_at', 0) <= now:
                ready.append(task)
            else:
                still_waiting.append(task)
                
        self.retry_queue = still_waiting
        
        # 将就绪的重试任务加回主队列
        for task in ready:
            prioritized = PrioritizedTask(
                priority=PRIORITY_MAP.get(task['priority'], 2) + 0.5,  # 重试任务优先级略低
                created_at=task.get('retry_at', now),
                task=task,
            )
            heapq.heappush(self.task_queue, prioritized)
            
        if ready:
            self.log(f"🔄 {len(ready)} 个任务准备重试")
            
    def run_cycle(self):
        """执行一个循环"""
        # 1. 处理重试队列
        self.process_retry_queue()
        
        # 2. 执行主队列任务
        if self.task_queue:
            prioritized = heapq.heappop(self.task_queue)
            task = prioritized.task
            self.execute_task(task)
            
        # 3. 定期生成报告
        if len(self.execution_history) % 10 == 0:
            self.generate_report()
            
        # 4. 定期保存状态
        if len(self.execution_history) % 5 == 0:
            self.save_state()
            
    def generate_report(self):
        """生成执行报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_tasks': len(self.execution_history),
            'completed': len([t for t in self.execution_history if t['status'] == 'completed']),
            'failed': len([t for t in self.execution_history if t['status'] == 'failed']),
            'pending_approval': len(self.pending_approval),
            'retry_queue': len(self.retry_queue),
            'circuit_breakers': {
                k: v for k, v in self.circuit_breaker.items() 
                if v['failures'] > 0
            },
            'recent_tasks': self.execution_history[-10:],
        }
        
        os.makedirs('reports/enhanced', exist_ok=True)
        report_file = f"reports/enhanced/cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        self.log(f"📄 报告已生成：{report_file}")
        
    def get_status(self) -> Dict:
        """获取系统状态"""
        return {
            'queue_size': len(self.task_queue),
            'pending_approval': len(self.pending_approval),
            'retry_queue': len(self.retry_queue),
            'failed_tasks': len(self.failed_tasks),
            'circuit_breakers': len([k for k, v in self.circuit_breaker.items() 
                                     if v['failures'] > 0]),
            'total_executed': len(self.execution_history),
        }
        
    def run_continuous(self, interval=60):
        """持续运行 (缩短默认间隔到 1 分钟)"""
        self.log("🚀 启动增强版自动化系统")
        self.log(f"   循环间隔：{interval}秒")
        self.log(f"   最大重试：{self.max_retries}")
        self.log(f"   需要审核：{self.approval_required}")
        
        self.start_time = datetime.now()
        self.running = True
        
        iteration = 0
        while self.running:
            try:
                iteration += 1
                
                # 执行循环
                self.run_cycle()
                
                # 更新状态
                if iteration % 30 == 0:  # 每 30 秒
                    self.save_state()
                    status = self.get_status()
                    self.log(f"📊 状态：队列={status['queue_size']}, "
                            f"审核={status['pending_approval']}, "
                            f"重试={status['retry_queue']}")
                    
                time.sleep(interval)
                
            except KeyboardInterrupt:
                self.log("🛑 收到终止信号")
                self.running = False
            except Exception as e:
                self.log(f"❌ 循环错误：{e}")
                time.sleep(interval)
                
        self.save_state()
        self.log("🛑 系统已停止")

if __name__ == '__main__':
    orchestrator = EnhancedOrchestrator()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--status':
            status = orchestrator.get_status()
            print(json.dumps(status, indent=2))
        elif sys.argv[1] == '--approve':
            index = int(sys.argv[2]) if len(sys.argv) > 2 else 0
            orchestrator.approve_task(index)
        elif sys.argv[1] == '--reject':
            index = int(sys.argv[2]) if len(sys.argv) > 2 else 0
            reason = sys.argv[3] if len(sys.argv) > 3 else '未通过'
            orchestrator.reject_task(index, reason)
        else:
            # 添加任务
            task = ' '.join(sys.argv[1:])
            priority = 'P1'
            if '--p0' in sys.argv:
                priority = 'P0'
            elif '--p2' in sys.argv:
                priority = 'P2'
            elif '--p3' in sys.argv:
                priority = 'P3'
            orchestrator.add_task(task, priority=priority)
            orchestrator.run_cycle()
    else:
        # 守护模式
        orchestrator.run_continuous(interval=60)
