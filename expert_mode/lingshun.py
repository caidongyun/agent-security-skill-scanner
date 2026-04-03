#!/usr/bin/env python3
"""
🚀 灵顺编排系统 (Lingshun Orchestration System)
================================================
整合所有工具，统一调度:

1. 持续优化器 (lingshun_optimizer.py)
2. Code Review (code_review_agent.py)
3. 代码监控 (code_watcher.py)
4. 任务编排 (task_orchestrator.py)
5. 知识库 (knowledge_base_v2.py)

使用方式:
    python3 lingshun.py --status              # 查看状态
    python3 lingshun.py --run-all            # 运行全部
    python3 lingshun.py --optimize           # 运行优化
    python3 lingshun.py --review             # Code Review
    python3 lingshun.py --watch              # 代码监控
    python3 lingshun.py --daemon             # 守护模式
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List


SCRIPT_DIR = Path(__file__).parent
STATE_FILE = SCRIPT_DIR / ".lingshun_state.json"


class LingshunOrchestrator:
    """灵顺编排系统"""
    
    def __init__(self):
        self.state = self.load_state()
    
    def load_state(self) -> Dict:
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        return {
            "started_at": datetime.now().isoformat(),
            "last_full_run": None,
            "total_runs": 0,
            "optimization_rounds": 0,
            "code_issues_found": 0,
            "rules_reviewed": 0,
            "context_saved_bytes": 0
        }
    
    def save_state(self):
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def run_optimize(self) -> Dict:
        """运行优化器"""
        print("\n🔄 运行优化器...")
        
        result = subprocess.run(
            [sys.executable, "lingshun_optimizer.py", "--run-once"],
            capture_output=True,
            text=True,
            cwd=str(SCRIPT_DIR)
        )
        
        success = result.returncode == 0
        
        # 解析输出
        output = result.stdout + result.stderr
        rounds = 0
        if "优化轮次" in output:
            for line in output.split("\n"):
                if "优化轮次" in line:
                    try:
                        rounds = int(line.split(":")[-1].strip())
                    except:
                        pass
        
        self.state["optimization_rounds"] = rounds
        
        return {
            "success": success,
            "output": output[-200:] if len(output) > 200 else output
        }
    
    def run_code_review(self) -> Dict:
        """运行 Code Review"""
        print("\n🔍 运行 Code Review...")
        
        result = subprocess.run(
            [sys.executable, "code_review_agent.py", "--all", "--report"],
            capture_output=True,
            text=True,
            cwd=str(SCRIPT_DIR)
        )
        
        output = result.stdout + result.stderr
        
        # 解析通过率
        approved = 0
        if "通过:" in output:
            for line in output.split("\n"):
                if "通过:" in line:
                    try:
                        approved = int(line.split("通过:")[1].split("(")[0].strip())
                    except:
                        pass
        
        self.state["rules_reviewed"] = approved
        
        return {
            "success": result.returncode == 0,
            "approved": approved,
            "output": output[-200:]
        }
    
    def run_code_watch(self) -> Dict:
        """运行代码监控"""
        print("\n👁️ 运行代码监控...")
        
        result = subprocess.run(
            [sys.executable, "code_watcher.py", "--check"],
            capture_output=True,
            text=True,
            cwd=str(SCRIPT_DIR)
        )
        
        output = result.stdout + result.stderr
        
        # 解析问题数
        issues = 0
        if "总问题数" in output:
            for line in output.split("\n"):
                if "总问题数" in line:
                    try:
                        issues = int(line.split(":")[-1].strip())
                    except:
                        pass
        
        self.state["code_issues_found"] = issues
        
        return {
            "success": result.returncode == 0,
            "issues": issues,
            "output": output[-200:]
        }
    
    def run_all(self) -> Dict:
        """运行全部"""
        print("\n" + "="*60)
        print("🚀 灵顺编排系统 - 全部运行")
        print("="*60)
        
        results = {
            "timestamp": datetime.now().isoformat()
        }
        
        # 1. 代码监控
        results["code_watch"] = self.run_code_watch()
        
        # 2. Code Review
        results["code_review"] = self.run_code_review()
        
        # 3. 优化器
        results["optimize"] = self.run_optimize()
        
        # 保存状态
        self.state["last_full_run"] = datetime.now().isoformat()
        self.state["total_runs"] += 1
        self.save_state()
        
        # 总结
        print("\n" + "="*60)
        print("📊 运行结果总结")
        print("="*60)
        
        print(f"\n🔍 代码问题: {results['code_watch'].get('issues', 0)} 个")
        print(f"✅ Code Review: {results['code_review'].get('approved', 0)} 条规则通过")
        print(f"🔄 优化轮次: {results['optimize'].get('output', '')[:50]}")
        
        return results
    
    def status(self):
        """显示状态"""
        print("\n" + "="*60)
        print("🚀 灵顺编排系统 - 状态")
        print("="*60)
        
        print(f"\n启动时间: {self.state.get('started_at', 'N/A')}")
        print(f"最后全量运行: {self.state.get('last_full_run', 'N/A')}")
        print(f"总运行次数: {self.state.get('total_runs', 0)}")
        print(f"优化轮次: {self.state.get('optimization_rounds', 0)}")
        print(f"Code Review 通过: {self.state.get('rules_reviewed', 0)}")
        print(f"代码问题发现: {self.state.get('code_issues_found', 0)}")
        print(f"上下文节省: {self.state.get('context_saved_bytes', 0)/1024:.1f} KB")
        
        # 检查守护进程
        print(f"\n📦 子系统状态:")
        
        # 检查优化器
        opt_pid = SCRIPT_DIR / ".lingshun_optimizer.pid"
        if opt_pid.exists():
            try:
                pid = int(opt_pid.read_text().strip())
                if os.path.exists(f"/proc/{pid}"):
                    print(f"   ✅ 优化器守护进程: 运行中 (PID: {pid})")
                else:
                    print(f"   ❌ 优化器守护进程: 已停止")
            except:
                print(f"   ❌ 优化器守护进程: 异常")
        else:
            print(f"   ⏳ 优化器守护进程: 未启动")
    
    def daemon(self, interval: int = 600):
        """守护模式"""
        print(f"\n🚀 灵顺编排守护进程启动")
        print(f"   间隔: {interval} 秒 ({interval/60:.0f} 分钟)")
        
        while True:
            self.run_all()
            print(f"\n😴 等待 {interval} 秒...")
            time.sleep(interval)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="🚀 灵顺编排系统")
    parser.add_argument("--status", action="store_true", help="查看状态")
    parser.add_argument("--run-all", action="store_true", help="运行全部")
    parser.add_argument("--optimize", action="store_true", help="运行优化")
    parser.add_argument("--review", action="store_true", help="运行 Code Review")
    parser.add_argument("--watch", action="store_true", help="运行代码监控")
    parser.add_argument("--daemon", action="store_true", help="守护模式")
    parser.add_argument("--interval", type=int, default=600, help="守护模式间隔")
    
    args = parser.parse_args()
    
    orchestrator = LingshunOrchestrator()
    
    if args.status:
        orchestrator.status()
    elif args.run_all:
        orchestrator.run_all()
    elif args.optimize:
        orchestrator.run_optimize()
    elif args.review:
        orchestrator.run_code_review()
    elif args.watch:
        orchestrator.run_code_watch()
    elif args.daemon:
        orchestrator.daemon(args.interval)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
