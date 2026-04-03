#!/usr/bin/env python3
"""
🔍 Code Review Agent - 自动审查规则代码
========================================
功能:
- 静态分析规则代码
- 检查安全问题
- 验证测试覆盖
- 生成审查报告

使用方式:
    python3 code_review_agent.py --rule TP-RUNTIME-001
    python3 code_review_agent.py --attack-type tool_poisoning
    python3 code_review_agent.py --all
"""

import os
import sys
import json
import re
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime


# 审查维度权重
WEIGHTS = {
    "functionality": 0.30,  # 功能正确性
    "quality": 0.20,        # 代码质量
    "security": 0.25,       # 安全性
    "performance": 0.15,    # 性能
    "testing": 0.10        # 测试覆盖
}


@dataclass
class ReviewIssue:
    """审查问题"""
    line: int
    severity: str  # HIGH, MEDIUM, LOW, INFO
    category: str  # functionality, quality, security, performance, testing
    description: str
    suggestion: str


@dataclass
class ReviewResult:
    """审查结果"""
    rule_id: str
    score: float  # 0-100
    issues: List[ReviewIssue]
    approved: bool
    summary: str


class CodeReviewAgent:
    """Code Review Agent"""
    
    def __init__(self, rules_dir: Path):
        # 使用绝对路径
        self.rules_dir = rules_dir.resolve()
    
    def load_rule(self, rule_id: str) -> Dict:
        """加载规则"""
        # 遍历所有规则文件
        for rule_file in self.rules_dir.rglob("*.json"):
            if rule_file.name.startswith("."):
                continue
            try:
                with open(rule_file) as f:
                    data = json.load(f)
                    # 检查 ID 是否匹配
                    if data.get("id", "").upper() == rule_id.upper():
                        return data
            except:
                pass
        return None
    
    def load_test_cases(self, attack_type: str) -> List[Dict]:
        """加载测试用例"""
        test_file = self.rules_dir.parent / "tests" / "cases" / f"{attack_type}.json"
        if test_file.exists():
            with open(test_file) as f:
                return json.load(f)
        return []
    
    def check_functionality(self, rule: Dict) -> List[ReviewIssue]:
        """检查功能正确性"""
        issues = []
        
        # 检查必要字段
        required_fields = ["id", "name", "category", "patterns"]
        for field in required_fields:
            if field not in rule:
                issues.append(ReviewIssue(
                    line=0,
                    severity="HIGH",
                    category="functionality",
                    description=f"缺少必要字段: {field}",
                    suggestion=f"添加 {field} 字段"
                ))
        
        # 检查 patterns 非空
        if not rule.get("patterns"):
            issues.append(ReviewIssue(
                line=0,
                severity="HIGH",
                category="functionality",
                description="patterns 为空",
                suggestion="添加检测模式"
            ))
        
        return issues
    
    def check_quality(self, rule: Dict) -> List[ReviewIssue]:
        """检查代码质量"""
        issues = []
        
        # 检查命名
        name = rule.get("name", "")
        if len(name) < 5:
            issues.append(ReviewIssue(
                line=0,
                severity="LOW",
                category="quality",
                description="规则名称过短",
                suggestion="使用更描述性的名称"
            ))
        
        # 检查描述
        desc = rule.get("description", "")
        if len(desc) < 10:
            issues.append(ReviewIssue(
                line=0,
                severity="MEDIUM",
                category="quality",
                description="描述信息不足",
                suggestion="添加详细的规则描述"
            ))
        
        return issues
    
    def check_security(self, rule: Dict) -> List[ReviewIssue]:
        """检查安全性"""
        issues = []
        
        # 检查正则表达式安全性
        patterns = rule.get("patterns", [])
        dangerous_patterns = [
            (r".*\*\+.*", "可能导致正则爆炸"),
            (r".*\.\*.*", "可能匹配过多"),
            (r".*\+.*\+.*", "可能导致回溯")
        ]
        
        for i, pattern in enumerate(patterns):
            for danger, desc in dangerous_patterns:
                if re.search(danger, pattern):
                    issues.append(ReviewIssue(
                        line=i,
                        severity="HIGH",
                        category="security",
                        description=f"危险正则: {pattern[:30]}... - {desc}",
                        suggestion="优化正则表达式"
                    ))
        
        return issues
    
    def check_testing(self, rule: Dict, attack_type: str) -> List[ReviewIssue]:
        """检查测试覆盖"""
        issues = []
        
        # 检查是否有 test_cases
        if "test_cases" not in rule:
            issues.append(ReviewIssue(
                line=0,
                severity="MEDIUM",
                category="testing",
                description="缺少 test_cases 定义",
                suggestion="添加测试用例"
            ))
        
        # 检查测试用例数量
        test_cases = rule.get("test_cases", {})
        positive = test_cases.get("positive", [])
        negative = test_cases.get("negative", [])
        
        if len(positive) < 2:
            issues.append(ReviewIssue(
                line=0,
                severity="MEDIUM",
                category="testing",
                description=f"正向测试用例不足: {len(positive)} 个",
                suggestion="至少添加 2 个正向测试用例"
            ))
        
        if len(negative) < 1:
            issues.append(ReviewIssue(
                line=0,
                severity="LOW",
                category="testing",
                description="缺少负向测试用例",
                suggestion="添加负向测试用例"
            ))
        
        return issues
    
    def review_rule(self, rule_id: str) -> ReviewResult:
        """审查单个规则"""
        rule = self.load_rule(rule_id)
        
        if not rule:
            return ReviewResult(
                rule_id=rule_id,
                score=0,
                issues=[ReviewIssue(0, "HIGH", "functionality", "规则不存在", "")],
                approved=False,
                summary="规则不存在"
            )
        
        all_issues = []
        
        # 执行各项检查
        all_issues.extend(self.check_functionality(rule))
        all_issues.extend(self.check_quality(rule))
        all_issues.extend(self.check_security(rule))
        
        attack_type = rule.get("category", "")
        all_issues.extend(self.check_testing(rule, attack_type))
        
        # 计算分数
        score = 100
        for issue in all_issues:
            if issue.severity == "HIGH":
                score -= 20
            elif issue.severity == "MEDIUM":
                score -= 10
            elif issue.severity == "LOW":
                score -= 5
        
        score = max(0, score)
        
        # 判断是否通过
        approved = score >= 70 and not any(
            i.severity == "HIGH" and i.category == "security" 
            for i in all_issues
        )
        
        return ReviewResult(
            rule_id=rule_id,
            score=score,
            issues=all_issues,
            approved=approved,
            summary=f"得分: {score}/100, 问题数: {len(all_issues)}"
        )
    
    def review_all(self) -> List[ReviewResult]:
        """审查所有规则"""
        results = []
        
        for rule_file in self.rules_dir.rglob("*.json"):
            if rule_file.name.startswith("."):
                continue
            
            try:
                with open(rule_file) as f:
                    rule = json.load(f)
                
                rule_id = rule.get("id", rule_file.stem)
                result = self.review_rule(rule_id)
                results.append(result)
            except:
                pass
        
        return results
    
    def print_result(self, result: ReviewResult):
        """打印审查结果"""
        status = "✅" if result.approved else "❌"
        
        print(f"\n{'='*60}")
        print(f"{status} 规则审查: {result.rule_id}")
        print(f"{'='*60}")
        print(f"分数: {result.score}/100")
        print(f"状态: {'通过' if result.approved else '需要修改'}")
        
        if result.issues:
            print(f"\n发现问题 ({len(result.issues)} 个):")
            
            # 按严重程度排序
            severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "INFO": 3}
            sorted_issues = sorted(
                result.issues, 
                key=lambda x: severity_order.get(x.severity, 3)
            )
            
            for issue in sorted_issues:
                icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢", "INFO": "🔵"}[issue.severity]
                print(f"  {icon} [{issue.severity}] {issue.description}")
                print(f"     → {issue.suggestion}")
        
        print(f"\n{result.summary}")
    
    def generate_report(self, results: List[ReviewResult]) -> Dict:
        """生成审查报告"""
        
        # 统计
        total = len(results)
        approved = sum(1 for r in results if r.approved)
        
        # 按类别统计
        by_category = {}
        for r in results:
            for issue in r.issues:
                cat = issue.category
                by_category[cat] = by_category.get(cat, 0) + 1
        
        # 按严重程度统计
        by_severity = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for r in results:
            for issue in r.issues:
                if issue.severity in by_severity:
                    by_severity[issue.severity] += 1
        
        return {
            "generated_at": datetime.now().isoformat(),
            "total_rules": total,
            "approved": approved,
            "approval_rate": f"{approved/total*100:.1f}%" if total > 0 else "0%",
            "avg_score": sum(r.score for r in results) / total if total > 0 else 0,
            "issues_by_category": by_category,
            "issues_by_severity": by_severity
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="🔍 Code Review Agent")
    parser.add_argument("--rule", type=str, help="审查单个规则")
    parser.add_argument("--attack-type", type=str, help="按攻击类型审查")
    parser.add_argument("--all", action="store_true", help="审查所有规则")
    parser.add_argument("--report", action="store_true", help="生成报告")
    
    args = parser.parse_args()
    
    # 初始化
    script_dir = Path(__file__).parent
    rules_dir = script_dir / "rules"
    
    agent = CodeReviewAgent(rules_dir)
    
    if args.rule:
        # 审查单个规则
        result = agent.review_rule(args.rule)
        agent.print_result(result)
    
    elif args.all or args.attack_type:
        # 审查所有规则
        results = agent.review_all()
        
        if args.attack_type:
            results = [r for r in results if r.rule_id.startswith(args.attack_type[:2].upper())]
        
        for result in results:
            agent.print_result(result)
        
        # 生成报告
        if args.report:
            report = agent.generate_report(results)
            print(f"\n{'='*60}")
            print(f"📊 审查报告摘要")
            print(f"{'='*60}")
            print(f"总规则数: {report['total_rules']}")
            print(f"通过: {report['approved']} ({report['approval_rate']})")
            print(f"平均分: {report['avg_score']:.1f}")
            print(f"\n问题分类:")
            for cat, count in report['issues_by_category'].items():
                print(f"  {cat}: {count}")
            print(f"\n严重程度:")
            for sev, count in report['issues_by_severity'].items():
                print(f"  {sev}: {count}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
