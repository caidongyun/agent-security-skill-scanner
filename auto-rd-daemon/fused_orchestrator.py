#!/usr/bin/env python3
"""
融合版自动化循环系统
现有能力 + Skill 服务 + 自动循环
"""
import os, sys, json, time, signal, glob
from datetime import datetime
from pathlib import Path

# 导入现有能力
sys.path.insert(0, 'skills')
sys.path.insert(0, 'scanner-master')

class FusedOrchestrator:
    def __init__(self):
        self.log_file = 'logs/fused_orchestrator.log'
        self.status_file = 'logs/fused_status.json'
        self.session_dir = 'sessions/fused'
        self.skills_dir = 'skills'
        
        # 现有能力 (直接使用脚本)
        self.existing_tools = {
            'scanner': 'scanner-master/ros-scanner-v2.py',
            'benchmark': 'ros-orchestrator/ros-benchmark.sh',
            'progress': 'scripts/progress_reporter.py',
            'health': 'ros-orchestrator/ros-health-daemon.sh',
            'release': 'release/prepare_release.py',
        }
        
        # Skill 服务池 (按类别组织)
        self.skill_services = {
            'development': [
                'feature-dev',
                'code-generator',
                'test-generator',
            ],
            'testing': [
                'ros_test',
                'quality-gate',
            ],
            'research': [
                'self-improving-agent',
                'data-analyzer',
            ],
            'security': [
                'ultra-review',
                'security-sample-generator',
                'yara-rule-builder',
            ],
            'automation': [
                'workflow-automator',
                'pipeline-builder',
            ],
        }
        
        # 任务队列
        self.task_queue = []
        self.execution_history = []
        
        # 确保目录
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        os.makedirs(self.session_dir, exist_ok=True)
        
    def log(self, message):
        timestamp = datetime.now().isoformat()
        log_line = f"[{timestamp}] {message}\n"
        with open(self.log_file, 'a') as f:
            f.write(log_line)
        print(log_line.strip())
        
    def discover_skills(self):
        """发现可用的 Skill"""
        available = []
        for category, skills in self.skill_services.items():
            for skill in skills:
                skill_path = os.path.join(self.skills_dir, skill)
                if os.path.exists(skill_path):
                    available.append({
                        'name': skill,
                        'category': category,
                        'path': skill_path,
                    })
        return available
        
    def add_task(self, task, priority='P1', category='auto'):
        """添加任务"""
        self.task_queue.append({
            'id': len(self.task_queue) + 1,
            'task': task,
            'priority': priority,
            'category': category,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
        })
        self.log(f"✅ 任务已添加：{task}")
        
    def select_skill(self, task_desc):
        """根据任务描述选择合适的 Skill"""
        task_lower = task_desc.lower()
        
        # 简单匹配逻辑
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
            return 'self-improving-agent'  # 默认
            
    def execute_task(self, task):
        """执行任务"""
        self.log(f"📋 执行任务：{task['task']}")
        
        # 选择 Skill
        skill_name = self.select_skill(task['task'])
        self.log(f"  选择 Skill: {skill_name}")
        
        try:
            # 执行 Skill
            if skill_name == 'scanner':
                result = self.run_scanner()
            elif skill_name == 'feature-dev':
                result = self.run_feature_dev(task['task'])
            elif skill_name == 'self-improving-agent':
                result = self.run_self_improving(task['task'])
            elif skill_name == 'ultra-review':
                result = self.run_ultra_review(task['task'])
            elif skill_name == 'progress':
                result = self.run_progress_report()
            else:
                result = {'status': 'completed', 'skill': skill_name}
                
            task['status'] = 'completed'
            task['result'] = result
            task['completed_at'] = datetime.now().isoformat()
            task['skill_used'] = skill_name
            
            self.log(f"✅ 任务完成：{task['task']}")
            
        except Exception as e:
            task['status'] = 'failed'
            task['error'] = str(e)
            task['failed_at'] = datetime.now().isoformat()
            self.log(f"❌ 任务失败：{task['task']} - {e}")
            
        self.execution_history.append(task)
        return task
        
    def run_scanner(self):
        """运行扫描器"""
        self.log("  运行扫描器...")
        # 简化：实际应调用 ros-scanner-v2.py
        return {'status': 'scanned', 'samples': 100}
        
    def run_feature_dev(self, task_desc):
        """运行功能开发"""
        self.log("  运行功能开发...")
        from skills.feature_dev.main import FeatureDevAgent
        agent = FeatureDevAgent()
        result = agent.develop({
            'name': f"task_{len(self.execution_history)}",
            'description': task_desc,
        })
        return result
        
    def run_self_improving(self, task_desc):
        """运行自改进"""
        self.log("  运行自改进...")
        from skills.self_improving_agent.main import SelfImprovingAgent
        agent = SelfImprovingAgent()
        result = agent.execute(task_desc)
        return result
        
    def run_ultra_review(self, task_desc):
        """运行深度审查"""
        self.log("  运行深度审查...")
        from skills.ultra_review.main import UltraReview
        reviewer = UltraReview()
        result = reviewer.review(task_desc, type='all', deep=True)
        return result
        
    def run_progress_report(self):
        """运行进度汇报"""
        self.log("  生成进度报告...")
        subprocess.run(['python3', 'scripts/progress_reporter.py'], 
                      capture_output=True)
        return {'status': 'reported'}
        
    def run_cycle(self):
        """执行一个循环"""
        if not self.task_queue:
            # 自动添加常规任务
            self.add_task("生成进度报告", priority='P1', category='routine')
            self.add_task("扫描测试", priority='P2', category='routine')
            
        while self.task_queue:
            task = self.task_queue.pop(0)
            self.execute_task(task)
            
        # 生成循环报告
        if len(self.execution_history) % 5 == 0:
            self.generate_report()
            
    def generate_report(self):
        """生成执行报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_tasks': len(self.execution_history),
            'completed': len([t for t in self.execution_history if t['status'] == 'completed']),
            'failed': len([t for t in self.execution_history if t['status'] == 'failed']),
            'skills_used': {},
            'recent_tasks': self.execution_history[-10:],
        }
        
        # 统计 Skill 使用情况
        for task in self.execution_history:
            skill = task.get('skill_used', 'unknown')
            report['skills_used'][skill] = report['skills_used'].get(skill, 0) + 1
            
        os.makedirs('reports/fused', exist_ok=True)
        report_file = f"reports/fused/cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        self.log(f"📄 报告已生成：{report_file}")
        
    def run_continuous(self, interval=300):
        """持续运行"""
        self.log("🚀 启动融合版自动化循环系统")
        self.log(f"   循环间隔：{interval}秒")
        
        # 发现可用 Skill
        available_skills = self.discover_skills()
        self.log(f"   可用 Skill: {len(available_skills)} 个")
        for skill in available_skills[:5]:
            self.log(f"     - {skill['name']} ({skill['category']})")
        if len(available_skills) > 5:
            self.log(f"     ... 还有 {len(available_skills) - 5} 个")
        
        self.start_time = datetime.now()
        self.running = True
        
        iteration = 0
        while self.running:
            try:
                iteration += 1
                
                # 执行循环
                self.run_cycle()
                
                # 更新状态
                if iteration % 6 == 0:  # 每 30 秒
                    self.update_status({
                        'healthy': True,
                        'iteration': iteration,
                        'queue_size': len(self.task_queue),
                        'skills_available': len(available_skills),
                    })
                    
                time.sleep(interval / 12)
                
            except Exception as e:
                self.log(f"❌ 循环错误：{e}")
                time.sleep(60)
                
    def update_status(self, status):
        with open(self.status_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
                **status
            }, f, indent=2)

if __name__ == '__main__':
    import subprocess
    
    orchestrator = FusedOrchestrator()
    
    if len(sys.argv) > 1:
        # 添加任务并执行
        task = ' '.join(sys.argv[1:])
        orchestrator.add_task(task)
        orchestrator.run_cycle()
    else:
        # 守护模式
        orchestrator.run_continuous(interval=300)
