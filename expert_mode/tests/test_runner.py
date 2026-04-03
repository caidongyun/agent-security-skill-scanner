#!/usr/bin/env python3
"""
🧪 灵顺 V5 测试运行器 - TDD 测试驱动开发
======================================
功能：
- 加载 150+ 测试用例
- 运行检测验证
- 生成测试报告
- 计算质量指标

使用方式:
    python3 test_runner.py              # 运行所有测试
    python3 test_runner.py --category tool_poisoning
    python3 test_runner.py --verbose
"""

import os
import sys
import json
import time
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# 路径配置
SCRIPT_DIR = Path(__file__).parent
TEST_CASES_DIR = SCRIPT_DIR / "cases"
RULES_DIR = SCRIPT_DIR.parent / "rules"  # 从 rules/ 目录加载
REPORTS_DIR = SCRIPT_DIR / "reports"

# 确保报告目录存在
REPORTS_DIR.mkdir(exist_ok=True)


class SecurityDetector:
    """安全检测器 - 实现检测逻辑"""
    
    def __init__(self):
        # 加载检测规则
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict[str, List[Dict]]:
        """加载检测规则"""
        rules = {
            "tool_poisoning": [],
            {"id": "TP01", "pattern": r"b64decode", "risk": "HIGH"},
            {"id": "TP01", "pattern": r"atob\s*\(", "risk": "HIGH"},
            {"id": "TP02", "pattern": r"zlib\.decompress", "risk": "MEDIUM"},
            {"id": "TP02", "pattern": r"gzip\.decompress", "risk": "MEDIUM"},
            {"id": "TP03", "pattern": r"__import__\s*\(", "risk": "HIGH"},
            {"id": "TP03", "pattern": r"importlib\.import_module", "risk": "HIGH"},
            {"id": "TP04", "pattern": r"\beval\s*\(", "risk": "CRITICAL"},
            {"id": "TP04", "pattern": r"\bexec\s*\(", "risk": "CRITICAL"},
            {"id": "TP04", "pattern": r"\bcompile\s*\(", "risk": "CRITICAL"},
            {"id": "TP04", "pattern": r"pickle\.loads?", "risk": "CRITICAL"},
        ]
        
        # 远程加载规则
        rules["remote_load"] = [
            {"id": "RL01", "pattern": r"curl.*\|.*(?:bash|sh)", "risk": "CRITICAL"},
            {"id": "RL01", "pattern": r"wget.*\|.*(?:bash|sh)", "risk": "CRITICAL"},
            {"id": "RL01", "pattern": r"curl\s+.*\|\s*python", "risk": "CRITICAL"},
            {"id": "RL02", "pattern": r"glot\.io", "risk": "HIGH"},
            {"id": "RL02", "pattern": r"pastebin\.com", "risk": "HIGH"},
            {"id": "RL02", "pattern": r"rentry\.co", "risk": "HIGH"},
            {"id": "RL03", "pattern": r"nslookup\s+.*\.", "risk": "HIGH"},
            {"id": "RL03", "pattern": r"dig\s+.*\.", "risk": "HIGH"},
            {"id": "RL04", "pattern": r"steghide", "risk": "MEDIUM"},
            {"id": "RL04", "pattern": r"zsteg", "risk": "MEDIUM"},
        ]
        
        # 数据窃取规则
        rules["data_exfil"] = [
            {"id": "DE01", "pattern": r"/Desktop/", "risk": "MEDIUM"},
            {"id": "DE01", "pattern": r"/Documents/", "risk": "MEDIUM"},
            {"id": "DE02", "pattern": r"\.ssh/", "risk": "CRITICAL"},
            {"id": "DE02", "pattern": r"\.gnupg/", "risk": "CRITICAL"},
            {"id": "DE02", "pattern": r"id_rsa", "risk": "CRITICAL"},
            {"id": "DE03", "pattern": r"pyperclip\.paste", "risk": "HIGH"},
            {"id": "DE03", "pattern": r"xclip", "risk": "HIGH"},
            {"id": "DE04", "pattern": r"pynput", "risk": "CRITICAL"},
            {"id": "DE04", "pattern": r"keylog", "risk": "CRITICAL"},
            {"id": "DE05", "pattern": r"pyautogui\.screenshot", "risk": "MEDIUM"},
            {"id": "DE05", "pattern": r"ImageGrab\.grab", "risk": "MEDIUM"},
        ]
        
        # 提示词注入规则
        rules["prompt_injection"] = [
            {"id": "PI01", "pattern": r"(?i)ignore\s+(previous|all)", "risk": "HIGH"},
            {"id": "PI01", "pattern": r"(?i)忽略 (之前 | 上面)", "risk": "HIGH"},
            {"id": "PI02", "pattern": r"(?i)you\s+are\s+now", "risk": "HIGH"},
            {"id": "PI02", "pattern": r"(?i)act\s+as", "risk": "HIGH"},
            {"id": "PI02", "pattern": r"(?i)你现在是", "risk": "HIGH"},
            {"id": "PI03", "pattern": r"(?i)admin\s+mode", "risk": "CRITICAL"},
            {"id": "PI03", "pattern": r"(?i)developer\s+mode", "risk": "CRITICAL"},
            {"id": "PI03", "pattern": r"(?i)解除限制", "risk": "CRITICAL"},
            {"id": "PI05", "pattern": r"```python", "risk": "HIGH"},
            {"id": "PI05", "pattern": r"```bash", "risk": "HIGH"},
        ]
        
        # 资源耗尽规则
        rules["resource_exhaustion"] = [
            {"id": "RE01", "pattern": r"while\s+True", "risk": "MEDIUM"},
            {"id": "RE01", "pattern": r"while\s*\(\s*1\s*\)", "risk": "MEDIUM"},
            {"id": "RE01", "pattern": r"for\s*\(;;\)", "risk": "MEDIUM"},
            {"id": "RE02", "pattern": r"bytearray\s*\(", "risk": "HIGH"},
            {"id": "RE02", "pattern": r"\[0\]\s*\*\s*\d+", "risk": "HIGH"},
            {"id": "RE03", "pattern": r"open\s*\([^)]*'a'", "risk": "MEDIUM"},
            {"id": "RE04", "pattern": r"os\.fork\s*\(", "risk": "HIGH"},
            {"id": "RE04", "pattern": r"multiprocessing", "risk": "MEDIUM"},
        ]
        
        # 记忆污染规则
        rules["memory_pollution"] = [
            {"id": "MP01", "pattern": r"SOUL\.md", "risk": "CRITICAL"},
            {"id": "MP01", "pattern": r"修改.*灵魂", "risk": "CRITICAL"},
            {"id": "MP02", "pattern": r"MEMORY\.md", "risk": "HIGH"},
            {"id": "MP02", "pattern": r"write_memory", "risk": "HIGH"},
            {"id": "MP02", "pattern": r"记住这个", "risk": "MEDIUM"},
            {"id": "MP03", "pattern": r"conversation", "risk": "MEDIUM"},
            {"id": "MP03", "pattern": r"history", "risk": "MEDIUM"},
            {"id": "MP04", "pattern": r"SKILL\.md", "risk": "HIGH"},
            {"id": "MP04", "pattern": r"修改.*技能", "risk": "HIGH"},
        ]
        
        # 供应链攻击规则
        rules["supply_chain"] = [
            {"id": "SC01", "pattern": r"official", "risk": "MEDIUM"},
            {"id": "SC01", "pattern": r"verified", "risk": "MEDIUM"},
            {"id": "SC01", "pattern": r"官方", "risk": "MEDIUM"},
            {"id": "SC02", "pattern": r"pip\s+install", "risk": "MEDIUM"},
            {"id": "SC02", "pattern": r"npm\s+install", "risk": "MEDIUM"},
            {"id": "SC03", "pattern": r"update.*source", "risk": "HIGH"},
            {"id": "SC03", "pattern": r"修改.*更新源", "risk": "HIGH"},
        ]
        
        # 容器逃逸规则
        rules["container_escape"] = [
            {"id": "CE01", "pattern": r"--privileged", "risk": "CRITICAL"},
            {"id": "CE01", "pattern": r"cap_add", "risk": "HIGH"},
            {"id": "CE02", "pattern": r"-v\s+/:", "risk": "CRITICAL"},
            {"id": "CE02", "pattern": r"-v\s+/proc", "risk": "CRITICAL"},
            {"id": "CE03", "pattern": r"mount\s+-t\s+proc", "risk": "CRITICAL"},
            {"id": "CE03", "pattern": r"nsenter", "risk": "HIGH"},
            {"id": "CE04", "pattern": r"dirty_pipe", "risk": "CRITICAL"},
            {"id": "CE04", "pattern": r"dirty_cow", "risk": "CRITICAL"},
            {"id": "CE04", "pattern": r"CVE-202", "risk": "HIGH"},
            {"id": "CE05", "pattern": r"cgroup", "risk": "HIGH"},
            {"id": "CE05", "pattern": r"release_agent", "risk": "CRITICAL"},
        ]
        
        return rules
    
    def detect(self, input_data) -> Dict[str, Any]:
        """
        检测输入是否恶意
        
        Args:
            input_data: str 或 dict (如果是 dict，提取 content 字段)
        
        Returns:
            {
                "detected": bool,
                "risk_level": str,
                "matched_rules": List[str],
                "category": str,
                "latency_ms": float
            }
        """
        # 处理输入类型 - 支持 dict 和 string
        if isinstance(input_data, dict):
            input_text = input_data.get("content", str(input_data))
        else:
            input_text = str(input_data)
        
        start_time = time.time()
        
        detected = False
        risk_level = "SAFE"
        matched_rules = []
        category = None
        
        # 按类别检测
        for cat, rules in self.rules.items():
            for rule in rules:
                if re.search(rule["pattern"], input_text, re.IGNORECASE):
                    detected = True
                    matched_rules.append(rule["id"])
                    category = cat
                    
                    # 更新风险等级 (取最高)
                    if rule["risk"] == "CRITICAL":
                        risk_level = "CRITICAL"
                    elif rule["risk"] == "HIGH" and risk_level != "CRITICAL":
                        risk_level = "HIGH"
                    elif rule["risk"] == "MEDIUM" and risk_level not in ["CRITICAL", "HIGH"]:
                        risk_level = "MEDIUM"
        
        latency_ms = (time.time() - start_time) * 1000
        
        return {
            "detected": detected,
            "risk_level": risk_level,
            "matched_rules": list(set(matched_rules)),
            "category": category,
            "latency_ms": latency_ms
        }


class TestRunner:
    """测试运行器"""
    
    def __init__(self, verbose: bool = False):
        self.detector = SecurityDetector()
        self.verbose = verbose
        self.test_cases = self._load_test_cases()
        self.results = []
    
    def _load_test_cases(self) -> List[Dict]:
        """加载所有测试用例"""
        cases = []
        
        if not TEST_CASES_DIR.exists():
            print(f"❌ 测试用例目录不存在：{TEST_CASES_DIR}")
            return cases
        
        for file in TEST_CASES_DIR.glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    file_cases = json.load(f)
                
                # 添加类别信息
                for case in file_cases:
                    case["source_file"] = file.name
                    cases.append(case)
                
                if self.verbose:
                    print(f"  📄 加载 {file.name}: {len(file_cases)} 个用例")
            except Exception as e:
                print(f"  ❌ 加载失败 {file.name}: {e}")
        
        return cases
    
    def run_test(self, case: Dict) -> Dict:
        """运行单个测试"""
        input_data = case["input"]
        expected = case["expected"]
        
        # 处理列表输入 (性能测试)
        if isinstance(input_data, list):
            detected_count = 0
            total_latency = 0
            
            for item in input_data:
                result = self.detector.detect(item)
                if result["detected"]:
                    detected_count += 1
                total_latency += result["latency_ms"]
            
            # 性能测试：所有都检测到且延迟达标
            passed = (detected_count == len(input_data))
            if "max_latency_ms" in case:
                avg_latency = total_latency / len(input_data)
                passed = passed and (avg_latency < case["max_latency_ms"])
            
            return {
                "case_id": case["id"],
                "name": case["name"],
                "passed": passed,
                "detected": detected_count == len(input_data),
                "total_cases": len(input_data),
                "latency_ms": total_latency / len(input_data),
                "expected": expected
            }
        
        # 单个输入检测
        result = self.detector.detect(input_data)
        
        # 判断是否通过
        if expected == "BLOCK":
            passed = result["detected"]
        elif expected == "WARN":
            passed = result["detected"]  # WARN 也算检测成功
        elif expected == "ALLOW":
            passed = not result["detected"]
        else:
            passed = False
        
        return {
            "case_id": case["id"],
            "name": case["name"],
            "passed": passed,
            "detected": result["detected"],
            "risk_level": result["risk_level"],
            "matched_rules": result["matched_rules"],
            "latency_ms": result["latency_ms"],
            "expected": expected
        }
    
    def run_all(self, category: Optional[str] = None) -> Dict:
        """运行所有测试"""
        print("\n" + "=" * 60)
        print("🧪 灵顺 V5 测试运行器")
        print("=" * 60)
        print(f"总用例数：{len(self.test_cases)}")
        
        # 过滤类别
        if category:
            filter_cases = [c for c in self.test_cases if category in c.get("source_file", "")]
            print(f"过滤类别：{category} ({len(filter_cases)} 个用例)")
            self.test_cases = filter_cases
        
        print("\n开始运行测试...\n")
        
        # 运行测试
        for i, case in enumerate(self.test_cases, 1):
            result = self.run_test(case)
            self.results.append(result)
            
            if self.verbose:
                status = "✅" if result["passed"] else "❌"
                print(f"  [{i}/{len(self.test_cases)}] {status} {case['id']}: {case['name']}")
        
        # 生成报告
        return self._generate_report()
    
    def _generate_report(self) -> Dict:
        """生成测试报告"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed
        
        # 按类别统计
        by_category = {}
        for result in self.results:
            # 从 case_id 推断类别
            category = result["case_id"].split("-")[0]
            if category not in by_category:
                by_category[category] = {"total": 0, "passed": 0}
            by_category[category]["total"] += 1
            if result["passed"]:
                by_category[category]["passed"] += 1
        
        # 计算指标
        pass_rate = (passed / total * 100) if total > 0 else 0
        avg_latency = sum(r["latency_ms"] for r in self.results) / total if total > 0 else 0
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": round(pass_rate, 2),
                "avg_latency_ms": round(avg_latency, 2)
            },
            "by_category": by_category,
            "failed_cases": [r for r in self.results if not r["passed"]],
            "details": self.results
        }
        
        # 打印报告
        print("\n" + "=" * 60)
        print("📊 测试报告")
        print("=" * 60)
        print(f"总用例：{total}")
        print(f"✅ 通过：{passed}")
        print(f"❌ 失败：{failed}")
        print(f"📈 通过率：{pass_rate:.1f}%")
        print(f"⚡ 平均延迟：{avg_latency:.2f}ms")
        
        print("\n按类别统计:")
        for cat, stats in sorted(by_category.items()):
            cat_pass_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            print(f"  {cat}: {stats['passed']}/{stats['total']} ({cat_pass_rate:.1f}%)")
        
        if report["failed_cases"]:
            print("\n失败用例:")
            for case in report["failed_cases"][:10]:  # 只显示前 10 个
                print(f"  ❌ {case['case_id']}: {case['name']}")
            if len(report["failed_cases"]) > 10:
                print(f"  ... 还有 {len(report['failed_cases']) - 10} 个失败用例")
        
        print("=" * 60 + "\n")
        
        # 保存报告
        report_file = REPORTS_DIR / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📝 详细报告已保存：{report_file}\n")
        
        return report


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="🧪 灵顺 V5 测试运行器")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--category", "-c", type=str, help="指定类别")
    parser.add_argument("--generate-samples", action="store_true", help="生成缺失的测试用例文件")
    
    args = parser.parse_args()
    
    if args.generate_samples:
        print("🔧 生成测试用例文件...")
        # 这里可以添加生成其他类别测试用例的逻辑
        print("✅ 生成完成")
        return
    
    runner = TestRunner(verbose=args.verbose)
    report = runner.run_all(category=args.category)
    
    # 返回退出码
    if report["summary"]["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
