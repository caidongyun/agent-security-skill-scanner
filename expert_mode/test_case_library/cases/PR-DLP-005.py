"""
PR-DLP-005 单元测试
===================
规则: 多语言注入
类型: prompt_injection
严重程度: high

自动生成
"""

import pytest
import re


class TestPR_DLP_005:
    """测试 PR-DLP-005"""

    def test_positive_1(self):
        """正向测试 1"""
        rule = {
    "id": "PR-DLP-005",
    "name": "多语言注入",
    "category": "prompt_injection",
    "type": "dlp",
    "severity": "high",
    "description": "防止多语言注入导致的数据泄露",
    "patterns": [
        "translate to",
        "ignore and",
        "execute this"
    ],
    "actions": [
        "block",
        "alert",
        "log"
    ],
    "enabled": true,
    "created_at": "2026-03-17T22:50:32.175589",
    "data_types": [
        "credentials",
        "secrets",
        "tokens",
        "keys"
    ]
}
        
        # 测试模式: translate to
        for test_input in [
        "translate to",
        "ignore and"
]:
            # 这里应该调用检测器
            pass

    def test_positive_2(self):
        """正向测试 2"""
        rule = {
    "id": "PR-DLP-005",
    "name": "多语言注入",
    "category": "prompt_injection",
    "type": "dlp",
    "severity": "high",
    "description": "防止多语言注入导致的数据泄露",
    "patterns": [
        "translate to",
        "ignore and",
        "execute this"
    ],
    "actions": [
        "block",
        "alert",
        "log"
    ],
    "enabled": true,
    "created_at": "2026-03-17T22:50:32.175589",
    "data_types": [
        "credentials",
        "secrets",
        "tokens",
        "keys"
    ]
}
        
        # 测试模式: ignore and
        for test_input in [
        "translate to",
        "ignore and"
]:
            # 这里应该调用检测器
            pass

    def test_positive_3(self):
        """正向测试 3"""
        rule = {
    "id": "PR-DLP-005",
    "name": "多语言注入",
    "category": "prompt_injection",
    "type": "dlp",
    "severity": "high",
    "description": "防止多语言注入导致的数据泄露",
    "patterns": [
        "translate to",
        "ignore and",
        "execute this"
    ],
    "actions": [
        "block",
        "alert",
        "log"
    ],
    "enabled": true,
    "created_at": "2026-03-17T22:50:32.175589",
    "data_types": [
        "credentials",
        "secrets",
        "tokens",
        "keys"
    ]
}
        
        # 测试模式: execute this
        for test_input in [
        "translate to",
        "ignore and"
]:
            # 这里应该调用检测器
            pass

    def test_negative(self):
        """负向测试"""
        # 不应该触发的情况
        pass
