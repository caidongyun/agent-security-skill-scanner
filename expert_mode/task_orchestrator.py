#!/usr/bin/env python3
"""
🎯 任务编排器 - 自动拆分任务为最小可执行单元
"""

import json
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime

# 任务目录
TASKS_DIR = Path("tasks")
REPORTS_DIR = Path("reports")
TASKS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)


@dataclass
class RuleTask:
    """单条规则任务"""
    id: str
    attack_type: str
    rule_type: str
    pattern: str
    test_cases: List[str]
    status: str = "pending"  # pending/running/completed/failed


class TaskOrchestrator:
    """任务编排器"""
    
    def __init__(self):
        self.tasks: List[RuleTask] = []
        self.load_rules()
    
    def load_rules(self):
        """从 rules/ 目录加载规则"""
        rules_dir = Path("rules")
        if not rules_dir.exists():
            print("❌ rules/ 目录不存在")
            return
        
        # 遍历所有规则 (rules/{rule_type}/{attack_type}/*.json)
        for rule_type_dir in rules_dir.iterdir():
            if not rule_type_dir.is_dir():
                continue
            
            rule_type = rule_type_dir.name
            
            for attack_type_dir in rule_type_dir.iterdir():
                if not attack_type_dir.is_dir():
                    continue
                
                attack_type = attack_type_dir.name
                
                for rule_file in attack_type_dir.glob("*.json"):
                    try:
                        with open(rule_file) as f:
                            rule = json.load(f)
                        
                        task = RuleTask(
                            id=rule.get("id", rule_file.stem),
                            attack_type=attack_type,
                            rule_type=rule_type,
                            pattern=rule.get("patterns", [""])[0],
                            test_cases=rule.get("test_cases", {}).get("positive", [])
                        )
                        self.tasks.append(task)
                    except Exception as e:
                        print(f"⚠️  加载失败 {rule_file}: {e}")
        
        print(f"📋 加载了 {len(self.tasks)} 个规则任务")
    
    def list_tasks(self, attack_type: str = None):
        """列出任务"""
        tasks = self.tasks
        if attack_type:
            tasks = [t for t in tasks if t.attack_type == attack_type]
        
        print(f"\n{'='*60}")
        print(f"📋 任务列表 ({len(tasks)} 个)")
        print(f"{'='*60}")
        
        for task in tasks:
            status_icon = {
                "pending": "⏳",
                "running": "🔬",
                "completed": "✅",
                "failed": "❌"
            }.get(task.status, "❓")
            
            print(f"{status_icon} {task.id:20s} | {task.attack_type:20s} | {task.rule_type}")
    
    def run_task(self, task_id: str) -> Dict:
        """运行单个任务"""
        task = next((t for t in self.tasks if t.id == task_id), None)
        if not task:
            return {"error": f"任务 {task_id} 不存在"}
        
        task.status = "running"
        
        print(f"\n🔬 运行任务: {task.id}")
        print(f"   攻击类型: {task.attack_type}")
        print(f"   规则类型: {task.rule_type}")
        print(f"   Pattern: {task.pattern}")
        
        # 运行测试
        result = {
            "task_id": task.id,
            "status": "completed",
            "passed": 0,
            "failed": 0
        }
        
        # 简单测试 - 检查 pattern 是否能匹配 test cases
        import re
        for test_input in task.test_cases:
            try:
                if re.search(task.pattern, test_input, re.IGNORECASE):
                    result["passed"] += 1
                else:
                    result["failed"] += 1
            except:
                result["failed"] += 1
        
        task.status = "completed" if result["failed"] == 0 else "failed"
        
        return result
    
    def run_batch(self, attack_type: str, limit: int = 5):
        """批量运行任务"""
        tasks = [t for t in self.tasks if t.attack_type == attack_type]
        tasks = [t for t in tasks if t.status == "pending"][:limit]
        
        print(f"\n🚀 批量运行: {attack_type} (前 {len(tasks)} 个)")
        
        results = []
        for task in tasks:
            result = self.run_task(task.id)
            results.append(result)
        
        passed = sum(1 for r in results if r.get("passed", 0) > 0)
        print(f"\n📊 批量完成: {passed}/{len(results)} 有检测能力")
        
        return results
    
    def generate_report(self):
        """生成任务报告"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_tasks": len(self.tasks),
            "by_attack_type": {},
            "by_status": {}
        }
        
        # 按攻击类型统计
        for task in self.tasks:
            at = task.attack_type
            if at not in report["by_attack_type"]:
                report["by_attack_type"][at] = {"total": 0, "completed": 0, "failed": 0}
            report["by_attack_type"][at]["total"] += 1
            if task.status == "completed":
                report["by_attack_type"][at]["completed"] += 1
            elif task.status == "failed":
                report["by_attack_type"][at]["failed"] += 1
        
        # 按状态统计
        for task in self.tasks:
            status = task.status
            report["by_status"][status] = report["by_status"].get(status, 0) + 1
        
        # 保存报告
        report_file = REPORTS_DIR / f"task_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 报告已保存: {report_file}")
        return report


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="🎯 任务编排器")
    parser.add_argument("--list", action="store_true", help="列出所有任务")
    parser.add_argument("--attack-type", type=str, help="按攻击类型筛选")
    parser.add_argument("--run", type=str, help="运行单个任务")
    parser.add_argument("--batch", type=str, help="批量运行任务")
    parser.add_argument("--limit", type=int, default=5, help="批量运行数量")
    parser.add_argument("--report", action="store_true", help="生成报告")
    
    args = parser.parse_args()
    
    orchestrator = TaskOrchestrator()
    
    if args.list:
        orchestrator.list_tasks(args.attack_type)
    elif args.run:
        result = orchestrator.run_task(args.run)
        print(f"\n结果: {result}")
    elif args.batch:
        orchestrator.run_batch(args.batch, args.limit)
    elif args.report:
        orchestrator.generate_report()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
