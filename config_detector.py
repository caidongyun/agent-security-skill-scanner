#!/usr/bin/env python3
"""
🔧 配置文件识别器

自动识别 JSON/YAML 配置文件，分离统计
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


class ConfigFileDetector:
    """配置文件检测器"""
    
    # 配置文件扩展名
    CONFIG_EXTENSIONS = {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf'}
    
    # 可执行代码特征
    CODE_PATTERNS = [
        r'function\s+\w+\s*\(',  # 函数定义
        r'def\s+\w+\s*\(',       # Python 函数
        r'class\s+\w+',          # 类定义
        r'import\s+\w+',         # 导入语句
        r'require\s*\(',         # Node.js require
        r'from\s+\w+\s+import',  # Python from import
        r'Invoke-Expression',    # PowerShell IEX
        r'Invoke-Command',       # PowerShell 远程
        r'eval\s*\(',            # eval 执行
        r'exec\s*\(',            # exec 执行
        r'subprocess\.',         # 子进程
        r'os\.system',           # 系统调用
        r'\.DownloadString',     # 下载执行
        r'IEX\s*\(',             # PowerShell IEX
    ]
    
    # 恶意配置特征
    MALICIOUS_CONFIG_PATTERNS = [
        r'attacker',
        r'malicious',
        r'exploit',
        r'payload',
        r'backdoor',
        r'reverse.*shell',
        r'c2.*server',
        r'exfil',
        r'steal.*credential',
    ]
    
    def is_config_file(self, file_path: str, content: str) -> bool:
        """
        判断是否为配置文件
        
        Args:
            file_path: 文件路径
            content: 文件内容
        
        Returns:
            True=配置文件，False=代码文件
        """
        path = Path(file_path)
        ext = path.suffix.lower()
        
        # 检查扩展名
        if ext not in self.CONFIG_EXTENSIONS:
            return False
        
        # 检查是否包含可执行代码
        for pattern in self.CODE_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                return False  # 包含代码，不是纯配置文件
        
        return True  # 纯配置文件
    
    def has_malicious_config(self, file_path: str, content: str) -> bool:
        """
        检查配置文件是否包含恶意配置
        
        Args:
            file_path: 文件路径
            content: 文件内容
        
        Returns:
            True=恶意配置，False=正常配置
        """
        for pattern in self.MALICIOUS_CONFIG_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
    
    def classify_file(self, file_path: str, content: str) -> Tuple[str, str]:
        """
        分类文件
        
        Args:
            file_path: 文件路径
            content: 文件内容
        
        Returns:
            (文件类型，风险等级)
            文件类型：config/code
            风险等级：safe/suspicious/malicious
        """
        if self.is_config_file(file_path, content):
            # 配置文件
            if self.has_malicious_config(file_path, content):
                return ('config', 'malicious')
            else:
                return ('config', 'safe')
        else:
            # 代码文件 (需要进一步扫描)
            return ('code', 'unknown')


# 测试
if __name__ == '__main__':
    detector = ConfigFileDetector()
    
    # 测试用例
    test_cases = [
        ('test.json', '{"name": "test"}', 'config', 'safe'),
        ('test.yaml', 'name: test', 'config', 'safe'),
        ('test.ps1', 'IEX (New-Object Net.WebClient)', 'code', 'unknown'),
        ('evil.json', '{"c2_server": "attacker.com"}', 'config', 'malicious'),
    ]
    
    print("=== 配置文件识别器测试 ===")
    for file_path, content, expected_type, expected_risk in test_cases:
        file_type, risk = detector.classify_file(file_path, content)
        status = "✅" if (file_type == expected_type and risk == expected_risk) else "❌"
        print(f"{status} {file_path}: {file_type}/{risk} (期望：{expected_type}/{expected_risk})")
    
    print("\n✅ 配置文件识别器测试完成")
