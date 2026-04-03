#!/usr/bin/env python3
"""
UltraReview - 深度审查 Agent
代码/决策/规划全方位审查
"""
import os, json, re
from datetime import datetime
from pathlib import Path

class UltraReview:
    def __init__(self):
        self.review_templates = {
            'code': self.review_code,
            'decision': self.review_decision,
            'plan': self.review_plan,
            'all': self.review_all,
        }
        
    def review(self, target, type='code', deep=False):
        """执行审查"""
        print(f"[{datetime.now()}] 🔍 开始审查：{type}")
        
        review_func = self.review_templates.get(type, self.review_code)
        result = review_func(target, deep)
        
        # 添加审查元数据
        result['reviewed_at'] = datetime.now().isoformat()
        result['type'] = type
        result['deep'] = deep
        
        # 保存审查报告
        self.save_review_report(result)
        
        return result
        
    def review_code(self, code, deep=False):
        """代码审查"""
        issues = []
        suggestions = []
        
        # 1. 正确性检查
        issues.extend(self.check_correctness(code))
        
        # 2. 可靠性检查
        issues.extend(self.check_reliability(code))
        
        # 3. 可维护性检查
        issues.extend(self.check_maintainability(code))
        
        # 4. 性能检查 (深度模式)
        if deep:
            issues.extend(self.check_performance(code))
            
        # 5. 安全性检查 (深度模式)
        if deep:
            issues.extend(self.check_security(code))
            
        # 计算分数
        score = self.calculate_score(issues)
        
        return {
            'score': score,
            'level': self.score_to_level(score),
            'issues': issues,
            'suggestions': suggestions,
            'passed': score >= 0.8,
        }
        
    def check_correctness(self, code):
        """正确性检查"""
        issues = []
        
        # 检查常见错误模式
        if 'eval(' in code and 'input(' in code:
            issues.append({
                'type': 'bug',
                'severity': 'critical',
                'description': 'eval + input 组合存在安全风险',
            })
            
        if 'while True' in code and 'break' not in code:
            issues.append({
                'type': 'bug',
                'severity': 'high',
                'description': '可能存在死循环',
            })
            
        return issues
        
    def check_reliability(self, code):
        """可靠性检查"""
        issues = []
        
        if 'try:' not in code and 'open(' in code:
            issues.append({
                'type': 'reliability',
                'severity': 'medium',
                'description': '文件操作缺少异常处理',
            })
            
        return issues
        
    def check_maintainability(self, code):
        """可维护性检查"""
        issues = []
        
        # 检查函数长度
        if code.count('\n') > 100:
            issues.append({
                'type': 'maintainability',
                'severity': 'low',
                'description': '代码过长，建议拆分',
            })
            
        # 检查注释
        if code.count('#') < code.count('\n') * 0.1:
            issues.append({
                'type': 'maintainability',
                'severity': 'low',
                'description': '注释不足',
            })
            
        return issues
        
    def check_performance(self, code):
        """性能检查"""
        issues = []
        
        if 'for' in code and 'open(' in code:
            issues.append({
                'type': 'performance',
                'severity': 'medium',
                'description': '循环内文件操作可能影响性能',
            })
            
        return issues
        
    def check_security(self, code):
        """安全性检查"""
        issues = []
        
        if 'password' in code.lower() and '=' in code:
            issues.append({
                'type': 'security',
                'severity': 'high',
                'description': '可能存在硬编码密码',
            })
            
        return issues
        
    def review_decision(self, decision, deep=False):
        """决策审查"""
        issues = []
        
        # 检查决策逻辑
        if isinstance(decision, dict):
            if 'criteria' not in decision:
                issues.append({
                    'type': 'logic',
                    'severity': 'medium',
                    'description': '决策缺少明确标准',
                })
                
        return {
            'score': 1.0 - len(issues) * 0.2,
            'level': 'A' if len(issues) == 0 else 'B',
            'issues': issues,
            'suggestions': ['建议添加决策标准文档'],
            'passed': len(issues) == 0,
        }
        
    def review_plan(self, plan, deep=False):
        """规划审查"""
        issues = []
        
        # 检查规划完整性
        if isinstance(plan, dict):
            required_fields = ['goals', 'tasks', 'timeline']
            for field in required_fields:
                if field not in plan:
                    issues.append({
                        'type': 'completeness',
                        'severity': 'medium',
                        'description': f'规划缺少 {field}',
                    })
                    
        return {
            'score': 1.0 - len(issues) * 0.2,
            'level': 'A' if len(issues) == 0 else 'B',
            'issues': issues,
            'suggestions': ['建议完善规划文档结构'],
            'passed': len(issues) == 0,
        }
        
    def review_all(self, target, deep=False):
        """全方位审查"""
        code_result = self.review_code(target, deep)
        decision_result = self.review_decision({}, deep)
        plan_result = self.review_plan({}, deep)
        
        return {
            'code_review': code_result,
            'decision_review': decision_result,
            'plan_review': plan_result,
            'overall_score': (code_result['score'] + decision_result['score'] + plan_result['score']) / 3,
            'passed': code_result['passed'] and decision_result['passed'] and plan_result['passed'],
        }
        
    def calculate_score(self, issues):
        """计算分数"""
        severity_weights = {
            'critical': 0.3,
            'high': 0.2,
            'medium': 0.1,
            'low': 0.05,
        }
        
        deduction = sum(severity_weights.get(issue['severity'], 0.1) for issue in issues)
        return max(0.0, 1.0 - deduction)
        
    def score_to_level(self, score):
        """分数转等级"""
        if score >= 0.9:
            return 'S'
        elif score >= 0.8:
            return 'A'
        elif score >= 0.7:
            return 'B'
        elif score >= 0.6:
            return 'C'
        else:
            return 'D'
            
    def save_review_report(self, result):
        """保存审查报告"""
        os.makedirs('reports/reviews', exist_ok=True)
        report_file = f"reports/reviews/review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(result, f, indent=2)
            
        print(f"📄 审查报告已保存：{report_file}")

if __name__ == '__main__':
    import sys
    
    reviewer = UltraReview()
    
    if len(sys.argv) > 2:
        review_type = sys.argv[1]
        target = sys.argv[2]
        
        # 读取目标文件
        if os.path.exists(target):
            with open(target) as f:
                content = f.read()
        else:
            content = target
            
        result = reviewer.review(content, type=review_type, deep='--deep' in sys.argv)
        
        print(f"\n{'='*60}")
        print(f"审查结果:")
        print(f"  分数：{result.get('overall_score', result.get('score', 0)):.2f}")
        print(f"  等级：{result.get('level', 'N/A')}")
        print(f"  通过：{'✅' if result.get('passed') else '❌'}")
        print(f"  问题数：{len(result.get('issues', []))}")
        print(f"{'='*60}")
    else:
        print("用法：python3 main.py --review <type> <target> [--deep]")
        print("类型：code, decision, plan, all")
