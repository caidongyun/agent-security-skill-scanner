#!/usr/bin/env python3
"""
元数据检测器 - 检测 Skill 元数据中的安全风险

检测内容:
- SKILL.yaml/skill.yaml 解析
- 外部链接提取
- 可疑域名检测
- 加密文件要求
- 异常权限组合
"""

import re
import yaml
from typing import List, Dict, Optional
from pathlib import Path


class MetadataDetector:
    """元数据检测器"""
    
    # 可疑域名模式
    SUSPICIOUS_DOMAINS = [
        r'glot\.io',
        r'transfer\.sh',
        r'paste\.ee',
        r'pastebin\.com',
        r'ipfs\.io',
        r'bit\.ly',  # 短链接
        r'tinyurl\.com',  # 短链接
    ]
    
    # 可疑模式
    SUSPICIOUS_PATTERNS = [
        r'password.*zip',           # 加密文件
        r'encrypted.*file',         # 加密文件
        r'download.*\.(exe|zip|sh|bat)',  # 可执行文件
        r'execute.*script',         # 执行脚本
        r'run.*external',           # 运行外部程序
        r'install.*agent',          # 安装代理
    ]
    
    # 异常权限组合
    DANGEROUS_PERMISSIONS = [
        {'read_all_files', 'network_access'},
        {'shell_exec', 'internet_access'},
        {'read_credentials', 'network_upload'},
        {'execute_code', 'file_write'},
    ]
    
    # 敏感文件模式
    SENSITIVE_FILES = [
        r'~/.ssh/',
        r'~/.aws/',
        r'~/.azure/',
        r'~/.kube/',
        r'\.env$',
        r'credentials',
        r'secrets',
        r'password',
    ]
    
    def __init__(self):
        self.findings = []
    
    def scan_skill(self, skill_path: str) -> Dict:
        """扫描 Skill 元数据"""
        self.findings = []
        
        # 查找 skill.yaml 或 SKILL.yaml
        skill_files = list(Path(skill_path).rglob('skill.yaml'))
        skill_files.extend(list(Path(skill_path).rglob('SKILL.yaml')))
        
        if not skill_files:
            return {
                'status': 'NO_METADATA',
                'message': 'No skill.yaml found',
                'risk_score': 0
            }
        
        # 扫描第一个找到的 skill.yaml
        skill_file = skill_files[0]
        return self._scan_metadata_file(skill_file)
    
    def _scan_metadata_file(self, file_path: Path) -> Dict:
        """扫描元数据文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                metadata = yaml.safe_load(f)
        except Exception as e:
            return {
                'status': 'PARSE_ERROR',
                'message': f'Failed to parse skill.yaml: {str(e)}',
                'risk_score': 50
            }
        
        # 执行各项检查
        self._check_external_links(metadata)
        self._check_suspicious_patterns(metadata)
        self._check_permissions(metadata)
        self._check_dependencies(metadata)
        
        # 计算风险评分
        risk_score = self._calculate_risk_score()
        
        return {
            'status': 'COMPLETED',
            'findings': self.findings,
            'risk_score': risk_score,
            'risk_level': self._get_risk_level(risk_score),
            'metadata': metadata
        }
    
    def _check_external_links(self, metadata: Dict):
        """检查外部链接"""
        # 从 description 中提取链接
        description = metadata.get('description', '')
        
        # 提取所有 URL
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, description)
        
        # 检查每个 URL
        for url in urls:
            # 检查可疑域名
            for pattern in self.SUSPICIOUS_DOMAINS:
                if re.search(pattern, url, re.IGNORECASE):
                    self.findings.append({
                        'type': 'SUSPICIOUS_DOMAIN',
                        'severity': 'HIGH',
                        'finding': f'Suspicious domain detected: {url}',
                        'pattern': pattern,
                        'recommendation': 'Verify the legitimacy of this domain'
                    })
    
    def _check_suspicious_patterns(self, metadata: Dict):
        """检查可疑模式"""
        # 检查 description
        description = metadata.get('description', '')
        
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, description, re.IGNORECASE):
                self.findings.append({
                    'type': 'SUSPICIOUS_PATTERN',
                    'severity': 'MEDIUM',
                    'finding': f'Suspicious pattern in description: {pattern}',
                    'recommendation': 'Review the skill requirements'
                })
        
        # 检查其他字段
        for field in ['installation', 'requirements', 'notes']:
            value = str(metadata.get(field, ''))
            for pattern in self.SUSPICIOUS_PATTERNS:
                if re.search(pattern, value, re.IGNORECASE):
                    self.findings.append({
                        'type': 'SUSPICIOUS_PATTERN',
                        'severity': 'MEDIUM',
                        'finding': f'Suspicious pattern in {field}: {pattern}',
                        'recommendation': 'Review this field carefully'
                    })
    
    def _check_permissions(self, metadata: Dict):
        """检查权限"""
        permissions = set(metadata.get('permissions', []))
        
        # 检查危险权限组合
        for dangerous_combo in self.DANGEROUS_PERMISSIONS:
            if dangerous_combo.issubset(permissions):
                self.findings.append({
                    'type': 'DANGEROUS_PERMISSIONS',
                    'severity': 'HIGH',
                    'finding': f'Dangerous permission combination: {dangerous_combo}',
                    'recommendation': 'Reduce permissions to minimum required'
                })
        
        # 检查过度权限
        excessive_perms = [
            'read_all_files',
            'write_all_files',
            'execute_any',
            'full_network',
        ]
        
        for perm in excessive_perms:
            if perm in permissions:
                self.findings.append({
                    'type': 'EXCESSIVE_PERMISSION',
                    'severity': 'MEDIUM',
                    'finding': f'Excessive permission: {perm}',
                    'recommendation': 'Use more specific permissions'
                })
    
    def _check_dependencies(self, metadata: Dict):
        """检查依赖"""
        dependencies = metadata.get('dependencies', [])
        
        # 检查可疑依赖
        suspicious_packages = [
            'requests-lite',  # typosquatting
            'pandas-lite',
            'numpy-lite',
        ]
        
        for dep in dependencies:
            dep_name = dep.split('>')[0].split('=')[0].strip()
            
            # 检查仿冒包
            if dep_name in suspicious_packages:
                self.findings.append({
                    'type': 'TYPOSQUATTING',
                    'severity': 'HIGH',
                    'finding': f'Possible typosquatting package: {dep_name}',
                    'recommendation': 'Verify the package name'
                })
            
            # 检查新注册包 (简单检查)
            if '-' in dep_name and dep_name.count('-') >= 2:
                self.findings.append({
                    'type': 'SUSPICIOUS_PACKAGE',
                    'severity': 'LOW',
                    'finding': f'Suspicious package name: {dep_name}',
                    'recommendation': 'Verify the package legitimacy'
                })
    
    def _calculate_risk_score(self) -> int:
        """计算风险评分"""
        score = 0
        
        for finding in self.findings:
            severity = finding.get('severity', 'LOW')
            
            if severity == 'HIGH':
                score += 30
            elif severity == 'MEDIUM':
                score += 15
            elif severity == 'LOW':
                score += 5
        
        return min(score, 100)
    
    def _get_risk_level(self, score: int) -> str:
        """获取风险等级"""
        if score >= 80:
            return 'CRITICAL'
        elif score >= 60:
            return 'HIGH'
        elif score >= 40:
            return 'MEDIUM'
        elif score >= 20:
            return 'LOW'
        else:
            return 'SAFE'
    
    def generate_report(self, result: Dict) -> str:
        """生成人类可读报告"""
        lines = []
        lines.append("=" * 60)
        lines.append("Metadata Security Report")
        lines.append("=" * 60)
        lines.append("")
        
        # 风险等级
        risk_level = result.get('risk_level', 'UNKNOWN')
        risk_score = result.get('risk_score', 0)
        
        lines.append(f"Risk Level: {risk_level}")
        lines.append(f"Risk Score: {risk_score}/100")
        lines.append("")
        
        # 发现
        findings = result.get('findings', [])
        if findings:
            lines.append(f"Findings: {len(findings)}")
            lines.append("-" * 60)
            
            for i, finding in enumerate(findings, 1):
                lines.append(f"\n[{i}] {finding['type']}")
                lines.append(f"    Severity: {finding['severity']}")
                lines.append(f"    Finding: {finding['finding']}")
                lines.append(f"    Recommendation: {finding['recommendation']}")
        else:
            lines.append("No security issues found! ✅")
        
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python metadata.py <skill_directory>")
        sys.exit(1)
    
    detector = MetadataDetector()
    result = detector.scan_skill(sys.argv[1])
    
    print(detector.generate_report(result))
    
    # 输出 JSON
    import json
    print("\nJSON Output:")
    print(json.dumps(result, indent=2))
