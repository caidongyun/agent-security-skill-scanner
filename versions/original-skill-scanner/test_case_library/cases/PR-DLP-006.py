"""
PR-DLP-006 单元测试
===================
规则: 上下文污染
类型: prompt_injection
严重程度: high

自动生成
"""

import pytest
import re


class TestPR_DLP_006:
    """测试 PR-DLP-006"""

    def test_positive_1(self):
        """正向测试 1"""
        rule = {
    "id": "PR-DLP-006",
    "name": "上下文污染",
    "category": "prompt_injection",
    "type": "dlp",
    "severity": "high",
    "description": "防止上下文污染导致的数据泄露",
    "patterns": [
        "new context",
        "reset memory",
        "clear history"
    ],
    "actions": [
        "block",
        "alert",
        "log"
    ],
    "enabled": true,
    "created_at": "2026-03-17T22:50:32.176017",
    "data_types": [
        "credentials",
        "secrets",
        "tokens",
        "keys"
    ]
}
        
        # 测试模式: new context
        for test_input in [
        "new context",
        "reset memory"
]:
            # 这里应该调用检测器
            pass

    def test_positive_2(self):
        """正向测试 2"""
        rule = {
    "id": "PR-DLP-006",
    "name": "上下文污染",
    "category": "prompt_injection",
    "type": "dlp",
    "severity": "high",
    "description": "防止上下文污染导致的数据泄露",
    "patterns": [
        "new context",
        "reset memory",
        "clear history"
    ],
    "actions": [
        "block",
        "alert",
        "log"
    ],
    "enabled": true,
    "created_at": "2026-03-17T22:50:32.176017",
    "data_types": [
        "credentials",
        "secrets",
        "tokens",
        "keys"
    ]
}
        
        # 测试模式: reset memory
        for test_input in [
        "new context",
        "reset memory"
]:
            # 这里应该调用检测器
            pass

    def test_positive_3(self):
        """正向测试 3"""
        rule = {
    "id": "PR-DLP-006",
    "name": "上下文污染",
    "category": "prompt_injection",
    "type": "dlp",
    "severity": "high",
    "description": "防止上下文污染导致的数据泄露",
    "patterns": [
        "new context",
        "reset memory",
        "clear history"
    ],
    "actions": [
        "block",
        "alert",
        "log"
    ],
    "enabled": true,
    "created_at": "2026-03-17T22:50:32.176017",
    "data_types": [
        "credentials",
        "secrets",
        "tokens",
        "keys"
    ]
}
        
        # 测试模式: clear history
        for test_input in [
        "new context",
        "reset memory"
]:
            # 这里应该调用检测器
            pass

    def test_negative(self):
        """负向测试"""
        # 不应该触发的情况
        pass
