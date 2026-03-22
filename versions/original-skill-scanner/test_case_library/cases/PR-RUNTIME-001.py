"""
PR-RUNTIME-001 单元测试
===================
规则: 指令覆盖攻击
类型: prompt_injection
严重程度: high

自动生成
"""

import pytest
import re


class TestPR_RUNTIME_001:
    """测试 PR-RUNTIME-001"""

    def test_positive_1(self):
        """正向测试 1"""
        rule = {
    "id": "PR-RUNTIME-001",
    "name": "指令覆盖攻击",
    "category": "prompt_injection",
    "severity": "high",
    "description": "检测指令覆盖攻击攻击",
    "patterns": [
        "ignore previous",
        "forget all",
        "disregard instructions"
    ],
    "risk_score": 90,
    "enabled": true,
    "created_at": "2026-03-17T22:50:32.173758",
    "action": "block",
    "test_cases": {
        "positive": [
            "ignore previous",
            "forget all"
        ],
        "negative": []
    }
}
        
        # 测试模式: ignore previous
        for test_input in [
        "ignore previous",
        "forget all"
]:
            # 这里应该调用检测器
            pass

    def test_positive_2(self):
        """正向测试 2"""
        rule = {
    "id": "PR-RUNTIME-001",
    "name": "指令覆盖攻击",
    "category": "prompt_injection",
    "severity": "high",
    "description": "检测指令覆盖攻击攻击",
    "patterns": [
        "ignore previous",
        "forget all",
        "disregard instructions"
    ],
    "risk_score": 90,
    "enabled": true,
    "created_at": "2026-03-17T22:50:32.173758",
    "action": "block",
    "test_cases": {
        "positive": [
            "ignore previous",
            "forget all"
        ],
        "negative": []
    }
}
        
        # 测试模式: forget all
        for test_input in [
        "ignore previous",
        "forget all"
]:
            # 这里应该调用检测器
            pass

    def test_positive_3(self):
        """正向测试 3"""
        rule = {
    "id": "PR-RUNTIME-001",
    "name": "指令覆盖攻击",
    "category": "prompt_injection",
    "severity": "high",
    "description": "检测指令覆盖攻击攻击",
    "patterns": [
        "ignore previous",
        "forget all",
        "disregard instructions"
    ],
    "risk_score": 90,
    "enabled": true,
    "created_at": "2026-03-17T22:50:32.173758",
    "action": "block",
    "test_cases": {
        "positive": [
            "ignore previous",
            "forget all"
        ],
        "negative": []
    }
}
        
        # 测试模式: disregard instructions
        for test_input in [
        "ignore previous",
        "forget all"
]:
            # 这里应该调用检测器
            pass

    def test_negative(self):
        """负向测试"""
        # 不应该触发的情况
        pass
