# Generated: 2026-04-02 12:15:22.313974
# Type: Benign Python Sample

#!/usr/bin/env python3
"""测试运行器 - 良性"""
import unittest
import sys
from pathlib import Path

def run_tests(test_dir: str = 'tests'):
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\n测试结果：{result.testsRun} 个测试")
    print(f"成功：{result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败：{len(result.failures)}")
    print(f"错误：{len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
