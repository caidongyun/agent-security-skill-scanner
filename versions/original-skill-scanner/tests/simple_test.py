#!/usr/bin/env python3
"""
🧪 简单测试运行器 - Tool Poisoning
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any

SCRIPT_DIR = Path(__file__).parent
TEST_CASES_DIR = SCRIPT_DIR / "cases"


class SimpleDetector:
    """简单检测器"""
    
    def __init__(self):
        # 工具投毒规则
        self.rules = [
            {"id": "TP01", "pattern": r"base64\s+(-d|-D)", "risk": "HIGH"},
            {"id": "TP01", "pattern": r"b64decode", "risk": "HIGH"},
            {"id": "TP01", "pattern": r"atob\s*\(", "risk": "HIGH"},
            {"id": "TP04", "pattern": r"\beval\s*\(", "risk": "CRITICAL"},
            {"id": "TP04", "pattern": r"\bexec\s*\(", "risk": "CRITICAL"},
            {"id": "TP04", "pattern": r"pickle\.loads?", "risk": "CRITICAL"},
            {"id": "TP03", "pattern": r"__import__\s*\(", "risk": "HIGH"},
            {"id": "TP03", "pattern": r"importlib\.import_module", "risk": "HIGH"},
            {"id": "TP02", "pattern": r"subprocess\.run.*shell\s*=\s*True", "risk": "CRITICAL"},
            {"id": "TP02", "pattern": r"subprocess\.call.*shell\s*=\s*True", "risk": "CRITICAL"},
            {"id": "TP02", "pattern": r"zlib\.decompress", "risk": "MEDIUM"},
            {"id": "TP02", "pattern": r"gzip\.decompress", "risk": "MEDIUM"},
        ]
    
    def detect(self, input_text: str) -> Dict:
        """检测"""
        if isinstance(input_text, dict):
            input_text = input_text.get("content", str(input_text))
        
        input_text = str(input_text)
        matched = []
        
        for rule in self.rules:
            if re.search(rule["pattern"], input_text, re.IGNORECASE):
                matched.append(rule["id"])
        
        return {
            "detected": len(matched) > 0,
            "matched": list(set(matched))
        }


def main():
    detector = SimpleDetector()
    
    # 加载测试用例
    test_file = TEST_CASES_DIR / "tool_poisoning.json"
    with open(test_file) as f:
        cases = json.load(f)
    
    passed = 0
    failed = 0
    
    print(f"\n🧪 测试 Tool Poisoning ({len(cases)} 个用例)")
    print("="*60)
    
    for case in cases:
        case_id = case.get("id", "?")
        name = case.get("name", "?")
        
        # 获取输入
        input_data = case.get("input", {})
        if isinstance(input_data, dict):
            input_text = input_data.get("content", "")
        else:
            input_text = str(input_data)
        
        # 检测
        result = detector.detect(input_text)
        
        # 期望
        expected = case.get("expected", {})
        expected_detected = expected.get("detected", False)
        
        # 判断
        if result["detected"] == expected_detected:
            passed += 1
            print(f"✅ {case_id}: {name}")
        else:
            failed += 1
            print(f"❌ {case_id}: {name}")
            print(f"   期望: {expected_detected}, 实际: {result['detected']}")
    
    print("="*60)
    print(f"📊 结果: ✅ {passed} / ❌ {failed}")
    print(f"📈 通过率: {passed*100/(passed+failed):.1f}%")


if __name__ == "__main__":
    main()
