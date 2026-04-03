#!/usr/bin/env python3
"""
融合版扫描器自治研发系统
集成历史系统能力：Enhanced Orchestrator + Fused Orchestrator
"""

import subprocess
import json
import glob
import sys
import os
import time
import heapq
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

class FusedScannerAutoRD:
    """融合版扫描器自治研发系统"""
    
    def __init__(self):
        self.scanner_dir = Path.home() / ".openclaw/workspace/agent-security-skill-scanner-master"
        self.sample_gen_dir = Path.home() / ".openclaw/workspace/skills/security-sample-generator"
        self.benchmark_dir = Path.home() / "Desktop/security-benchmark"
        self.reports_dir = self.scanner_dir / "reports"
        self.rules_dir = self.scanner_dir / "rules" / "scanner_v3" / "yara"
        self.skills_dir = self.scanner_dir / "skills"
        
        # ===== 来自 Enhanced Orchestrator =====
        # 优先级队列
        self.task_queue: List[tuple] = []
        self.PRIORITY_MAP = {
            'P0': 0,  # 紧急 (立即执行)
            'P1': 1,  # 高 (优先执行)
            'P2': 2,  # 中 (正常执行)
            'P3': 3,  # 低 (空闲时执行)
        }
        
        # 故障处理
        self.max_retries = 3
        self.circuit_breaker = {}
        self.failed_tasks = []
        
        # 人工审核
        self.pending_approval = []
        self.approval_required = ['P0', 'security', 'production']
        
        # ===== 来自 Fused Orchestrator =====
        # 现有工具
        self.existing_tools = {
            'scanner': 'scanner-master/ros-scanner-v2.py',
            'benchmark': 'ros-orchestrator/ros-benchmark.sh',
            'progress': 'scripts/progress_reporter.py',
            'health': 'ros-orchestrator/ros-health-daemon.sh',
        }
        
        # Skill 服务池
        self.skill_services = {
            'development': ['feature-dev', 'code-generator'],
            'testing': ['ros_test', 'quality-gate'],
            'research': ['self-improving-agent', 'data-analyzer'],
            'security': ['ultra-review', 'security-sample-generator'],
            'automation': ['workflow-automator', 'pipeline-builder'],
        }
        
        # 执行历史
        self.execution_history = []
        
        # 日志
        self.log_file = self.scanner_dir / "logs" / "fused_scanner.log"
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().isoformat()
        log_line = f"[{timestamp}] {message}\n"
        with open(self.log_file, 'a') as f:
            f.write(log_line)
        print(log_line.strip())
    
    # ========== 来自 Enhanced Orchestrator 的能力 ==========
    
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
                'added_at': datetime.now().isoformat(),
            })
            return
        
        # 添加到优先级队列
        heapq.heappush(self.task_queue, (
            self.PRIORITY_MAP.get(priority, 2),
            time.time(),
            {
                'desc': task_desc,
                'priority': priority,
                'category': category,
                'added_at': datetime.now().isoformat(),
            }
        ))
        
        self.log(f"✅ 任务已添加：{task_desc} (优先级：{priority})")
    
    def needs_approval(self, priority, category):
        """检查是否需要人工审核"""
        return (priority in self.approval_required or 
                category in self.approval_required)
    
    def get_next_task(self):
        """获取下一个最高优先级任务"""
        if not self.task_queue:
            return None
        
        _, _, task = heapq.heappop(self.task_queue)
        return task
    
    def execute_with_retry(self, task_func, task_desc):
        """带重试的执行"""
        # 检查熔断器
        if task_desc in self.circuit_breaker:
            breaker_time = self.circuit_breaker[task_desc]
            if time.time() - breaker_time < 300:  # 5 分钟熔断
                self.log(f"⚠️  任务被熔断器阻止：{task_desc}")
                return False
        
        # 执行任务 (带重试)
        for attempt in range(self.max_retries):
            try:
                self.log(f"执行任务：{task_desc} (尝试 {attempt + 1}/{self.max_retries})")
                result = task_func()
                
                # 清除熔断器
                if task_desc in self.circuit_breaker:
                    del self.circuit_breaker[task_desc]
                
                return result
                
            except Exception as e:
                self.log(f"❌ 任务失败：{task_desc} - {e}")
                
                if attempt == self.max_retries - 1:
                    # 达到最大重试次数，触发熔断器
                    self.circuit_breaker[task_desc] = time.time()
                    self.failed_tasks.append({
                        'task': task_desc,
                        'error': str(e),
                        'failed_at': datetime.now().isoformat(),
                    })
                    return False
                
                # 指数退避
                time.sleep(2 ** attempt)
        
        return False
    
    # ========== 来自 Fused Orchestrator 的能力 ==========
    
    def discover_skills(self):
        """发现可用的 Skill"""
        available = []
        
        for category, skills in self.skill_services.items():
            for skill in skills:
                skill_path = self.skills_dir / skill
                if skill_path.exists():
                    available.append({
                        'name': skill,
                        'category': category,
                        'path': str(skill_path),
                        'type': 'directory',
                    })
        
        self.log(f"发现 {len(available)} 个可用 Skill")
        return available
    
    def discover_tools(self):
        """发现可用的工具"""
        available = []
        
        for name, path in self.existing_tools.items():
            tool_path = self.scanner_dir / path
            if tool_path.exists():
                available.append({
                    'name': name,
                    'path': str(tool_path),
                    'executable': os.access(tool_path, os.X_OK),
                    'type': 'file',
                })
        
        self.log(f"发现 {len(available)} 个可用工具")
        return available
    
    def select_skill_for_task(self, task_desc):
        """根据任务描述选择合适的 Skill"""
        task_lower = task_desc.lower()
        
        # 简单的关键词匹配
        skill_mapping = {
            'development': ['开发', '功能', '代码', 'feature', 'code'],
            'testing': ['测试', '验证', 'test', 'verify'],
            'security': ['安全', '扫描', '规则', 'security', 'scanner'],
            'research': ['研究', '分析', 'research', 'analyze'],
        }
        
        for category, keywords in skill_mapping.items():
            if any(kw in task_lower for kw in keywords):
                # 返回该类别的第一个可用 Skill
                if category in self.skill_services:
                    skill_name = self.skill_services[category][0]
                    skill_path = self.skills_dir / skill_name
                    if skill_path.exists():
                        return {
                            'name': skill_name,
                            'category': category,
                            'path': str(skill_path),
                        }
        
        return None
    
    # ========== 当前系统的能力 ==========
    
    def check_scanner_status(self):
        """检查扫描器状态"""
        self.log("=" * 60)
        self.log("检查扫描器状态")
        self.log("=" * 60)
        
        # 检查规则文件
        if not self.rules_dir.exists():
            self.log("❌ 规则目录不存在")
            return False
        
        rules_file = self.rules_dir / "scanner_rules.yar"
        if not rules_file.exists():
            self.log("❌ 规则文件不存在")
            return False
        
        # 统计规则数
        with open(rules_file) as f:
            rule_count = sum(1 for line in f if line.startswith("rule "))
        self.log(f"✅ 规则文件：{rule_count} 条")
        
        # 检查扫描器脚本
        scan_script = self.scanner_dir / "scan.sh"
        if not scan_script.exists():
            self.log("❌ scan.sh 不存在")
            return False
        
        self.log("✅ 扫描器脚本存在")
        return True
    
    def run_full_test(self):
        """运行全量测试"""
        self.log("开始全量测试...")
        
        # 这里调用实际的 auto_rd_scanner.py
        result = subprocess.run(
            [sys.executable, str(self.scanner_dir / "auto_rd_scanner.py")],
            capture_output=True, text=True, timeout=3600
        )
        
        self.log(f"全量测试完成：{result.returncode}")
        return result.returncode == 0
    
    # ========== 融合能力 ==========
    
    def run_fused_cycle(self):
        """运行融合循环"""
        self.log("=" * 60)
        self.log("启动融合版自治研发循环")
        self.log("=" * 60)
        
        # 1. 发现可用 Skill 和工具
        skills = self.discover_skills()
        tools = self.discover_tools()
        
        self.log(f"可用资源：{len(skills)} Skills, {len(tools)} 工具")
        
        # 2. 处理待办任务
        while True:
            task = self.get_next_task()
            if not task:
                self.log("✅ 所有任务已完成")
                break
            
            self.log(f"处理任务：{task['desc']}")
            
            # 3. 选择合适的 Skill
            skill = self.select_skill_for_task(task['desc'])
            
            if skill:
                self.log(f"使用 Skill: {skill['name']}")
                # 调用 Skill (简化版)
                # 实际应该调用 Skill 的接口
            else:
                self.log("⚠️  没有合适的 Skill，使用默认处理")
            
            # 4. 执行任务 (带重试)
            success = self.execute_with_retry(
                lambda: self.run_full_test(),
                task['desc']
            )
            
            # 5. 记录执行历史
            self.execution_history.append({
                'task': task,
                'skill': skill,
                'success': success,
                'executed_at': datetime.now().isoformat(),
            })
        
        # 6. 保存状态
        self.save_state()
        
        self.log("=" * 60)
        self.log("融合循环完成")
        self.log("=" * 60)
    
    def save_state(self):
        """保存当前状态"""
        state_file = self.scanner_dir / "logs" / "fused_state.json"
        state = {
            'task_queue_size': len(self.task_queue),
            'execution_history': self.execution_history[-100:],  # 保留最近 100 条
            'failed_tasks': self.failed_tasks[-50:],  # 保留最近 50 个
            'circuit_breaker': self.circuit_breaker,
            'saved_at': datetime.now().isoformat(),
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        self.log(f"✅ 状态已保存：{state_file}")
    
    def show_status(self):
        """显示当前状态"""
        print("=" * 60)
        print("📊 融合版扫描器状态")
        print("=" * 60)
        print()
        
        # 任务队列
        print(f"待办任务：{len(self.task_queue)} 个")
        if self.task_queue:
            print("  最高优先级任务:", self.task_queue[0][2]['desc'])
        
        # Skill 和工具
        skills = self.discover_skills()
        tools = self.discover_tools()
        print(f"可用 Skill: {len(skills)} 个")
        print(f"可用工具：{len(tools)} 个")
        
        # 执行历史
        print(f"执行历史：{len(self.execution_history)} 条")
        
        # 失败任务
        print(f"失败任务：{len(self.failed_tasks)} 个")
        
        # 熔断器
        print(f"熔断器：{len(self.circuit_breaker)} 个")
        
        print("=" * 60)

def main():
    """主函数"""
    scanner = FusedScannerAutoRD()
    
    # 显示状态
    scanner.show_status()
    
    # 添加示例任务
    scanner.add_task("全量测试", priority='P0', category='security')
    scanner.add_task("规则优化", priority='P1', category='security')
    scanner.add_task("性能分析", priority='P2', category='research')
    
    # 运行融合循环
    scanner.run_fused_cycle()

if __name__ == '__main__':
    main()
