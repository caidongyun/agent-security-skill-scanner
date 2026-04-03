"""
PR-DLP-004 单元测试
===================
规则: 分隔符绕过
类型: prompt_injection
严重程度: medium

自动生成
"""

import pytest
import re


class TestPR_DLP_004:
    """测试 PR-DLP-004"""

    def test_positive_1(self):
        """正向测试 1"""
        rule = {
    "id": "PR-DLP-004",
    "name": "分隔符绕过",
    "category": "prompt_injection",
    "type": "dlp",
    "severity": "medium",
    "description": "防止分隔符绕过导致的数据泄露",
    "patterns": [
        "\"\"\"",
        "'''",
        "### END ###"
    ],
    "actions": [
        "block",
        "alert",
        "log"
    ],
    "enabled": true,
    "created_at": "2026-03-17T22:50:32.175147",
    "data_types": [
        "credentials",
        "secrets",
        "tokens",
        "keys"
    ]
}
        
        # 测试模式: """
        for test_input in [
        "\"\"\"",
        "'''"
]:
            # 这里应该调用检测器
            pass

    def test_positive_2(self):
        """正向测试 2"""
        rule = {
    "id": "PR-DLP-004",
    "name": "分隔符绕过",
    "category": "prompt_injection",
    "type": "dlp",
    "severity": "medium",
    "description": "防止分隔符绕过导致的数据泄露",
    "patterns": [
        "\"\"\"",
        "'''",
        "### END ###"
    ],
    "actions": [
        "block",
        "alert",
        "log"
    ],
    "enabled": true,
    "created_at": "2026-03-17T22:50:32.175147",
    "data_types": [
        "credentials",
        "secrets",
        "tokens",
        "keys"
    ]
}
        
        # 测试模式: '''
        for test_input in [
        "\"\"\"",
        "'''"
]:
            # 这里应该调用检测器
            pass

    def test_positive_3(self):
        """正向测试 3"""
        rule = {
    "id": "PR-DLP-004",
    "name": "分隔符绕过",
    "category": "prompt_injection",
    "type": "dlp",
    "severity": "medium",
    "description": "防止分隔符绕过导致的数据泄露",
    "patterns": [
        "\"\"\"",
        "'''",
        "### END ###"
    ],
    "actions": [
        "block",
        "alert",
        "log"
    ],
    "enabled": true,
    "created_at": "2026-03-17T22:50:32.175147",
    "data_types": [
        "credentials",
        "secrets",
        "tokens",
        "keys"
    ]
}
        
        # 测试模式: ### END ###
        for test_input in [
        "\"\"\"",
        "'''"
]:
            # 这里应该调用检测器
            pass

    def test_negative(self):
        """负向测试"""
        # 不应该触发的情况
        pass
