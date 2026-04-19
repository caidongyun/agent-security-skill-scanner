#!/usr/bin/env python3
"""
改进测试用例 - 区分 should_match 和 should_not_match
"""

import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ImproveTests')

WORKSPACE_DIR = Path('/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/release/v5.8.0')
TEST_CASES_DIR = WORKSPACE_DIR / 'tests' / 'pattern_test_cases'

def improve():
    """改进测试用例"""
    logger.info("📝 改进测试用例")
    
    # 创建 exec/eval测试目录
    exec_dir = TEST_CASES_DIR / 'exec_eval'
    exec_dir.mkdir(parents=True, exist_ok=True)
    
    # 阳性测试用例 (应该匹配)
    positive_tests = {
        'test_exec_direct.py': """
# Direct exec call
code = "print('hello')"
exec(code)
""",
        'test_exec_with_source.py': """
# Exec with source
exec("x = 1", {}, {})
""",
        'test_eval_direct.py': """
# Direct eval call
result = eval("1 + 2")
""",
        'test_eval_expression.py': """
# Eval expression
value = eval(user_input)
""",
    }
    
    # 阴性测试用例 (不应匹配)
    negative_tests = {
        'test_safe_execute.py': """
# Safe function named execute
def execute_task(task):
    '''Execute a task safely'''
    print(f"Executing: {task}")
    return True
""",
        'test_safe_evaluator.py': """
# Safe class named Evaluator
class Evaluator:
    '''An evaluator class'''
    def evaluate(self, item):
        return item.score
""",
        'test_comment_exec.py': """
# This is a comment about exec
# But no actual exec call
print("Hello")
""",
        'test_string_exec.py': """
# String containing word exec
description = "The exec function is dangerous"
print(description)
""",
    }
    
    # 写入阳性测试
    for filename, content in positive_tests.items():
        filepath = exec_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"  ✅ 创建阳性测试：{filepath.name}")
    
    # 写入阴性测试
    for filename, content in negative_tests.items():
        filepath = exec_dir / f"safe_{filename}" if not filename.startswith('safe_') else exec_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"  ✅ 创建阴性测试：{filepath.name}")
    
    logger.info(f"✅ 测试用例改进完成")
    return {'positive': len(positive_tests), 'negative': len(negative_tests)}

if __name__ == '__main__':
    result = improve()
    print(f"创建测试用例：{result}")
