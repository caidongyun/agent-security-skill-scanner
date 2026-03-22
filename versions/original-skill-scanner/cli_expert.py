#!/usr/bin/env python3
"""
Expert Mode - CLI 整合模块
自动决策引擎
"""

import argparse
import json
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from expert_mode.expert_sandbox import expert_mode_analyze
from expert_mode.risk_assessor import RiskRule, RiskAssessor


class AutoDecisionEngine:
    """自动决策引擎"""
    
    AUTO_EXPERT_THRESHOLD = 60
    FORCE_EXPERT_THRESHOLD = 80
    
    def __init__(self):
        pass
        
    async def scan_with_decision(self, skill_path: str, mode: str = "auto") -> dict:
        result = {
            "skill_path": skill_path,
            "mode": mode,
            "static_result": None,
            "expert_result": None,
            "final_decision": None
        }
        
        print("🔍 静态扫描...")
        static_result = await self._static_scan(skill_path)
        result["static_result"] = static_result
        
        risk_score = static_result.get("risk_score", 0)
        risk_level = static_result.get("risk_level", "UNKNOWN")
        
        print(f"   风险: {risk_score}/100 [{risk_level}]")
        
        need_expert = False
        
        if mode == "expert":
            need_expert = True
            reason = "用户指定专家模式"
        elif mode == "static":
            need_expert = False
            reason = "用户指定仅静态"
        elif mode == "auto":
            if risk_score >= self.FORCE_EXPERT_THRESHOLD:
                need_expert = True
                reason = f"高风险({risk_score}>)强制专家模式"
            elif risk_score >= self.AUTO_EXPERT_THRESHOLD:
                need_expert = True
                reason = f"中风险({risk_score}>)自动触发"
            else:
                reason = f"低风险({risk_score}<{self.AUTO_EXPERT_THRESHOLD})直接通过"
        
        if need_expert:
            print(f"🔬 专家模式: {reason}")
            try:
                expert_result = await expert_mode_analyze(skill_path)
                result["expert_result"] = expert_result
                
                final_score = int(risk_score * 0.4 + expert_result.get("risk_score", 0) * 0.6)
                final_level = self._get_level(final_score)
                
                result["final_decision"] = {
                    "risk_score": final_score,
                    "risk_level": final_level,
                    "recommendation": expert_result.get("recommendation", "需确认"),
                    "expert_triggered": True,
                    "reason": reason
                }
            except Exception as e:
                result["final_decision"] = {
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                    "recommendation": f"专家模式执行失败: {e}",
                    "expert_triggered": False,
                    "reason": f"静态:{reason}"
                }
        else:
            result["final_decision"] = {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "recommendation": self._get_recommendation(risk_score),
                "expert_triggered": False,
                "reason": reason
            }
            
        return result
        
    async def _static_scan(self, skill_path: str) -> dict:
        findings = []
        path = Path(skill_path)
        
        for ext in ['.py', '.js', '.sh']:
            for code_file in path.rglob(f'*{ext}'):
                try:
                    code = code_file.read_text(errors='ignore')
                    file_findings = RiskRule.match(code)
                    for f in file_findings:
                        f['file'] = str(code_file.relative_to(path))
                    findings.extend(file_findings)
                except:
                    pass
        
        assessor = RiskAssessor()
        result = assessor.assess(findings)
        
        return result
        
    def _get_level(self, score: int) -> str:
        if score > 100:
            return "CRITICAL"
        elif score > 60:
            return "HIGH"
        elif score > 30:
            return "MEDIUM"
        elif score > 10:
            return "LOW"
        else:
            return "SAFE"
            
    def _get_recommendation(self, score: int) -> str:
        if score > 100:
            return "🚫 立即拦截"
        elif score > 60:
            return "❌ 建议拦截"
        elif score > 30:
            return "⚠️ 需确认"
        else:
            return "✅ 安全通过"


def print_result(result: dict, verbose: bool = False):
    decision = result.get("final_decision", {})
    risk_score = decision.get("risk_score", 0)
    risk_level = decision.get("risk_level", "UNKNOWN")
    recommendation = decision.get("recommendation", "")
    reason = decision.get("reason", "")
    expert_triggered = decision.get("expert_triggered", False)
    
    level_emoji = {
        "CRITICAL": "🔴",
        "HIGH": "🟠", 
        "MEDIUM": "🟡",
        "LOW": "🔵",
        "SAFE": "✅"
    }
    
    emoji = level_emoji.get(risk_level, "⚪")
    
    print("\n" + "="*50)
    print(f"🔍 扫描完成")
    print("="*50)
    print(f"📊 风险评分: {risk_score}/100 {emoji} {risk_level}")
    print(f"🎯 建议: {recommendation}")
    print(f"💡 决策: {reason}")
    
    if expert_triggered:
        print(f"🔬 专家模式: 已执行")
        
    if verbose:
        static = result.get("static_result", {})
        if static.get("findings"):
            print("\n📋 发现问题:")
            for f in static["findings"][:10]:
                print(f"  • {f.get('description', f.get('pattern', 'Unknown'))}")
                
    print("="*50 + "\n")


async def main():
    parser = argparse.ArgumentParser(description="Skill Scanner Expert Mode")
    parser.add_argument("skill_path", help="Skill路径")
    parser.add_argument("--mode", choices=["auto", "expert", "static"], default="auto",
                        help="扫描模式: auto(AI自动)/expert(强制专家)/static(仅静态)")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--json", action="store_true", help="JSON输出")
    
    args = parser.parse_args()
    
    engine = AutoDecisionEngine()
    result = await engine.scan_with_decision(args.skill_path, args.mode)
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_result(result, args.verbose)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
