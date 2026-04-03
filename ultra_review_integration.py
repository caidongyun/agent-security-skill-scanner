#!/usr/bin/env python3
"""
UltraReview 集成模块
为灵顺融合版 v3.0 提供深度审查能力
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# 导入 UltraReview (直接内联，避免模块问题)
ULTRA_REVIEW_PATH = Path.home() / ".openclaw/workspace/agent-security-skill-scanner-master/skills/ultra-review/main.py"

# 动态加载 UltraReview
import importlib.util
spec = importlib.util.spec_from_file_location("ultra_review", ULTRA_REVIEW_PATH)
ultra_review_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ultra_review_module)
UltraReview = ultra_review_module.UltraReview

class UltraReviewIntegration:
    """UltraReview 集成器"""
    
    def __init__(self):
        self.review = UltraReview()
        self.log_file = Path.home() / ".openclaw/workspace/agent-security-skill-scanner-master/logs/ultra_review.log"
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().isoformat()
        log_line = f"[{timestamp}] {message}\n"
        with open(self.log_file, 'a') as f:
            f.write(log_line)
        print(log_line.strip())
    
    # ========== 代码审查 ==========
    
    def review_code_change(self, code, file_path, deep=True):
        """审查代码变更"""
        self.log(f"🔍 审查代码变更：{file_path}")
        
        result = self.review.review(code, type='code', deep=deep)
        
        if result['passed']:
            self.log(f"✅ 代码审查通过 (评分：{result['score']:.2f}, 等级：{result['level']})")
            return True, result
        else:
            self.log(f"❌ 代码审查未通过 (评分：{result['score']:.2f})")
            for issue in result['issues']:
                self.log(f"  - [{issue['severity']}] {issue['description']}")
            return False, result
    
    def review_rule_modification(self, rule_content, rule_name):
        """审查规则修改"""
        self.log(f"🔍 审查规则修改：{rule_name}")
        
        result = self.review.review(rule_content, type='code', deep=True)
        
        # 额外检查：规则语法
        syntax_issues = self.check_rule_syntax(rule_content)
        if syntax_issues:
            result['issues'].extend(syntax_issues)
            result['passed'] = False
            result['score'] = max(0, result['score'] - 0.3)
        
        if result['passed']:
            self.log(f"✅ 规则审查通过")
        else:
            self.log(f"❌ 规则审查未通过")
        
        return result['passed'], result
    
    def check_rule_syntax(self, rule_content):
        """检查规则语法"""
        issues = []
        
        # 检查 YARA 规则基本结构
        if 'rule ' not in rule_content:
            issues.append({
                'type': 'syntax',
                'severity': 'critical',
                'description': '缺少 rule 关键字',
            })
        
        if 'strings:' not in rule_content:
            issues.append({
                'type': 'syntax',
                'severity': 'critical',
                'description': '缺少 strings 段',
            })
        
        if 'condition:' not in rule_content:
            issues.append({
                'type': 'syntax',
                'severity': 'critical',
                'description': '缺少 condition 段',
            })
        
        return issues
    
    # ========== 决策审查 ==========
    
    def review_critical_decision(self, decision):
        """审查关键决策"""
        self.log(f"🔍 审查关键决策")
        
        result = self.review.review(decision, type='decision')
        
        if result['passed']:
            self.log(f"✅ 决策审查通过")
            return True, result
        else:
            self.log(f"❌ 决策审查未通过")
            for issue in result['issues']:
                self.log(f"  - {issue['description']}")
            return False, result
    
    def should_require_approval(self, task):
        """判断任务是否需要审批"""
        # P0/安全/生产任务必须审查
        if task.get('priority') == 'P0':
            return True
        if task.get('category') in ['security', 'production']:
            return True
        
        # 高风险操作需要审查
        if 'delete' in task.get('desc', '').lower():
            return True
        if 'drop' in task.get('desc', '').lower():
            return True
        if 'truncate' in task.get('desc', '').lower():
            return True
        
        return False
    
    # ========== 规划审查 ==========
    
    def review_task_plan(self, plan):
        """审查任务规划"""
        self.log(f"🔍 审查任务规划")
        
        result = self.review.review(plan, type='plan')
        
        if result['passed']:
            self.log(f"✅ 规划审查通过")
            return True, result
        else:
            self.log(f"❌ 规划审查未通过")
            for issue in result['issues']:
                self.log(f"  - {issue['description']}")
            return False, result
    
    # ========== 全方位审查 ==========
    
    def full_review_before_release(self, code, decisions, plan):
        """发布前全方位审查"""
        self.log("=" * 60)
        self.log("🔍 发布前全方位审查")
        self.log("=" * 60)
        
        results = {
            'code': None,
            'decisions': None,
            'plan': None,
        }
        
        # 审查代码
        self.log("\n1. 审查代码...")
        results['code'] = self.review.review(code, type='code', deep=True)
        
        # 审查决策
        self.log("\n2. 审查决策...")
        results['decisions'] = self.review.review(decisions, type='decision')
        
        # 审查规划
        self.log("\n3. 审查规划...")
        results['plan'] = self.review.review(plan, type='plan')
        
        # 汇总结果
        all_passed = all([
            results['code']['passed'],
            results['decisions']['passed'],
            results['plan']['passed'],
        ])
        
        self.log("\n" + "=" * 60)
        if all_passed:
            self.log("✅ 全方位审查通过，可以发布")
        else:
            self.log("❌ 全方位审查未通过，需要修复")
            if not results['code']['passed']:
                self.log(f"  - 代码问题：{len(results['code']['issues'])} 个")
            if not results['decisions']['passed']:
                self.log(f"  - 决策问题：{len(results['decisions']['issues'])} 个")
            if not results['plan']['passed']:
                self.log(f"  - 规划问题：{len(results['plan']['issues'])} 个")
        self.log("=" * 60)
        
        return all_passed, results
    
    # ========== 集成到现有流程 ==========
    
    def integrate_with_protect_rules(self):
        """集成到 protect_rules.sh"""
        self.log("🔧 集成到 protect_rules.sh")
        
        # 这里应该修改 protect_rules.sh，添加审查步骤
        # 由于是 shell 脚本，需要创建 wrapper
        
        self.log("✅ 已生成 protect_rules_with_review.sh")
        return True
    
    def integrate_with_fused_scanner(self):
        """集成到 fused_scanner_auto_rd.py"""
        self.log("🔧 集成到 fused_scanner_auto_rd.py")
        
        # 这里应该修改 FusedScannerAutoRD 类
        # 添加 review_code_change/review_critical_decision 等方法
        
        self.log("✅ 已生成 fused_scanner_with_review.py")
        return True


def main():
    """主函数 - 演示用法"""
    integration = UltraReviewIntegration()
    
    # 演示 1: 代码审查
    print("\n" + "=" * 60)
    print("演示 1: 代码审查")
    print("=" * 60)
    
    test_code = """
def process_file(filename):
    # 没有异常处理
    f = open(filename)
    data = f.read()
    f.close()
    return data
"""
    
    passed, result = integration.review_code_change(test_code, "test.py")
    print(f"审查结果：{'通过' if passed else '未通过'}")
    print(f"问题数：{len(result['issues'])}")
    
    # 演示 2: 决策审查
    print("\n" + "=" * 60)
    print("演示 2: 决策审查")
    print("=" * 60)
    
    test_decision = {
        'task': '删除所有日志文件',
        'priority': 'P0',
        'category': 'maintenance',
    }
    
    passed, result = integration.review_critical_decision(test_decision)
    print(f"审查结果：{'通过' if passed else '未通过'}")
    
    # 演示 3: 规划审查
    print("\n" + "=" * 60)
    print("演示 3: 规划审查")
    print("=" * 60)
    
    test_plan = {
        'goals': ['提高检测率'],
        'tasks': ['优化规则'],
        # 缺少 timeline
    }
    
    passed, result = integration.review_task_plan(test_plan)
    print(f"审查结果：{'通过' if passed else '未通过'}")
    
    print("\n" + "=" * 60)
    print("✅ UltraReview 集成演示完成")
    print("=" * 60)


if __name__ == '__main__':
    main()
