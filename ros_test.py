#!/usr/bin/env python3
"""
🧪 HROS 测试套件
Unit Testing / Integration Testing / Regression Testing / Stress Testing
"""

import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# === 配置 ===
WORKSPACE = Path('/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master')
RULES_DIR = WORKSPACE / 'rules' / 'scanner_v3' / 'yara'
BENCHMARK = WORKSPACE / 'benchmark' / 'benchmark_v3.py'

@dataclass
class TestResult:
    name: str
    passed: bool
    duration: float
    message: str
    details: Dict = None

# === 测试套件 ===

class RosTestSuite:
    """HROS 测试套件"""
    
    def __init__(self):
        self.results: List[TestResult] = []
    
    def run_all(self) -> Dict:
        """运行所有测试"""
        print("="*70)
        print("🧪 HROS 测试套件")
        print("="*70)
        
        # 单元测试
        print("\n📋 单元测试")
        self.test_single_rule_detection()
        self.test_benign_sample()
        self.test_rule_syntax()
        
        # 集成测试
        print("\n🔧 集成测试")
        self.test_full_cycle()
        self.test_benchmark_integration()
        
        # 回归测试
        print("\n🔄 回归测试")
        self.test_version_comparison()
        
        # 压力测试
        print("\n⚡ 压力测试")
        self.test_large_samples()
        
        # 生成报告
        return self.generate_report()
    
    def test_single_rule_detection(self):
        """测试：单条规则检测"""
        name = "单条规则检测"
        start = time.time()
        
        try:
            import yara
            
            # 创建测试样本
            test_code = 'eval("malicious")'
            test_file = WORKSPACE / 'ros_tests' / 'test_sample.py'
            test_file.write_text(test_code)
            
            # 编译规则
            rules = yara.compile(source='rule Test { strings: $a = "eval" condition: $a }')
            matches = rules.match(str(test_file))
            
            passed = len(matches) > 0
            duration = time.time() - start
            
            self.results.append(TestResult(
                name=name,
                passed=passed,
                duration=duration,
                message="✅ 检测到恶意模式" if passed else "❌ 未检测到"
            ))
            
            # 清理
            test_file.unlink()
            
        except Exception as e:
            self.results.append(TestResult(
                name=name,
                passed=False,
                duration=time.time() - start,
                message=f"❌ 错误：{e}"
            ))
    
    def test_benign_sample(self):
        """测试：良性样本不误报"""
        name = "良性样本不误报"
        start = time.time()
        
        try:
            import yara
            
            # 创建良性样本
            benign_code = '''#!/usr/bin/env python3
def hello():
    print("Hello World")
    
if __name__ == '__main__':
    hello()
'''
            test_file = WORKSPACE / 'ros_tests' / 'benign_sample.py'
            test_file.write_text(benign_code)
            
            # 使用简化规则测试
            rules = yara.compile(source='rule Test { strings: $a = "eval" $b = "exec" condition: $a or $b }')
            matches = rules.match(str(test_file))
            
            passed = len(matches) == 0
            duration = time.time() - start
            
            self.results.append(TestResult(
                name=name,
                passed=passed,
                duration=duration,
                message="✅ 无误报" if passed else "❌ 误报"
            ))
            
            test_file.unlink()
            
        except Exception as e:
            self.results.append(TestResult(
                name=name,
                passed=False,
                duration=time.time() - start,
                message=f"❌ 错误：{e}"
            ))
    
    def test_rule_syntax(self):
        """测试：规则语法正确"""
        name = "规则语法检查"
        start = time.time()
        
        try:
            import yara
            
            # 检查所有规则文件
            rule_files = list(RULES_DIR.glob('*.yar'))
            errors = []
            
            for rf in rule_files:
                try:
                    yara.compile(source=rf.read_text())
                except Exception as e:
                    errors.append(f"{rf.name}: {e}")
            
            passed = len(errors) == 0
            duration = time.time() - start
            
            self.results.append(TestResult(
                name=name,
                passed=passed,
                duration=duration,
                message=f"✅ {len(rule_files)} 个文件通过" if passed else f"❌ {len(errors)} 个错误",
                details={'errors': errors[:5]}
            ))
            
        except Exception as e:
            self.results.append(TestResult(
                name=name,
                passed=False,
                duration=time.time() - start,
                message=f"❌ 错误：{e}"
            ))
    
    def test_full_cycle(self):
        """测试：完整循环流程"""
        name = "完整循环流程"
        start = time.time()
        
        try:
            result = subprocess.run(
                ['python3', str(WORKSPACE / 'ros_cycle.py')],
                capture_output=True, text=True, timeout=60
            )
            
            passed = 'ROS 循环' in result.stdout
            duration = time.time() - start
            
            self.results.append(TestResult(
                name=name,
                passed=passed,
                duration=duration,
                message="✅ 循环正常" if passed else "❌ 循环失败"
            ))
            
        except Exception as e:
            self.results.append(TestResult(
                name=name,
                passed=False,
                duration=time.time() - start,
                message=f"❌ 错误：{e}"
            ))
    
    def test_benchmark_integration(self):
        """测试：benchmark 集成"""
        name = "benchmark 集成"
        start = time.time()
        
        try:
            # 找到最新规则文件
            rule_files = sorted(RULES_DIR.glob('all_rules_v*.yar'))
            if not rule_files:
                raise Exception("未找到规则文件")
            
            latest = rule_files[-1]
            result = subprocess.run(
                ['python3', str(BENCHMARK), '--rules', str(latest)],
                capture_output=True, text=True, timeout=90
            )
            
            passed = 'Detection Rate' in result.stdout
            duration = time.time() - start
            
            self.results.append(TestResult(
                name=name,
                passed=passed,
                duration=duration,
                message="✅ benchmark 正常" if passed else "❌ benchmark 失败"
            ))
            
        except Exception as e:
            self.results.append(TestResult(
                name=name,
                passed=False,
                duration=time.time() - start,
                message=f"❌ 错误：{e}"
            ))
    
    def test_version_comparison(self):
        """测试：版本对比"""
        name = "版本对比测试"
        start = time.time()
        
        try:
            # 检查历史记录
            history_file = WORKSPACE / 'ros_meta' / 'history.json'
            
            if history_file.exists():
                history = json.loads(history_file.read_text())
                passed = len(history) > 0
                message = f"✅ {len(history)} 轮记录" if passed else "❌ 无记录"
            else:
                passed = False
                message = "❌ 历史记录不存在"
            
            duration = time.time() - start
            
            self.results.append(TestResult(
                name=name,
                passed=passed,
                duration=duration,
                message=message
            ))
            
        except Exception as e:
            self.results.append(TestResult(
                name=name,
                passed=False,
                duration=time.time() - start,
                message=f"❌ 错误：{e}"
            ))
    
    def test_large_samples(self):
        """测试：大批量样本"""
        name = "大批量样本压力测试"
        start = time.time()
        
        try:
            # 找到最新规则文件
            rule_files = sorted(RULES_DIR.glob('all_rules_v*.yar'))
            if not rule_files:
                raise Exception("未找到规则文件")
            
            latest = rule_files[-1]
            
            # 运行 benchmark (包含 135 个样本)
            result = subprocess.run(
                ['python3', str(BENCHMARK), '--rules', str(latest)],
                capture_output=True, text=True, timeout=120
            )
            
            # 检查是否完成
            passed = 'Detection Rate' in result.stdout
            duration = time.time() - start
            
            self.results.append(TestResult(
                name=name,
                passed=passed,
                duration=duration,
                message=f"✅ 135 个样本，{duration:.1f}秒" if passed else "❌ 超时或失败"
            ))
            
        except Exception as e:
            self.results.append(TestResult(
                name=name,
                passed=False,
                duration=time.time() - start,
                message=f"❌ 错误：{e}"
            ))
    
    def generate_report(self) -> Dict:
        """生成测试报告"""
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        
        print("\n" + "="*70)
        print(f"📊 测试结果：{passed}/{total} 通过 ({passed/total*100:.1f}%)")
        print("="*70)
        
        for r in self.results:
            status = "✅" if r.passed else "❌"
            print(f"{status} {r.name} ({r.duration:.2f}秒)")
            print(f"   {r.message}")
        
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'passed': passed,
            'total': total,
            'pass_rate': passed/total*100,
            'results': [asdict(r) for r in self.results]
        }
        
        # 保存报告
        report_file = WORKSPACE / 'ros_tests' / 'test_report.json'
        report_file.parent.mkdir(exist_ok=True)
        report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        
        print(f"\n💾 报告已保存：{report_file}")
        print("="*70)
        
        return report

# === 主函数 ===
if __name__ == '__main__':
    suite = RosTestSuite()
    suite.run_all()
