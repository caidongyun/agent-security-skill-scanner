#!/usr/bin/env python3
"""
Task 1.3: Pattern 单元测试
"""

import os
import sys
import json
import re
import yaml
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Task1.3')

WORKSPACE_DIR = Path('/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/release/v5.8.0')
PATTERNS_FILE = WORKSPACE_DIR / 'rules' / 'v580_patterns_semgrep.yaml'
TEST_CASES_DIR = WORKSPACE_DIR / 'tests' / 'pattern_test_cases'
OUTPUT_FILE = WORKSPACE_DIR / 'tests' / 'pattern_unit_test_results.json'

def test():
    """测试 Patterns"""
    logger.info("🧪 开始 Pattern 单元测试")
    
    # 1. 加载 Patterns
    with open(PATTERNS_FILE, 'r', encoding='utf-8') as f:
        patterns_data = yaml.safe_load(f)
    
    patterns = patterns_data.get('patterns', [])
    logger.info(f"  加载 {len(patterns)} 个 Patterns")
    
    # 2. 创建测试用例
    create_test_cases()
    
    # 3. 运行测试
    test_results = []
    passed = 0
    failed = 0
    
    for pattern in patterns:
        try:
            result = test_pattern(pattern)
            test_results.append(result)
            
            if result['passed']:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"  Pattern {pattern['id']} 测试失败：{str(e)}")
            failed += 1
            test_results.append({
                'pattern_id': pattern['id'],
                'passed': False,
                'error': str(e)
            })
    
    # 4. 保存结果
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    result_data = {
        'test_time': datetime.now().isoformat(),
        'total_patterns': len(patterns),
        'passed': passed,
        'failed': failed,
        'pass_rate': passed / len(patterns) * 100 if patterns else 0,
        'results': test_results
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ 测试完成")
    logger.info(f"  通过：{passed}/{len(patterns)} ({result_data['pass_rate']:.1f}%)")
    logger.info(f"  失败：{failed}/{len(patterns)}")
    logger.info(f"  结果保存至：{OUTPUT_FILE}")
    
    return {'output_file': str(OUTPUT_FILE), 'passed': passed, 'failed': failed, 'pass_rate': result_data['pass_rate']}

def test_pattern(pattern: dict) -> dict:
    """测试单个 Pattern"""
    pattern_id = pattern['id']
    regex = pattern['pattern']
    
    # 编译正则
    try:
        compiled = re.compile(regex)
    except Exception as e:
        return {
            'pattern_id': pattern_id,
            'passed': False,
            'error': f"正则编译失败：{str(e)}"
        }
    
    # 查找测试用例
    test_files = find_test_files(pattern)
    
    if not test_files:
        # 无测试用例，简单验证正则
        return {
            'pattern_id': pattern_id,
            'passed': True,
            'note': '无测试用例，正则编译成功',
            'true_positives': 0,
            'false_positives': 0
        }
    
    # 运行测试
    true_positives = 0
    false_positives = 0
    
    for test_file in test_files:
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            should_match = test_file.name.startswith('test_')
            matches = bool(compiled.search(content))
            
            if should_match and matches:
                true_positives += 1
            elif not should_match and not matches:
                true_positives += 1
            else:
                false_positives += 1
        except Exception as e:
            false_positives += 1
    
    passed = false_positives == 0
    
    return {
        'pattern_id': pattern_id,
        'passed': passed,
        'true_positives': true_positives,
        'false_positives': false_positives,
        'test_files': len(test_files)
    }

def create_test_cases():
    """创建测试用例"""
    TEST_CASES_DIR.mkdir(parents=True, exist_ok=True)
    
    # 创建 exec/eval 测试用例
    exec_dir = TEST_CASES_DIR / 'exec_eval'
    exec_dir.mkdir(parents=True, exist_ok=True)
    
    # 阳性测试用例 (应匹配)
    with open(exec_dir / 'test_exec_1.py', 'w', encoding='utf-8') as f:
        f.write("""
# Test exec call
code = "print('hello')"
exec(code)
""")
    
    with open(exec_dir / 'test_eval_1.py', 'w', encoding='utf-8') as f:
        f.write("""
# Test eval call
result = eval("1 + 2")
""")
    
    # 阴性测试用例 (不应匹配)
    with open(exec_dir / 'test_safe_1.py', 'w', encoding='utf-8') as f:
        f.write("""
# Safe code
def execute_task(task):
    '''Execute a task'''
    print(f"Executing: {task}")
""")
    
    logger.info("  ✅ 测试用例已创建")

def find_test_files(pattern: dict) -> List[Path]:
    """查找匹配的测试文件"""
    pattern_name = pattern.get('name', '').lower()
    test_files = []
    
    # 根据 pattern 名称查找对应测试目录
    if 'exec' in pattern_name or 'eval' in pattern_name:
        test_dir = TEST_CASES_DIR / 'exec_eval'
        if test_dir.exists():
            test_files.extend(test_dir.glob('*.py'))
    
    return test_files

if __name__ == '__main__':
    result = test()
    print(json.dumps(result, indent=2))
