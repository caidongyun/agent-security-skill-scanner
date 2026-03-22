"""
PR-DLP-001 单元测试
===================
规则: 指令覆盖攻击
类型: prompt_injection
严重程度: high

自动生成
"""

import pytest
import re


class TestPR_DLP_001:
    """测试 PR-DLP-001"""

    def test_positive_1(self):
        """正向测试 1"""
        rule = {
    "id": "PR-DLP-001",
    "name": "指令覆盖攻击",
    "category": "prompt_injection",
    "type": "dlp",
    "severity": "high",
    "description": "防止指令覆盖攻击导致的数据泄露",
    "patterns": [
        "ignore previous",
        "forget all",
        "disregard instructions"
    ],
    "actions": [
        "block",
        "alert",
        "log"
    ],
    "enabled": true,
    "created_at": "2026-03-17T22:50:32.173828",
    "data_types": [
        "credentials",
        "secrets",
        "tokens",
        "keys"
    ]
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
    "id": "PR-DLP-001",
    "name": "指令覆盖攻击",
    "category": "prompt_injection",
    "type": "dlp",
    "severity": "high",
    "description": "防止指令覆盖攻击导致的数据泄露",
    "patterns": [
        "ignore previous",
        "forget all",
        "disregard instructions"
    ],
    "actions": [
        "block",
        "alert",
        "log"
    ],
    "enabled": true,
    "created_at": "2026-03-17T22:50:32.173828",
    "data_types": [
        "credentials",
        "secrets",
        "tokens",
        "keys"
    ]
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
    "id": "PR-DLP-001",
    "name": "指令覆盖攻击",
    "category": "prompt_injection",
    "type": "dlp",
    "severity": "high",
    "description": "防止指令覆盖攻击导致的数据泄露",
    "patterns": [
        "ignore previous",
        "forget all",
        "disregard instructions"
    ],
    "actions": [
        "block",
        "alert",
        "log"
    ],
    "enabled": true,
    "created_at": "2026-03-17T22:50:32.173828",
    "data_types": [
        "credentials",
        "secrets",
        "tokens",
        "keys"
    ]
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
