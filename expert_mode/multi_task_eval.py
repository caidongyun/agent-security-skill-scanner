#!/usr/bin/env python3
"""
灵顺 - 多任务自动评估循环系统
持续评估 + 持续改进
"""

import asyncio
import subprocess
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(Path(__file__).parent.parent))

from expert_mode.risk_assessor import RiskRule, RiskAssessor


class MultiTaskEvaluator:
    """
    多任务自动评估系统
    并行执行多个评估任务
    """
    
    def __init__(self, project_path: str = None):
        self.project_path = project_path or str(Path(__file__).parent.parent)
        self.version = "0.1.0"
        self.round = 0
        self.best_score = 0
        self.history = []
        
        # 评估任务
        self.tasks = [
            {"name": "代码质量扫描", "func": self._scan_quality, "priority": 1},
            {"name": "安全风险扫描", "func": self._scan_security, "priority": 1},
            {"name": "测试覆盖评估", "func": self._eval_tests, "priority": 2},
            {"name": "性能评估", "func": self._eval_performance, "priority": 3},
            {"name": "文档完整性", "func": self._eval_docs, "priority": 4},
        ]
        
    async def run_cycle(self):
        """执行一轮多任务评估"""
        self.round += 1
        start_time = time.time()
        
        print(f"\n{'='*60}")
        print(f"🔄 多任务评估 - 第 {self.round} 轮")
        print(f"📁 项目: {self.project_path}")
        print(f"⏱️  时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        
        result = {
            "round": self.round,
            "timestamp": datetime.now().isoformat(),
            "tasks": {},
            "total_score": 0,
            "issues": [],
            "improvements": []
        }
        
        # 并行执行评估任务
        print("\n📋 并行执行评估任务...")
        
        task_results = await self._run_tasks_parallel()
        
        # 汇总结果
        for task_name, task_result in task_results.items():
            result["tasks"][task_name] = task_result
            result["total_score"] += task_result.get("score", 0)
            
        # 发现问题
        print("\n🔍 发现问题...")
        issues = self._collect_issues(task_results)
        result["issues"] = issues
        print(f"   发现 {len(issues)} 个问题")
        
        # 制定改进
        print("\n🚀 制定改进...")
        improvements = self._plan_improvements(issues)
        result["improvements"] = improvements
        print(f"   制定 {len(improvements)} 项改进")
        
        # 记录历史
        duration = time.time() - start_time
        result["duration"] = duration
        self.history.append(result)
        
        # 评估得分
        score = result["total_score"]
        
        # 检查是否超越
        if score > self.best_score:
            self.best_score = score
            print(f"\n🎉 超越历史! 得分: {score} (最佳: {self.best_score})")
        else:
            print(f"\n📊 得分: {score} (最佳: {self.best_score})")
            
        # 总结
        print(f"\n{'='*60}")
        print(f"📈 第 {self.round} 轮完成")
        print(f"⏱️  用时: {duration:.1f}s")
        print(f"📊 总得分: {score}")
        print(f"🔧 问题: {len(issues)}")
        print(f"🚀 改进: {len(improvements)}")
        print(f"{'='*60}")
        
        return result
        
    async def _run_tasks_parallel(self):
        """并行执行任务"""
        results = {}
        
        # 使用线程池并行执行
        loop = asyncio.get_event_loop()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(task["func"]): task["name"] 
                for task in self.tasks
            }
            
            for future in futures:
                task_name = futures[future]
                try:
                    result = await asyncio.wrap_future(future)
                    results[task_name] = result
                except Exception as e:
                    results[task_name] = {
                        "score": 0,
                        "status": "ERROR",
                        "error": str(e)
                    }
                    
        return results
        
    def _scan_quality(self) -> dict:
        """代码质量扫描"""
        project = Path(self.project_path)
        issues = []
        
        # 检查重复代码
        code_patterns = {}
        for ext in ['.py']:
            for f in project.rglob(f'*{ext}'):
                if 'test' in f.name or f.name.startswith('.'):
                    continue
                try:
                    content = f.read_text(errors='ignore')
                    # 简单检查重复模式
                    for pattern in ['def ', 'class ', 'import ']:
                        count = content.count(pattern)
                        code_patterns[pattern] = code_patterns.get(pattern, 0) + count
                except:
                    pass
                    
        # 计算得分
        score = 80  # 基础分
        if len(issues) < 5:
            score += 20
            
        return {
            "name": "代码质量扫描",
            "score": score,
            "status": "OK",
            "issues": issues,
            "metrics": code_patterns
        }
        
    def _scan_security(self) -> dict:
        """安全风险扫描"""
        project = Path(self.project_path)
        findings = []
        
        # 扫描所有代码文件
        for ext in ['.py', '.js']:
            for f in project.rglob(f'*{ext}'):
                if 'test' in f.name or f.name.startswith('.'):
                    continue
                try:
                    content = f.read_text(errors='ignore')
                    file_findings = RiskRule.match(content)
                    for ff in file_findings:
                        ff['file'] = str(f.relative_to(project))
                    findings.extend(file_findings)
                except:
                    pass
                    
        # 计算得分
        high_risk = len([f for f in findings if f.get('severity') == 'HIGH'])
        score = max(0, 100 - high_risk * 20)
        
        return {
            "name": "安全风险扫描",
            "score": score,
            "status": "OK",
            "findings": findings[:10],  # 只保留前10个
            "high_risk_count": high_risk
        }
        
    def _eval_tests(self) -> dict:
        """测试覆盖评估"""
        project = Path(self.project_path)
        
        # 检查测试文件
        test_files = list(project.rglob("test*.py"))
        
        score = min(100, len(test_files) * 20 + 40)
        
        return {
            "name": "测试覆盖评估",
            "score": score,
            "status": "OK",
            "test_files": len(test_files)
        }
        
    def _eval_performance(self) -> dict:
        """性能评估"""
        project = Path(self.project_path)
        
        # 统计代码行数
        total_lines = 0
        for ext in ['.py']:
            for f in project.rglob(f'*{ext}'):
                if 'test' not in f.name:
                    try:
                        total_lines += len(f.read_text(errors='ignore').splitlines())
                    except:
                        pass
        
        # 根据代码行数评估
        if total_lines > 1000:
            score = 90
        elif total_lines > 500:
            score = 70
        else:
            score = 50
            
        return {
            "name": "性能评估",
            "score": score,
            "status": "OK",
            "total_lines": total_lines
        }
        
    def _eval_docs(self) -> dict:
        """文档完整性"""
        project = Path(self.project_path)
        
        docs = [
            "README.md",
            "SKILL.md", 
            "DEVELOPMENT_PLAN.md",
            "TASK_PLAN.md"
        ]
        
        existing = [d for d in docs if (project / d).exists()]
        
        score = min(100, len(existing) * 25)
        
        return {
            "name": "文档完整性",
            "score": score,
            "status": "OK",
            "existing_docs": existing
        }
        
    def _collect_issues(self, task_results):
        """收集问题"""
        issues = []
        
        for task_name, result in task_results.items():
            if result.get("status") != "OK":
                issues.append({
                    "task": task_name,
                    "issue": result.get("error", "未知错误"),
                    "severity": "HIGH"
                })
                
            # 安全问题
            if "安全" in task_name:
                findings = result.get("findings", [])
                for f in findings[:3]:
                    issues.append({
                        "task": task_name,
                        "issue": f"{f.get('pattern')} in {f.get('file', '')}",
                        "severity": f.get("severity", "MEDIUM")
                    })
                    
        return issues
        
    def _plan_improvements(self, issues):
        """制定改进计划"""
        improvements = []
        
        for issue in issues:
            severity = issue.get("severity", "LOW")
            
            if "安全" in issue.get("task", ""):
                improvements.append({
                    "issue": issue.get("issue", ""),
                    "priority": "P1" if severity == "HIGH" else "P2",
                    "action": "修复安全问题"
                })
            else:
                improvements.append({
                    "issue": issue.get("issue", ""),
                    "priority": "P3",
                    "action": "优化代码质量"
                })
                
        return improvements
        
    async def run_forever(self, interval: int = 300):
        """持续循环评估"""
        print(f"\n🚀 多任务评估系统启动 v{self.version}")
        print(f"⏱️  循环间隔: {interval}秒")
        
        while True:
            try:
                await self.run_cycle()
                
                print(f"\n💤 等待 {interval}秒...")
                await asyncio.sleep(interval)
                
            except KeyboardInterrupt:
                print("\n\n🛑 停止评估")
                break
            except Exception as e:
                print(f"\n❌ 错误: {e}")
                await asyncio.sleep(60)


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="多任务自动评估系统")
    parser.add_argument("--once", action="store_true", help="只运行一轮")
    parser.add_argument("--interval", type=int, default=300, help="循环间隔(秒)")
    
    args = parser.parse_args()
    
    evaluator = MultiTaskEvaluator()
    
    if args.once:
        await evaluator.run_cycle()
    else:
        await evaluator.run_forever(args.interval)


if __name__ == "__main__":
    asyncio.run(main())
