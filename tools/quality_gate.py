#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 质量评估引擎 (Quality Gate)

功能:
1. 评估检测率 (目标：≥99%)
2. 评估误报率 (目标：<1%)
3. 评估性能指标 (目标：<50ms)
4. 生成质量报告
"""

import os
import sys
import json
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# 路径配置
PROJECT_ROOT = Path(__file__).parent.parent
RULES_DIR = PROJECT_ROOT / "rules"
SAMPLES_DIR = PROJECT_ROOT / "samples"
REPORTS_DIR = PROJECT_ROOT / "reports"

# 确保报告目录存在
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class DetectionEngine:
    """简化版检测引擎 - 用于测试"""
    
    def __init__(self, rules_dir: Path = None):
        self.rules_dir = rules_dir or RULES_DIR
        self.rules = []
        self.load_rules()
    
    def load_rules(self):
        """加载所有规则"""
        # 加载 Sigma 规则
        sigma_dir = self.rules_dir / "sigma"
        if sigma_dir.exists():
            for yaml_file in sigma_dir.rglob("*.yaml"):
                try:
                    import yaml
                    with open(yaml_file, "r", encoding="utf-8") as f:
                        rule = yaml.safe_load(f)
                        if rule:
                            rule["_type"] = "sigma"
                            rule["_source"] = str(yaml_file)
                            self.rules.append(rule)
                except Exception as e:
                    print(f"⚠️  加载规则失败 {yaml_file}: {e}")
        
        # 加载 YARA 规则
        yara_dir = self.rules_dir / "yara"
        if yara_dir.exists():
            for yar_file in yara_dir.rglob("*.yar"):
                try:
                    with open(yar_file, "r", encoding="utf-8") as f:
                        content = f.read()
                        rule = {
                            "_type": "yara",
                            "_source": str(yar_file),
                            "_raw": content
                        }
                        self.rules.append(rule)
                except Exception as e:
                    print(f"⚠️  加载规则失败 {yar_file}: {e}")
        
        print(f"📚 加载 {len(self.rules)} 条规则")
    
    def detect(self, code: str) -> List[Dict]:
        """检测代码"""
        threats = []
        
        for rule in self.rules:
            rule_type = rule.get("_type", "")
            detected = False
            
            if rule_type == "sigma":
                # Sigma 规则检测 (简化版)
                detection = rule.get("detection", {})
                selection = detection.get("selection", {})
                keyword = selection.get("keyword", "")
                
                if keyword and re.search(keyword, code, re.IGNORECASE):
                    detected = True
            
            elif rule_type == "yara":
                # YARA 规则检测 (简化版)
                raw = rule.get("_raw", "")
                # 提取字符串
                import re
                strings = re.findall(r'\$[a-z] = "([^"]+)"', raw, re.IGNORECASE)
                for string in strings:
                    if string.lower() in code.lower():
                        detected = True
                        break
            
            if detected:
                threats.append({
                    "rule_id": rule.get("id", "unknown"),
                    "rule_title": rule.get("title", "unknown"),
                    "rule_type": rule_type,
                    "severity": rule.get("level", rule.get("severity", "unknown"))
                })
        
        return threats


class QualityGate:
    """质量评估引擎"""
    
    def __init__(self):
        self.engine = DetectionEngine()
        self.results = {
            "detection_rate": 0.0,
            "false_positive_rate": 0.0,
            "performance": {},
            "coverage": {}
        }
    
    def evaluate_detection_rate(self) -> float:
        """评估检测率"""
        print("\n📊 评估检测率...")
        
        malicious_dir = SAMPLES_DIR / "malicious"
        if not malicious_dir.exists():
            print("  ⚠️  恶意样本目录不存在")
            return 0.0
        
        total_samples = 0
        detected_samples = 0
        
        for attack_dir in malicious_dir.iterdir():
            if attack_dir.is_dir():
                attack_type = attack_dir.name
                print(f"  检测 {attack_type}...")
                
                for sample_file in attack_dir.glob("*.txt"):
                    with open(sample_file, "r", encoding="utf-8") as f:
                        sample = f.read()
                    
                    total_samples += 1
                    threats = self.engine.detect(sample)
                    
                    if threats:
                        detected_samples += 1
        
        detection_rate = (detected_samples / total_samples * 100) if total_samples > 0 else 0.0
        
        print(f"  总样本：{total_samples}")
        print(f"  检出：{detected_samples}")
        print(f"  检测率：{detection_rate:.2f}%")
        
        self.results["detection_rate"] = detection_rate
        return detection_rate
    
    def evaluate_false_positive_rate(self) -> float:
        """评估误报率"""
        print("\n📊 评估误报率...")
        
        benign_dir = SAMPLES_DIR / "benign"
        if not benign_dir.exists():
            print("  ⚠️  良性样本目录不存在")
            return 0.0
        
        total_samples = 0
        false_positives = 0
        
        for sample_file in benign_dir.glob("*.txt"):
            with open(sample_file, "r", encoding="utf-8") as f:
                sample = f.read()
            
            total_samples += 1
            threats = self.engine.detect(sample)
            
            if threats:
                false_positives += 1
        
        fp_rate = (false_positives / total_samples * 100) if total_samples > 0 else 0.0
        
        print(f"  总样本：{total_samples}")
        print(f"  误报：{false_positives}")
        print(f"  误报率：{fp_rate:.2f}%")
        
        self.results["false_positive_rate"] = fp_rate
        return fp_rate
    
    def evaluate_performance(self) -> Dict:
        """评估性能指标"""
        print("\n📊 评估性能...")
        
        # 准备测试样本
        test_samples = []
        for sample_dir in [SAMPLES_DIR / "malicious", SAMPLES_DIR / "benign"]:
            if sample_dir.exists():
                for sample_file in list(sample_dir.glob("*.txt"))[:20]:  # 取前 20 个
                    with open(sample_file, "r", encoding="utf-8") as f:
                        test_samples.append(f.read())
        
        if not test_samples:
            print("  ⚠️  无测试样本")
            return {}
        
        # 性能测试
        times = []
        for sample in test_samples:
            start = time.time()
            self.engine.detect(sample)
            end = time.time()
            times.append((end - start) * 1000)  # 转换为毫秒
        
        avg_time = sum(times) / len(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        p99_time = sorted(times)[int(len(times) * 0.99)]
        max_time = max(times)
        
        print(f"  平均耗时：{avg_time:.2f}ms")
        print(f"  P95 耗时：{p95_time:.2f}ms")
        print(f"  P99 耗时：{p99_time:.2f}ms")
        print(f"  最大耗时：{max_time:.2f}ms")
        
        self.results["performance"] = {
            "avg_ms": avg_time,
            "p95_ms": p95_time,
            "p99_ms": p99_time,
            "max_ms": max_time
        }
        
        return self.results["performance"]
    
    def evaluate_coverage(self) -> Dict:
        """评估攻击类型覆盖率"""
        print("\n📊 评估覆盖率...")
        
        # 统计规则覆盖的攻击类型
        attack_types = set()
        for rule in self.engine.rules:
            # 从规则 ID 或标签推断攻击类型
            rule_id = rule.get("id", "").lower()
            if "prompt" in rule_id:
                attack_types.add("prompt_injection")
            elif "tool" in rule_id or "poison" in rule_id:
                attack_types.add("tool_poisoning")
            elif "exfil" in rule_id or "data" in rule_id:
                attack_types.add("data_exfiltration")
            elif "memory" in rule_id or "pollut" in rule_id:
                attack_types.add("memory_pollution")
            elif "remote" in rule_id or "load" in rule_id:
                attack_types.add("remote_load")
            elif "resource" in rule_id or "exhaust" in rule_id:
                attack_types.add("resource_exhaustion")
        
        # 统计样本覆盖的攻击类型
        sample_types = set()
        if (SAMPLES_DIR / "malicious").exists():
            for attack_dir in (SAMPLES_DIR / "malicious").iterdir():
                if attack_dir.is_dir():
                    sample_types.add(attack_dir.name)
        
        print(f"  规则覆盖：{len(attack_types)} 类")
        print(f"  样本覆盖：{len(sample_types)} 类")
        
        self.results["coverage"] = {
            "rule_attack_types": len(attack_types),
            "sample_attack_types": len(sample_types),
            "attack_types": list(attack_types)
        }
        
        return self.results["coverage"]
    
    def run_full_evaluation(self) -> Dict:
        """运行完整评估"""
        print("=" * 60)
        print("🎯 质量评估引擎")
        print("=" * 60)
        
        self.evaluate_detection_rate()
        self.evaluate_false_positive_rate()
        self.evaluate_performance()
        self.evaluate_coverage()
        
        return self.results
    
    def generate_report(self, output_file: Path = None) -> Path:
        """生成质量报告"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = REPORTS_DIR / f"quality_report_{timestamp}.md"
        
        detection_rate = self.results.get("detection_rate", 0.0)
        fp_rate = self.results.get("false_positive_rate", 0.0)
        performance = self.results.get("performance", {})
        coverage = self.results.get("coverage", {})
        
        # 评估是否达标
        detection_pass = detection_rate >= 99.0
        fp_pass = fp_rate < 1.0
        perf_pass = performance.get("avg_ms", 999) < 50
        
        report = f"""# 🎯 质量评估报告

**生成时间:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 核心指标

| 指标 | 当前值 | 目标 | 状态 |
|------|--------|------|------|
| 检测率 | {detection_rate:.2f}% | ≥99% | {"✅" if detection_pass else "❌"} |
| 误报率 | {fp_rate:.2f}% | <1% | {"✅" if fp_pass else "❌"} |
| 平均耗时 | {performance.get("avg_ms", 0):.2f}ms | <50ms | {"✅" if perf_pass else "❌"} |
| P99 耗时 | {performance.get("p99_ms", 0):.2f}ms | <100ms | {"✅" if performance.get("p99_ms", 999) < 100 else "❌"} |

## 详细结果

### 检测率
- 检出率：{detection_rate:.2f}%
- 目标：≥99%
- 差距：{99.0 - detection_rate:.2f}%

### 误报率
- 误报率：{fp_rate:.2f}%
- 目标：<1%
- 差距：{fp_rate - 1.0:.2f}%

### 性能指标
- 平均耗时：{performance.get("avg_ms", 0):.2f}ms
- P95 耗时：{performance.get("p95_ms", 0):.2f}ms
- P99 耗时：{performance.get("p99_ms", 0):.2f}ms
- 最大耗时：{performance.get("max_ms", 0):.2f}ms

### 覆盖率
- 规则覆盖攻击类型：{coverage.get("rule_attack_types", 0)} 类
- 样本覆盖攻击类型：{coverage.get("sample_attack_types", 0)} 类
- 覆盖的攻击类型：{", ".join(coverage.get("attack_types", []))}

## 总体评估

{"✅ 所有指标达标!" if (detection_pass and fp_pass and perf_pass) else "⚠️ 部分指标未达标，需要优化"}

## 改进建议

"""
        
        if not detection_pass:
            report += f"""### 提升检测率
- 当前检测率：{detection_rate:.2f}%
- 目标：≥99%
- 建议:
  - 增加规则数量 (特别是未覆盖的攻击类型)
  - 优化现有规则的模式匹配
  - 添加更多样本变体进行测试

"""
        
        if not fp_pass:
            report += f"""### 降低误报率
- 当前误报率：{fp_rate:.2f}%
- 目标：<1%
- 建议:
  - 优化规则的精确度
  - 添加白名单机制
  - 增加上下文判断逻辑

"""
        
        if not perf_pass:
            report += f"""### 优化性能
- 当前平均耗时：{performance.get("avg_ms", 0):.2f}ms
- 目标：<50ms
- 建议:
  - 实现规则缓存
  - 优化正则表达式
  - 使用并发检测

"""
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"\n📄 报告已生成：{output_file}")
        return output_file


def main():
    """主函数"""
    gate = QualityGate()
    results = gate.run_full_evaluation()
    gate.generate_report()
    
    print("\n" + "=" * 60)
    print("📊 评估完成!")
    print("=" * 60)
    
    # 返回是否达标
    detection_pass = results.get("detection_rate", 0) >= 99.0
    fp_pass = results.get("false_positive_rate", 100) < 1.0
    
    if detection_pass and fp_pass:
        print("✅ 所有核心指标达标!")
        return 0
    else:
        print("⚠️ 部分指标未达标")
        return 1


if __name__ == "__main__":
    sys.exit(main())
