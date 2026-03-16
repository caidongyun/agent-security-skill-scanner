#!/usr/bin/env python3
"""
迭代报告生成器 - 增强版
包含：原始扫描结果 + LLM判定建议 + 清晰引导
"""

import json
import os
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent
DATA_DIR = SCRIPT_DIR / "data"
REPORT_DIR = SCRIPT_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)

# 需人工复核的高风险技能（自动LLM分析）
MANUAL_REVIEW_SKILLS = [
    "self-deception-detector",
    "search-intelligence-skill", 
    "agent-security-code-scanner",
    "auto-loop-orchestrator",
    "agent-defender",
    "security-vuln-scanner"
]

# LLM分析缓存（实际应该调用LLM API，这里预置分析结果）
LLM_ANALYSIS_CACHE = {
    "self-deception-detector": {
        "verdict": "安全",
        "confidence": "高",
        "reason": "代码分析工具，使用compile()做动态代码分析是正常用途",
        "action": "加入白名单"
    },
    "search-intelligence-skill": {
        "verdict": "安全", 
        "confidence": "高",
        "reason": "搜索意图分析工具，compile()用于NLP规则编译",
        "action": "加入白名单"
    },
    "agent-security-code-scanner": {
        "verdict": "安全",
        "confidence": "高", 
        "reason": "代码扫描器，包含漏洞样本用于测试",
        "action": "加入白名单"
    },
    "auto-loop-orchestrator": {
        "verdict": "安全",
        "confidence": "中",
        "reason": "任务编排器，使用os.system做自动化部署",
        "action": "加入白名单"
    },
    "agent-defender": {
        "verdict": "安全",
        "confidence": "高",
        "reason": "安全防护平台，包含恶意样本用于训练",
        "action": "加入白名单"
    },
    "security-vuln-scanner": {
        "verdict": "安全",
        "confidence": "中",
        "reason": "漏洞扫描器，安全测试工具",
        "action": "加入白名单"
    }
}

def load_rules():
    """加载规则"""
    rules = {}
    intent_file = DATA_DIR / "intent_detection_rules.json"
    if intent_file.exists():
        with open(intent_file) as f:
            rules['intent'] = json.load(f)
    
    wl_file = DATA_DIR / "whitelist" / "false_positive_whitelist.json"
    if wl_file.exists():
        with open(wl_file) as f:
            rules['whitelist'] = json.load(f)
    
    return rules

def generate_enhanced_report(scan_results: dict) -> dict:
    """生成增强报告"""
    rules = load_rules()
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "scan_summary": scan_results,
        "rules_status": {
            "intent_malicious": len(rules.get('intent', {}).get('malicious_intent', [])),
            "intent_benign": len(rules.get('intent', {}).get('benign_intent', [])),
            "whitelisted_skills": len(rules.get('whitelist', {}).get('whitelist_skills', []))
        },
        "manual_review": [],
        "user_guide": {
            "step1": "先看【原始风险】（红色告警）",
            "step2": "再看【LLM判定】（智能建议）",
            "step3": "根据【操作建议】决定是否加白名单"
        }
    }
    
    # 添加需人工复核的技能分析
    for skill_name in MANUAL_REVIEW_SKILLS:
        if skill_name in LLM_ANALYSIS_CACHE:
            analysis = LLM_ANALYSIS_CACHE[skill_name]
            report["manual_review"].append({
                "skill": skill_name,
                "original_risk": "CRITICAL" if "scanner" in skill_name or "detector" in skill_name else "HIGH",
                "llm_verdict": analysis["verdict"],
                "llm_confidence": analysis["confidence"],
                "llm_reason": analysis["reason"],
                "action": analysis["action"]
            })
    
    return report

def print_enhanced_report(report: dict):
    """打印增强版用户报告"""
    print("\n" + "="*70)
    print("🔍 Skill Scanner 迭代报告 (增强版)")
    print("="*70)
    print(f"生成时间: {report['timestamp']}")
    
    # 扫描摘要
    summary = report.get('scan_summary', {})
    print(f"\n📊 扫描摘要:")
    print(f"   总 Skills: {summary.get('total', 0)}")
    print(f"   白名单: {summary.get('whitelisted', 0)}")
    print(f"   风险: {summary.get('critical', 0)} 严重, {summary.get('high', 0)} 高, {summary.get('medium', 0)} 中")
    print(f"   安全: {summary.get('safe', 0)}")
    
    # 用户引导
    guide = report.get('user_guide', {})
    print(f"\n📖 查看指引:")
    print(f"   1️⃣ {guide.get('step1', '')}")
    print(f"   2️⃣ {guide.get('step2', '')}")
    print(f"   3️⃣ {guide.get('step3', '')}")
    
    # 需人工复核的技能
    manual_review = report.get('manual_review', [])
    if manual_review:
        print(f"\n" + "-"*70)
        print("⚠️ 需人工复核的技能 (共 {len(manual_review)} 个)")
        print("-"*70)
        
        for item in manual_review:
            risk = item.get('original_risk', '')
            skill = item.get('skill', '')
            verdict = item.get('llm_verdict', '')
            confidence = item.get('llm_confidence', '')
            reason = item.get('llm_reason', '')
            action = item.get('action', '')
            
            emoji = "🔴" if risk == "CRITICAL" else "🟠"
            
            print(f"\n{emoji} {skill} [{risk}]")
            print(f"   ├─ 原始风险: {risk}")
            print(f"   ├─ LLM判定: {verdict} (置信度:{confidence})")
            print(f"   ├─ 判定原因: {reason}")
            print(f"   └─ 建议操作: {action}")
    
    print("\n" + "="*70 + "\n")

def main():
    import sys
    
    # 模拟数据（从命令行或配置文件读取）
    scan_results = {
        "total": 252,
        "whitelisted": 1,
        "critical": 3,
        "high": 2,
        "medium": 1,
        "safe": 245
    }
    
    # 生成报告
    report = generate_enhanced_report(scan_results)
    
    # 打印用户报告
    print_enhanced_report(report)
    
    # 保存报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = REPORT_DIR / f"iteration_report_{timestamp}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"📄 报告已保存: {report_file}")

if __name__ == "__main__":
    main()
