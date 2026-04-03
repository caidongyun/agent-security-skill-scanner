#!/usr/bin/env python3
"""
灵顺 - 自我改进系统
持续改进 skill-scanner 项目
"""

import asyncio
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from expert_mode.risk_assessor import RiskRule, RiskAssessor


class LingshunSelfImprover:
    """
    灵顺自我改进系统
    核心: 扫描自己 → 发现问题 → 改进 → 测试 → 循环
    """
    
    def __init__(self, project_path: str = None):
        self.project_path = project_path or str(Path(__file__).parent.parent)
        self.version = "0.1.0"
        self.iteration = 0
        self.improvements = []
        
    async def improve_once(self):
        """执行一轮自我改进"""
        self.iteration += 1
        
        print(f"\n{'='*60}")
        print(f"🧬 灵顺自我改进 - 第 {self.iteration} 轮")
        print(f"📁 项目: {self.project_path}")
        print(f"{'='*60}")
        
        result = {
            "iteration": self.iteration,
            "timestamp": datetime.now().isoformat(),
            "scan_result": None,
            "issues": [],
            "improvements": [],
            "tests": {}
        }
        
        # 1. 扫描分析项目
        print("\n🔍 1. 扫描分析项目...")
        scan_result = await self._scan_project()
        result["scan_result"] = scan_result
        
        # 2. 发现问题
        print("\n📋 2. 发现问题...")
        issues = self._find_issues(scan_result)
        result["issues"] = issues
        print(f"   发现 {len(issues)} 个问题")
        
        # 3. 制定改进
        print("\n🚀 3. 制定改进...")
        improvements = self._plan_improvements(issues)
        result["improvements"] = improvements
        
        # 4. 执行改进
        print("\n⚙️  4. 执行改进...")
        for imp in improvements:
            await self._execute_improvement(imp)
            
        # 5. 测试验证
        print("\n🧪 5. 测试验证...")
        test_result = self._run_tests()
        result["tests"] = test_result
        
        print(f"\n{'='*60}")
        print(f"📊 第 {self.iteration} 轮完成")
        print(f"🔧 改进: {len(improvements)} 项")
        print(f"🧪 测试: {'通过' if test_result['passed'] else '失败'}")
        print(f"{'='*60}")
        
        return result
        
    async def _scan_project(self):
        """扫描项目"""
        result = {
            "total_files": 0,
            "code_files": 0,
            "findings": [],
            "metrics": {}
        }
        
        project = Path(self.project_path)
        
        # 扫描所有代码文件
        for ext in ['.py', '.js', '.sh']:
            for code_file in project.rglob(f'*{ext}'):
                # 跳过测试和隐藏文件
                if 'test' in code_file.name or code_file.name.startswith('.'):
                    continue
                if '__pycache__' in str(code_file):
                    continue
                    
                result["total_files"] += 1
                
                try:
                    code = code_file.read_text(errors='ignore')
                    result["code_files"] += 1
                    
                    # 风险检测
                    findings = RiskRule.match(code)
                    if findings:
                        for f in findings:
                            f['file'] = str(code_file.relative_to(project))
                        result["findings"].extend(findings)
                        
                except:
                    pass
                    
        # 统计
        result["metrics"] = {
            "total_files": result["total_files"],
            "code_files": result["code_files"],
            "risk_count": len(result["findings"]),
            "high_risk": len([f for f in result["findings"] if f.get('severity') == 'HIGH'])
        }
        
        print(f"   文件: {result['code_files']} 个")
        print(f"   风险: {len(result['findings'])} 项")
        
        return result
        
    def _find_issues(self, scan_result):
        """发现问题"""
        issues = []
        
        # 基于扫描结果发现问题
        findings = scan_result.get("findings", [])
        
        # 检查重复代码
        patterns = {}
        for f in findings:
            p = f.get("pattern", "")
            patterns[p] = patterns.get(p, 0) + 1
            
        # 生成问题
        for pattern, count in patterns.items():
            if count > 1:
                issues.append({
                    "type": "重复风险模式",
                    "detail": f"{pattern} 出现 {count} 次",
                    "severity": "MEDIUM"
                })
                
        # 检查缺失的功能
        project = Path(self.project_path)
        
        if not (project / "expert_mode" / "docker_sandbox.py").exists():
            issues.append({
                "type": "功能缺失",
                "detail": "缺少 Docker 沙箱支持",
                "severity": "HIGH"
            })
            
        if not (project / "expert_mode" / "whitelist.py").exists():
            issues.append({
                "type": "功能缺失",
                "detail": "缺少白名单机制",
                "severity": "MEDIUM"
            })
            
        return issues
        
    def _plan_improvements(self, issues):
        """制定改进计划"""
        improvements = []
        
        for issue in issues:
            if issue.get("type") == "功能缺失":
                if "Docker" in issue.get("detail", ""):
                    improvements.append({
                        "action": "添加Docker沙箱支持",
                        "priority": 1,
                        "issue": issue
                    })
                elif "白名单" in issue.get("detail", ""):
                    improvements.append({
                        "action": "添加白名单机制",
                        "priority": 2,
                        "issue": issue
                    })
                    
        return improvements
        
    async def _execute_improvement(self, improvement):
        """执行改进"""
        action = improvement.get("action", "")
        
        print(f"   执行: {action}")
        
        # 这里可以实现自动改进逻辑
        # 目前只是记录
        
    def _run_tests(self):
        """运行测试"""
        try:
            result = subprocess.run(
                [sys.executable, "expert_mode/test_expert.py"],
                cwd=self.project_path,
                capture_output=True,
                timeout=60
            )
            passed = result.returncode == 0
        except Exception as e:
            print(f"   测试错误: {e}")
            passed = False
            
        return {
            "passed": passed,
            "status": "OK" if passed else "FAILED"
        }
        
    async def run_forever(self, interval: int = 600):
        """持续循环改进
        
        Args:
            interval: 每次循环间隔(秒)
        """
        print(f"\n🚀 灵顺自我改进系统启动")
        print(f"📁 项目: {self.project_path}")
        print(f"⏱️  间隔: {interval}秒")
        
        while True:
            try:
                await self.improve_once()
                
                print(f"\n💤 等待 {interval}秒...")
                await asyncio.sleep(interval)
                
            except KeyboardInterrupt:
                print("\n\n🛑 停止")
                break
            except Exception as e:
                print(f"\n❌ 错误: {e}")
                await asyncio.sleep(60)


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="灵顺自我改进系统")
    parser.add_argument("--once", action="store_true", help="只运行一轮")
    parser.add_argument("--interval", type=int, default=600, help="循环间隔(秒)")
    parser.add_argument("--path", type=str, default=None, help="项目路径")
    
    args = parser.parse_args()
    
    project_path = args.path or str(Path(__file__).parent.parent)
    
    improver = LingshunSelfImprover(project_path)
    
    if args.once:
        await improver.improve_once()
    else:
        await improver.run_forever(args.interval)


if __name__ == "__main__":
    asyncio.run(main())
