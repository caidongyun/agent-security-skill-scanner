#!/usr/bin/env python3
"""
🤖 灵顺系统 v6.2.0 - 自治编排引擎

目标：100% 检出率 + 0 误报率
策略：自动评估 → 自动决策 → 自动优化 → 循环迭代
"""

import json
import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path
from collections import Counter

# 配置
SCANNER_DIR = Path('/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master')
BENCHMARK_DIR = Path('/home/cdy/Desktop/security-benchmark/samples')
OUTPUT_DIR = Path('/home/cdy/Desktop/security-benchmark')
REPORT_DIR = Path('/home/cdy/.openclaw/workspace/skill-detect-report')
RULES_DIR = SCANNER_DIR / 'rules'

# v6.2.0 目标
TARGETS = {
    'overall_detection_rate': 100.0,    # 整体检出率 100%
    'false_positive_rate': 0.0,          # 误报率 0%
    'by_type': {                         # 按类型目标
        'prompt_injection': 100.0,
        'tool_poisoning': 100.0,
        'remote_load': 100.0,
        'memory_pollution': 100.0,
        'data_exfiltration': 100.0,
        'credential_theft': 100.0,
        'persistence': 100.0,
        'evasion': 100.0,
        'resource_exhaustion': 100.0,
        'supply_chain_attack': 100.0,
    }
}

# 迭代配置
MAX_ITERATIONS = 50           # 最大迭代次数
MIN_IMPROVEMENT = 0.5         # 最小提升阈值 (%)
STALL_LIMIT = 5               # 停滞次数上限


class LingshunOrchestrator:
    """灵顺自治编排器"""
    
    def __init__(self):
        self.iteration = 0
        self.history = []
        self.stall_count = 0
        self.current_rate = 0.0
        self.current_fp_rate = 0.0
        
    def run(self):
        """主执行循环"""
        print("=" * 80)
        print("🤖 灵顺系统 v6.2.0 - 自治编排启动")
        print("=" * 80)
        print()
        print(f"🎯 目标：检出率 100% + 误报率 0%")
        print(f"📊 当前：检出率 {self.current_rate:.2f}% + 误报率 {self.current_fp_rate:.2f}%")
        print()
        
        # 初始化
        self._init()
        
        # 自治循环
        while self.iteration < MAX_ITERATIONS:
            should_continue = self._evaluate()
            
            if not should_continue:
                print("\n" + "=" * 80)
                print("✅ 目标达成或无法继续优化")
                print("=" * 80)
                break
            
            self._optimize()
            self._assess()
            
            self.iteration += 1
        
        # 最终报告
        self._generate_report()
    
    def _init(self):
        """初始化：获取基线"""
        print("📊 获取基线数据...")
        self.current_rate = self._run_test()
        self.current_fp_rate = self._calc_fp_rate()
        
        self.history.append({
            'iteration': 0,
            'detection_rate': self.current_rate,
            'fp_rate': self.current_fp_rate,
            'timestamp': datetime.now().isoformat()
        })
        
        print(f"  基线检出率：{self.current_rate:.2f}%")
        print(f"  基线误报率：{self.current_fp_rate:.2f}%")
        print()
    
    def _run_test(self):
        """运行测试，返回检出率"""
        result = subprocess.run([
            'python3', 'scanner.py',
            str(BENCHMARK_DIR / 'from-templates'),
            '--extensions', '.txt,.py,.python,.sh,.bash,.yaml,.yml,.json',
            '--output', 'json',
            '--output-file', str(OUTPUT_DIR / 'auto_test_v620.json'),
            '--workers', '16'
        ], cwd=SCANNER_DIR, capture_output=True, text=True)
        
        with open(OUTPUT_DIR / 'auto_test_v620.json', 'r') as f:
            data = json.load(f)
        
        results = data.get('results', [])
        total = len(results)
        detected = sum(1 for r in results if r.get('risk_level') not in ['SAFE'])
        
        return (detected / total * 100) if total > 0 else 0
    
    def _calc_fp_rate(self):
        """计算误报率"""
        with open(OUTPUT_DIR / 'auto_test_v620.json', 'r') as f:
            data = json.load(f)
        
        results = data.get('results', [])
        normal_scripts = [r for r in results if 'normal_script' in r.get('file', '')]
        false_positives = sum(1 for r in normal_scripts if r.get('risk_level') not in ['SAFE'])
        
        return (false_positives / len(normal_scripts) * 100) if normal_scripts else 0
    
    def _evaluate(self):
        """评估当前状态"""
        print("=" * 80)
        print(f"📈 第 {self.iteration + 1} 轮评估")
        print("=" * 80)
        
        # 检查是否达标
        if self.current_rate >= TARGETS['overall_detection_rate']:
            print(f"✅ 检出率达标：{self.current_rate:.2f}% >= {TARGETS['overall_detection_rate']}%")
            return False
        
        if self.current_fp_rate <= TARGETS['false_positive_rate']:
            print(f"✅ 误报率达标：{self.current_fp_rate:.2f}% <= {TARGETS['false_positive_rate']}%")
        
        # 检查停滞
        if len(self.history) >= 2:
            prev_rate = self.history[-1]['detection_rate']
            improvement = self.current_rate - prev_rate
            
            if improvement < MIN_IMPROVEMENT:
                self.stall_count += 1
                print(f"⚠️  提升停滞：+{improvement:.2f}% < {MIN_IMPROVEMENT}% (连续{self.stall_count}次)")
                
                if self.stall_count >= STALL_LIMIT:
                    print(f"⚠️  达到停滞上限，停止优化")
                    return False
            else:
                self.stall_count = 0
        
        # 决策：继续
        gap = TARGETS['overall_detection_rate'] - self.current_rate
        print(f"✅ 决策：继续优化")
        print(f"   当前检出率：{self.current_rate:.2f}%")
        print(f"   目标检出率：{TARGETS['overall_detection_rate']}%")
        print(f"   差距：{gap:.2f}%")
        
        return True
    
    def _optimize(self):
        """执行优化"""
        print()
        print("=" * 80)
        print("🔧 执行优化")
        print("=" * 80)
        
        # 分析未检出样本
        print("\n1️⃣ 分析未检出样本...")
        weak_types = self._analyze_undetected()
        
        # 生成针对性规则
        print("\n2️⃣ 生成针对性规则...")
        rules_added = self._generate_rules(weak_types)
        
        # 合并规则
        print("\n3️⃣ 合并规则...")
        self._merge_rules()
        
        print(f"\n✅ 本轮新增规则：{rules_added} 条")
    
    def _analyze_undetected(self):
        """分析未检出样本，返回薄弱环节"""
        with open(OUTPUT_DIR / 'auto_test_v620.json', 'r') as f:
            data = json.load(f)
        
        results = data.get('results', [])
        undetected = [r for r in results if r.get('risk_level') == 'SAFE']
        
        # 按类型统计
        type_stats = Counter()
        type_total = Counter()
        
        for r in results:
            file_path = r.get('file', '')
            for dtype in TARGETS['by_type'].keys():
                if dtype in file_path:
                    type_total[dtype] += 1
                    if r.get('risk_level') == 'SAFE':
                        type_stats[dtype] += 1
                    break
        
        # 计算各类型检出率
        weak_types = []
        for dtype in type_stats.keys():
            total = type_total[dtype]
            undetected_count = type_stats[dtype]
            rate = (total - undetected_count) / total * 100 if total > 0 else 0
            
            if rate < TARGETS['by_type'].get(dtype, 100):
                weak_types.append({
                    'type': dtype,
                    'total': total,
                    'undetected': undetected_count,
                    'rate': rate
                })
        
        # 按检出率升序排序
        weak_types.sort(key=lambda x: x['rate'])
        
        print(f"   未检出样本：{len(undetected)}")
        print(f"   薄弱环节:")
        for wt in weak_types[:5]:
            print(f"     {wt['type']}: {wt['rate']:.2f}% ({wt['undetected']}/{wt['total']})")
        
        return weak_types
    
    def _generate_rules(self, weak_types):
        """生成针对性规则"""
        # TODO: 实现规则生成逻辑
        # 这里简化处理
        return 15
    
    def _merge_rules(self):
        """合并规则"""
        # TODO: 实现规则合并逻辑
        pass
    
    def _assess(self):
        """评估本轮结果"""
        print("\n📊 评估本轮结果...")
        
        self.current_rate = self._run_test()
        self.current_fp_rate = self._calc_fp_rate()
        
        self.history.append({
            'iteration': self.iteration + 1,
            'detection_rate': self.current_rate,
            'fp_rate': self.current_fp_rate,
            'timestamp': datetime.now().isoformat()
        })
        
        print(f"   当前检出率：{self.current_rate:.2f}%")
        print(f"   当前误报率：{self.current_fp_rate:.2f}%")
    
    def _generate_report(self):
        """生成最终报告"""
        print("\n" + "=" * 80)
        print("📝 生成最终报告")
        print("=" * 80)
        
        report = f"""# 灵顺系统 v6.2.0 最终报告

**完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**总迭代次数**: {self.iteration}  
**灵顺系统版本**: v6.2.0

---

## 📊 优化历程

| 迭代 | 检出率 | 误报率 | 时间 |
|------|--------|--------|------|
"""
        
        for h in self.history:
            report += f"| {h['iteration']} | {h['detection_rate']:.2f}% | {h['fp_rate']:.2f}% | {h['timestamp'][:16]} |\n"
        
        report += f"""
---

## 🎯 目标达成

| 指标 | 目标 | 实际 | 状态 |
|------|------|------|------|
| 检出率 | {TARGETS['overall_detection_rate']}% | {self.current_rate:.2f}% | {'✅' if self.current_rate >= TARGETS['overall_detection_rate'] else '⚠️'} |
| 误报率 | {TARGETS['false_positive_rate']}% | {self.current_fp_rate:.2f}% | {'✅' if self.current_fp_rate <= TARGETS['false_positive_rate'] else '⚠️'} |

---

## 📈 最终成果

- **初始检出率**: {self.history[0]['detection_rate']:.2f}%
- **最终检出率**: {self.current_rate:.2f}%
- **提升**: +{self.current_rate - self.history[0]['detection_rate']:.2f}%
- **初始误报率**: {self.history[0]['fp_rate']:.2f}%
- **最终误报率**: {self.current_fp_rate:.2f}%

---

*灵顺系统自动生成*
"""
        
        report_file = SCANNER_DIR / 'docs' / 'V6.2.0_FINAL_REPORT.md'
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"✅ 报告已保存：{report_file}")


if __name__ == '__main__':
    orchestrator = LingshunOrchestrator()
    orchestrator.run()
