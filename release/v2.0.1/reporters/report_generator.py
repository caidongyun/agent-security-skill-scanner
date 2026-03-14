#!/usr/bin/env python3
"""
报告生成器 - 支持 JSON/Console/HTML/SARIF 格式
"""

import json
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class Location:
    file: str
    line: int = None
    column: int = None
    function: str = None


@dataclass
class Finding:
    category: str
    type: str
    severity: str
    description: str
    evidence: str = None
    location: Location = None
    confidence: float = 1.0


@dataclass
class SkillInfo:
    id: str
    name: str
    version: str = "1.0.0"
    author: str = None
    description: str = None
    permissions: List[str] = None
    dependencies: List[str] = None


@dataclass
class ScanResult:
    id: str
    skill: SkillInfo
    score: int
    risk_level: str
    verdict: str
    findings: List[Finding]
    recommendations: List[str]
    scan_time: datetime = None
    duration_ms: int = 0


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        self.level_icon = {
            'SAFE': '🟢',
            'LOW': '🟡',
            'MEDIUM': '🟠',
            'HIGH': '🔴',
            'CRITICAL': '⚫'
        }
        
        self.verdict_icon = {
            'ALLOW': '✅',
            'REVIEW': '⚠️',
            'REJECT': '❌',
            'BLOCK': '🚫'
        }
        
        self.severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    
    def generate_json(self, scan_result: ScanResult) -> dict:
        """生成 JSON 格式报告"""
        return {
            'version': '1.0.0',
            'scan_id': scan_result.id,
            'timestamp': scan_result.scan_time.isoformat() if scan_result.scan_time else datetime.utcnow().isoformat(),
            'skill': {
                'id': scan_result.skill.id,
                'name': scan_result.skill.name,
                'version': scan_result.skill.version,
                'author': scan_result.skill.author
            },
            'risk': {
                'score': scan_result.score,
                'level': scan_result.risk_level,
                'verdict': scan_result.verdict
            },
            'findings': [
                {
                    'category': f.category,
                    'type': f.type,
                    'severity': f.severity,
                    'description': f.description,
                    'evidence': f.evidence,
                    'location': {
                        'file': f.location.file if f.location else None,
                        'line': f.location.line if f.location else None,
                        'column': f.location.column if f.location else None,
                        'function': f.location.function if f.location else None
                    },
                    'confidence': f.confidence
                }
                for f in scan_result.findings
            ],
            'recommendations': scan_result.recommendations,
            'metadata': {
                'scan_duration_ms': scan_result.duration_ms,
                'rules_triggered': len(scan_result.findings),
                'categories': list(set(f.category for f in scan_result.findings))
            }
        }
    
    def generate_console(self, scan_result: ScanResult) -> str:
        """生成终端格式报告"""
        output = []
        
        # 标题
        output.append("=" * 70)
        output.append("Skill Security Scan Report")
        output.append("=" * 70)
        output.append("")
        
        # 基本信息
        output.append(f"Skill: {scan_result.skill.name} v{scan_result.skill.version}")
        output.append(f"Author: {scan_result.skill.author or 'Unknown'}")
        output.append(f"Scan ID: {scan_result.id}")
        if scan_result.scan_time:
            output.append(f"Time: {scan_result.scan_time.strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("")
        
        # 风险评分
        output.append("Risk Assessment:")
        output.append("-" * 70)
        output.append(f"  Risk Score: {scan_result.score}/100")
        output.append(f"  Risk Level: {self.level_icon.get(scan_result.risk_level, '❓')} {scan_result.risk_level}")
        output.append(f"  Verdict: {self.verdict_icon.get(scan_result.verdict, '❓')} {scan_result.verdict}")
        output.append("")
        
        # 分类统计
        categories = {}
        for f in scan_result.findings:
            categories[f.category] = categories.get(f.category, 0) + 1
        
        if categories:
            output.append("Findings by Category:")
            output.append("-" * 70)
            for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
                output.append(f"  {cat}: {count}")
            output.append("")
        
        # 发现列表
        if scan_result.findings:
            output.append(f"Detailed Findings ({len(scan_result.findings)} issues):")
            output.append("-" * 70)
            
            # 按严重程度排序
            sorted_findings = sorted(scan_result.findings, key=lambda f: self.severity_order.get(f.severity, 4))
            
            for i, f in enumerate(sorted_findings, 1):
                severity_icon = {
                    'CRITICAL': '🔴',
                    'HIGH': '🟠',
                    'MEDIUM': '🟡',
                    'LOW': '🟢'
                }
                
                output.append(f"")
                output.append(f"  [{i}] {severity_icon.get(f.severity, '⚪')} {f.severity} - {f.type}")
                output.append(f"      Category: {f.category}")
                output.append(f"      {f.description}")
                
                if f.evidence:
                    output.append(f"      Evidence: {f.evidence}")
                
                if f.location and f.location.file:
                    location = f.location.file
                    if f.location.line:
                        location += f":{f.location.line}"
                    if f.location.function:
                        location += f" ({f.location.function})"
                    output.append(f"      Location: {location}")
                
                if f.confidence < 1.0:
                    output.append(f"      Confidence: {f.confidence:.0%}")
        else:
            output.append("")
            output.append("🎉 No security issues found!")
        
        # 修复建议
        if scan_result.recommendations:
            output.append("")
            output.append("Recommendations:")
            output.append("-" * 70)
            for i, rec in enumerate(scan_result.recommendations, 1):
                output.append(f"  {i}. {rec}")
        
        output.append("")
        output.append("=" * 70)
        output.append(f"Scan completed in {scan_result.duration_ms}ms")
        output.append("=" * 70)
        
        return "\n".join(output)
    
    def generate_html(self, scan_result: ScanResult) -> str:
        """生成 HTML 格式报告"""
        html = []
        
        html.append("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SkillScan Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
        .risk-score { font-size: 48px; font-weight: bold; }
        .SAFE { color: #28a745; }
        .LOW { color: #ffc107; }
        .MEDIUM { color: #fd7e14; }
        .HIGH { color: #dc3545; }
        .CRITICAL { color: #343a40; }
        .finding { border-left: 4px solid #dc3545; padding: 10px; margin: 10px 0; }
        .finding.CRITICAL { border-color: #343a40; }
        .finding.HIGH { border-color: #dc3545; }
        .finding.MEDIUM { border-color: #fd7e14; }
        .finding.LOW { border-color: #ffc107; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f0f0f0; }
    </style>
</head>
<body>
""")
        
        # 头部
        html.append(f"""
    <div class="header">
        <h1>Skill Security Scan Report</h1>
        <p><strong>Skill:</strong> {scan_result.skill.name} v{scan_result.skill.version}</p>
        <p><strong>Author:</strong> {scan_result.skill.author or 'Unknown'}</p>
        <p><strong>Scan ID:</strong> {scan_result.id}</p>
        <p><strong>Time:</strong> {scan_result.scan_time.strftime('%Y-%m-%d %H:%M:%S') if scan_result.scan_time else 'N/A'}</p>
    </div>
""")
        
        # 风险评分
        html.append(f"""
    <h2>Risk Assessment</h2>
    <p class="risk-score {scan_result.risk_level}">{scan_result.score}/100</p>
    <p><strong>Risk Level:</strong> {scan_result.risk_level}</p>
    <p><strong>Verdict:</strong> {scan_result.verdict}</p>
""")
        
        # 发现列表
        if scan_result.findings:
            html.append(f"""
    <h2>Findings ({len(scan_result.findings)} issues)</h2>
    <table>
        <tr>
            <th>#</th>
            <th>Severity</th>
            <th>Type</th>
            <th>Category</th>
            <th>Description</th>
            <th>Location</th>
        </tr>
""")
            
            for i, f in enumerate(scan_result.findings, 1):
                html.append(f"""
        <tr>
            <td>{i}</td>
            <td class="{f.severity}">{f.severity}</td>
            <td>{f.type}</td>
            <td>{f.category}</td>
            <td>{f.description}</td>
            <td>{f.location.file if f.location else 'N/A'}:{f.location.line if f.location else 'N/A'}</td>
        </tr>
""")
            
            html.append("    </table>")
        
        # 修复建议
        if scan_result.recommendations:
            html.append("""
    <h2>Recommendations</h2>
    <ol>
""")
            for rec in scan_result.recommendations:
                html.append(f"        <li>{rec}</li>\n")
            html.append("    </ol>")
        
        html.append("""
</body>
</html>
""")
        
        return "\n".join(html)
    
    def generate(self, scan_result: ScanResult, format: str = 'console') -> str:
        """生成指定格式的报告"""
        if format == 'json':
            return json.dumps(self.generate_json(scan_result), indent=2, ensure_ascii=False)
        elif format == 'html':
            return self.generate_html(scan_result)
        else:
            return self.generate_console(scan_result)


# 使用示例
if __name__ == '__main__':
    # 创建测试数据
    skill = SkillInfo(
        id="test-skill",
        name="Test Skill",
        version="1.0.0",
        author="Test Author"
    )
    
    findings = [
        Finding(
            category="metadata",
            type="SC-META-030",
            severity="HIGH",
            description="Suspicious domain detected",
            evidence="glot.io",
            location=Location(file="skill.yaml", line=10),
            confidence=0.95
        ),
        Finding(
            category="static",
            type="SC-STATIC-006",
            severity="CRITICAL",
            description="Dynamic evaluation",
            evidence="eval()",
            location=Location(file="tool.py", line=45, function="execute_code"),
            confidence=1.0
        )
    ]
    
    result = ScanResult(
        id="scan-20260312-170400-abc123",
        skill=skill,
        score=72,
        risk_level="HIGH",
        verdict="REJECT",
        findings=findings,
        recommendations=[
            "Verify the legitimacy of glot.io domain",
            "Remove eval() usage",
            "Reduce permissions to minimum required"
        ],
        duration_ms=245
    )
    
    # 生成报告
    generator = ReportGenerator()
    
    print("=== JSON Output ===")
    print(generator.generate(result, 'json'))
    
    print("\n=== Console Output ===")
    print(generator.generate(result, 'console'))
