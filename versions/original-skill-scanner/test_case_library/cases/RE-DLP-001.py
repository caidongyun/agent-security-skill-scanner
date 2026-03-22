"""
RE-DLP-001 单元测试
===================
规则: 远程代码加载
类型: remote_load
严重程度: high

自动生成
"""

import pytest
import re


class TestRE_DLP_001:
    """测试 RE-DLP-001"""

    def test_positive_1(self):
        """正向测试 1"""
        rule = {
    "id": "RE-DLP-001",
    "name": "远程代码加载",
    "category": "remote_load",
    "type": "dlp",
    "severity": "high",
    "description": "防止远程代码加载导致的数据泄露",
    "patterns": [
        "curl|bash",
        "wget|sh",
        "curl -fsSL"
    ],
    "actions": [
        "block",
        "alert",
        "log"
    ],
    "enabled": true,
    "created_at": "2026-03-17T22:50:32.169228",
    "data_types": [
        "credentials",
        "secrets",
        "tokens",
        "keys"
    ],
    "test_cases": {
        "positive": [
            "curl|bash",
            "wget|sh"
        ],
        "negative": []
    }
}
        
        # 测试模式: curl|bash
        for test_input in [
        "curl|bash",
        "wget|sh"
]:
            # 这里应该调用检测器
            pass

    def test_positive_2(self):
        """正向测试 2"""
        rule = {
    "id": "RE-DLP-001",
    "name": "远程代码加载",
    "category": "remote_load",
    "type": "dlp",
    "severity": "high",
    "description": "防止远程代码加载导致的数据泄露",
    "patterns": [
        "curl|bash",
        "wget|sh",
        "curl -fsSL"
    ],
    "actions": [
        "block",
        "alert",
        "log"
    ],
    "enabled": true,
    "created_at": "2026-03-17T22:50:32.169228",
    "data_types": [
        "credentials",
        "secrets",
        "tokens",
        "keys"
    ],
    "test_cases": {
        "positive": [
            "curl|bash",
            "wget|sh"
        ],
        "negative": []
    }
}
        
        # 测试模式: wget|sh
        for test_input in [
        "curl|bash",
        "wget|sh"
]:
            # 这里应该调用检测器
            pass

    def test_positive_3(self):
        """正向测试 3"""
        rule = {
    "id": "RE-DLP-001",
    "name": "远程代码加载",
    "category": "remote_load",
    "type": "dlp",
    "severity": "high",
    "description": "防止远程代码加载导致的数据泄露",
    "patterns": [
        "curl|bash",
        "wget|sh",
        "curl -fsSL"
    ],
    "actions": [
        "block",
        "alert",
        "log"
    ],
    "enabled": true,
    "created_at": "2026-03-17T22:50:32.169228",
    "data_types": [
        "credentials",
        "secrets",
        "tokens",
        "keys"
    ],
    "test_cases": {
        "positive": [
            "curl|bash",
            "wget|sh"
        ],
        "negative": []
    }
}
        
        # 测试模式: curl -fsSL
        for test_input in [
        "curl|bash",
        "wget|sh"
]:
            # 这里应该调用检测器
            pass

    def test_negative(self):
        """负向测试"""
        # 不应该触发的情况
        pass
