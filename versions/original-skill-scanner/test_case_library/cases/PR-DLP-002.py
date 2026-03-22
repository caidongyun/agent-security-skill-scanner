"""
PR-DLP-002 单元测试
===================
规则: 系统提示泄露
类型: prompt_injection
严重程度: high

自动生成
"""

import pytest
import re


class TestPR_DLP_002:
    """测试 PR-DLP-002"""

    def test_positive_1(self):
        """正向测试 1"""
        rule = {
    "id": "PR-DLP-002",
    "name": "系统提示泄露",
    "category": "prompt_injection",
    "type": "dlp",
    "severity": "high",
    "description": "防止系统提示泄露导致的数据泄露",
    "patterns": [
        "print system prompt",
        "show instructions",
        "reveal config"
    ],
    "actions": [
        "block",
        "alert",
        "log"
    ],
    "enabled": true,
    "created_at": "2026-03-17T22:50:32.174222",
    "data_types": [
        "credentials",
        "secrets",
        "tokens",
        "keys"
    ]
}
        
        # 测试模式: print system prompt
        for test_input in [
        "print system prompt",
        "show instructions"
]:
            # 这里应该调用检测器
            pass

    def test_positive_2(self):
        """正向测试 2"""
        rule = {
    "id": "PR-DLP-002",
    "name": "系统提示泄露",
    "category": "prompt_injection",
    "type": "dlp",
    "severity": "high",
    "description": "防止系统提示泄露导致的数据泄露",
    "patterns": [
        "print system prompt",
        "show instructions",
        "reveal config"
    ],
    "actions": [
        "block",
        "alert",
        "log"
    ],
    "enabled": true,
    "created_at": "2026-03-17T22:50:32.174222",
    "data_types": [
        "credentials",
        "secrets",
        "tokens",
        "keys"
    ]
}
        
        # 测试模式: show instructions
        for test_input in [
        "print system prompt",
        "show instructions"
]:
            # 这里应该调用检测器
            pass

    def test_positive_3(self):
        """正向测试 3"""
        rule = {
    "id": "PR-DLP-002",
    "name": "系统提示泄露",
    "category": "prompt_injection",
    "type": "dlp",
    "severity": "high",
    "description": "防止系统提示泄露导致的数据泄露",
    "patterns": [
        "print system prompt",
        "show instructions",
        "reveal config"
    ],
    "actions": [
        "block",
        "alert",
        "log"
    ],
    "enabled": true,
    "created_at": "2026-03-17T22:50:32.174222",
    "data_types": [
        "credentials",
        "secrets",
        "tokens",
        "keys"
    ]
}
        
        # 测试模式: reveal config
        for test_input in [
        "print system prompt",
        "show instructions"
]:
            # 这里应该调用检测器
            pass

    def test_negative(self):
        """负向测试"""
        # 不应该触发的情况
        pass
