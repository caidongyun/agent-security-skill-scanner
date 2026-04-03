"""
PR-DLP-003 单元测试
===================
规则: 角色扮演攻击
类型: prompt_injection
严重程度: medium

自动生成
"""

import pytest
import re


class TestPR_DLP_003:
    """测试 PR-DLP-003"""

    def test_positive_1(self):
        """正向测试 1"""
        rule = {
    "id": "PR-DLP-003",
    "name": "角色扮演攻击",
    "category": "prompt_injection",
    "type": "dlp",
    "severity": "medium",
    "description": "防止角色扮演攻击导致的数据泄露",
    "patterns": [
        "act as",
        "pretend to be",
        "role play"
    ],
    "actions": [
        "block",
        "alert",
        "log"
    ],
    "enabled": true,
    "created_at": "2026-03-17T22:50:32.174643",
    "data_types": [
        "credentials",
        "secrets",
        "tokens",
        "keys"
    ]
}
        
        # 测试模式: act as
        for test_input in [
        "act as",
        "pretend to be"
]:
            # 这里应该调用检测器
            pass

    def test_positive_2(self):
        """正向测试 2"""
        rule = {
    "id": "PR-DLP-003",
    "name": "角色扮演攻击",
    "category": "prompt_injection",
    "type": "dlp",
    "severity": "medium",
    "description": "防止角色扮演攻击导致的数据泄露",
    "patterns": [
        "act as",
        "pretend to be",
        "role play"
    ],
    "actions": [
        "block",
        "alert",
        "log"
    ],
    "enabled": true,
    "created_at": "2026-03-17T22:50:32.174643",
    "data_types": [
        "credentials",
        "secrets",
        "tokens",
        "keys"
    ]
}
        
        # 测试模式: pretend to be
        for test_input in [
        "act as",
        "pretend to be"
]:
            # 这里应该调用检测器
            pass

    def test_positive_3(self):
        """正向测试 3"""
        rule = {
    "id": "PR-DLP-003",
    "name": "角色扮演攻击",
    "category": "prompt_injection",
    "type": "dlp",
    "severity": "medium",
    "description": "防止角色扮演攻击导致的数据泄露",
    "patterns": [
        "act as",
        "pretend to be",
        "role play"
    ],
    "actions": [
        "block",
        "alert",
        "log"
    ],
    "enabled": true,
    "created_at": "2026-03-17T22:50:32.174643",
    "data_types": [
        "credentials",
        "secrets",
        "tokens",
        "keys"
    ]
}
        
        # 测试模式: role play
        for test_input in [
        "act as",
        "pretend to be"
]:
            # 这里应该调用检测器
            pass

    def test_negative(self):
        """负向测试"""
        # 不应该触发的情况
        pass
