#!/usr/bin/env python3
"""
Self-Improving Agent - 自改进 Agent
从执行结果中学习，持续优化自身能力
"""
import os, json, time
from datetime import datetime
from pathlib import Path

class SelfImprovingAgent:
    def __init__(self):
        self.knowledge_base = 'knowledge/self_improving.json'
        self.execution_log = 'logs/self_improving_executions.jsonl'
        self.improvement_history = 'logs/improvements.jsonl'
        
        # 确保目录存在
        os.makedirs(os.path.dirname(self.knowledge_base), exist_ok=True)
        os.makedirs(os.path.dirname(self.execution_log), exist_ok=True)
        os.makedirs(os.path.dirname(self.improvement_history), exist_ok=True)
        
        # 加载知识库
        self.knowledge = self.load_knowledge()
        
    def load_knowledge(self):
        """加载知识库"""
        if os.path.exists(self.knowledge_base):
            with open(self.knowledge_base) as f:
                return json.load(f)
        return {
            'successful_patterns': [],
            'failed_patterns': [],
            'optimizations': [],
            'best_practices': [],
        }
        
    def save_knowledge(self):
        """保存知识库"""
        with open(self.knowledge_base, 'w') as f:
            json.dump(self.knowledge, f, indent=2)
            
    def execute(self, task):
        """执行任务"""
        print(f"[{datetime.now()}] 执行任务：{task}")
        
        # 记录执行
        execution = {
            'timestamp': datetime.now().isoformat(),
            'task': task,
            'status': 'running',
        }
        
        try:
            # 执行逻辑 (这里简化，实际应调用具体执行器)
            result = self._execute_task(task)
            
            execution['status'] = 'success'
            execution['result'] = result
            
            # 学习成功经验
            self.learn_success(task, result)
            
        except Exception as e:
            execution['status'] = 'failed'
            execution['error'] = str(e)
            
            # 学习失败教训
            self.learn_failure(task, e)
            
        # 记录执行日志
        self.log_execution(execution)
        
        return execution
        
    def _execute_task(self, task):
        """实际执行任务 (简化版)"""
        # 这里应该根据任务类型调用不同的执行器
        # 示例：
        if 'scan' in task.lower():
            return {'scanned': 100, 'malicious': 10}
        elif 'optimize' in task.lower():
            return {'optimized': True, 'improvement': '15%'}
        else:
            return {'completed': True}
            
    def learn_success(self, task, result):
        """学习成功经验"""
        print(f"[{datetime.now()}] ✅ 学习成功经验")
        
        self.knowledge['successful_patterns'].append({
            'task_pattern': self.extract_pattern(task),
            'result': result,
            'learned_at': datetime.now().isoformat(),
        })
        
        # 限制知识库大小
        if len(self.knowledge['successful_patterns']) > 100:
            self.knowledge['successful_patterns'] = self.knowledge['successful_patterns'][-100:]
            
        self.save_knowledge()
        
    def learn_failure(self, task, error):
        """学习失败教训"""
        print(f"[{datetime.now()}] ❌ 学习失败教训：{error}")
        
        self.knowledge['failed_patterns'].append({
            'task_pattern': self.extract_pattern(task),
            'error': str(error),
            'learned_at': datetime.now().isoformat(),
        })
        
        # 限制知识库大小
        if len(self.knowledge['failed_patterns']) > 100:
            self.knowledge['failed_patterns'] = self.knowledge['failed_patterns'][-100:]
            
        self.save_knowledge()
        
    def extract_pattern(self, task):
        """提取任务模式"""
        # 简化版：提取关键词
        keywords = ['scan', 'optimize', 'test', 'build', 'deploy']
        return [kw for kw in keywords if kw in task.lower()]
        
    def log_execution(self, execution):
        """记录执行日志"""
        with open(self.execution_log, 'a') as f:
            f.write(json.dumps(execution) + '\n')
            
    def get_improvement_suggestions(self):
        """获取改进建议"""
        suggestions = []
        
        # 分析失败模式
        failed_patterns = self.knowledge.get('failed_patterns', [])
        if failed_patterns:
            suggestions.append({
                'type': 'avoid_failures',
                'description': f'避免 {len(failed_patterns)} 种已知失败模式',
            })
            
        # 总结最佳实践
        successful_patterns = self.knowledge.get('successful_patterns', [])
        if successful_patterns:
            suggestions.append({
                'type': 'follow_best_practices',
                'description': f'遵循 {len(successful_patterns)} 种成功模式',
            })
            
        return suggestions
        
    def run_continuous(self, interval=300):
        """持续运行 (守护模式)"""
        print(f"[{datetime.now()}] 🚀 启动持续运行模式 (间隔：{interval}秒)")
        
        try:
            while True:
                # 检查是否有待执行任务
                tasks = self.get_pending_tasks()
                
                for task in tasks:
                    self.execute(task)
                    
                # 定期总结改进
                suggestions = self.get_improvement_suggestions()
                if suggestions:
                    print(f"[{datetime.now()}] 💡 改进建议：{suggestions}")
                    
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"[{datetime.now()}] 收到终止信号，退出")
            
    def get_pending_tasks(self):
        """获取待执行任务"""
        # 从任务队列获取
        # 简化版：返回空列表
        return []

if __name__ == '__main__':
    import sys
    
    agent = SelfImprovingAgent()
    
    if len(sys.argv) > 1:
        # 执行指定任务
        task = ' '.join(sys.argv[1:])
        agent.execute(task)
    else:
        # 守护模式
        agent.run_continuous(interval=300)  # 5 分钟间隔
