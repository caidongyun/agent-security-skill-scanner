"""
Reporter Agent - 报告生成代理

负责生成检测报告、统计分析和可视化
"""

import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from datetime import datetime

from agents.base_agent import BaseAgent, Task, Result, AgentStatus


class ReporterAgent(BaseAgent):
    """报告 Agent - 报告生成"""
    
    def __init__(self, reports_path: str = "./reports/"):
        super().__init__(
            name="ReporterAgent",
            description="报告生成 - 检测/统计/可视化",
            capabilities=["report", "stats", "visualize", "export"]
        )
        self.reports_path = Path(reports_path)
        self.reports_path.mkdir(parents=True, exist_ok=True)
        self.report_history = []
    
    async def execute(self, task: Task) -> Result:
        """执行报告任务"""
        try:
            if task.type == "generate":
                return await self._generate_report(task)
            elif task.type == "stats":
                return await self._generate_stats(task)
            elif task.type == "summary":
                return await self._generate_summary(task)
            elif task.type == "export":
                return await self._export_report(task)
            elif task.type == "visualize":
                return await self._generate_visualization(task)
            else:
                return Result(
                    success=False,
                    error=f"未知任务类型：{task.type}"
                )
        except Exception as e:
            return Result(
                success=False,
                error=str(e)
            )
    
    async def _generate_report(self, task: Task) -> Result:
        """生成检测报告"""
        scan_results = task.parameters.get("scan_results", [])
        report_format = task.parameters.get("format", "markdown")
        output_file = task.parameters.get("output_file")
        
        # 生成报告内容
        report = {
            'title': '安全检测报告',
            'generated_at': datetime.now().isoformat(),
            'summary': self._generate_summary_data(scan_results),
            'details': scan_results,
            'recommendations': self._generate_recommendations(scan_results)
        }
        
        # 格式化报告
        if report_format == "markdown":
            content = self._format_markdown(report)
        elif report_format == "json":
            content = json.dumps(report, indent=2, ensure_ascii=False)
        elif report_format == "html":
            content = self._format_html(report)
        else:
            content = str(report)
        
        # 保存报告
        if output_file:
            output_path = Path(output_file)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.reports_path / f"report_{timestamp}.md"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 记录历史
        self.report_history.append({
            'file': str(output_path),
            'timestamp': report['generated_at'],
            'format': report_format
        })
        
        return Result(
            success=True,
            data={
                'report_file': str(output_path),
                'format': report_format,
                'summary': report['summary']
            }
        )
    
    def _generate_summary_data(self, scan_results: List[Dict]) -> Dict:
        """生成摘要数据"""
        total_files = len(scan_results)
        malicious_count = sum(1 for r in scan_results if r.get('is_malicious', False))
        benign_count = total_files - malicious_count
        
        # 按攻击类型统计
        attack_types = {}
        for result in scan_results:
            if result.get('is_malicious'):
                for match in result.get('matches', []):
                    attack_type = match.get('attack_type', 'unknown')
                    attack_types[attack_type] = attack_types.get(attack_type, 0) + 1
        
        # 按严重程度统计
        severities = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for result in scan_results:
            for match in result.get('matches', []):
                severity = match.get('severity', 'low')
                if severity in severities:
                    severities[severity] += 1
        
        return {
            'total_files': total_files,
            'malicious_files': malicious_count,
            'benign_files': benign_count,
            'detection_rate': malicious_count / total_files if total_files > 0 else 0,
            'attack_types': attack_types,
            'severities': severities
        }
    
    def _generate_recommendations(self, scan_results: List[Dict]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        malicious_count = sum(1 for r in scan_results if r.get('is_malicious', False))
        
        if malicious_count > 0:
            recommendations.append(f"发现 {malicious_count} 个恶意文件，建议立即隔离")
        
        # 检查高风险问题
        high_risk = sum(1 for r in scan_results 
                       for m in r.get('matches', []) 
                       if m.get('severity') in ['critical', 'high'])
        
        if high_risk > 0:
            recommendations.append(f"发现 {high_risk} 个高风险问题，建议优先处理")
        
        # 通用建议
        recommendations.append("定期更新检测规则库")
        recommendations.append("对可疑代码进行人工审查")
        recommendations.append("建立代码安全审查流程")
        
        return recommendations
    
    def _format_markdown(self, report: Dict) -> str:
        """格式化为 Markdown"""
        lines = []
        
        lines.append(f"# {report['title']}")
        lines.append("")
        lines.append(f"**生成时间**: {report['generated_at']}")
        lines.append("")
        
        # 摘要
        summary = report['summary']
        lines.append("## 📊 检测摘要")
        lines.append("")
        lines.append(f"- 总文件数：{summary['total_files']}")
        lines.append(f"- 恶意文件：{summary['malicious_files']}")
        lines.append(f"- 良性文件：{summary['benign_files']}")
        lines.append(f"- 检测率：{summary['detection_rate']:.2%}")
        lines.append("")
        
        # 攻击类型分布
        if summary['attack_types']:
            lines.append("### 攻击类型分布")
            lines.append("")
            for attack_type, count in summary['attack_types'].items():
                lines.append(f"- {attack_type}: {count}")
            lines.append("")
        
        # 严重程度分布
        lines.append("### 严重程度分布")
        lines.append("")
        for severity, count in summary['severities'].items():
            if count > 0:
                lines.append(f"- {severity.upper()}: {count}")
        lines.append("")
        
        # 详细信息
        lines.append("## 🔍 检测详情")
        lines.append("")
        
        malicious_results = [r for r in report['details'] if r.get('is_malicious')]
        if malicious_results:
            for i, result in enumerate(malicious_results[:20], 1):  # 最多显示 20 个
                lines.append(f"### {i}. {result.get('file', 'Unknown')}")
                lines.append("")
                lines.append(f"**风险评分**: {result.get('risk_score', 0):.2f}")
                lines.append("")
                lines.append("**匹配规则**:")
                for match in result.get('matches', [])[:5]:  # 最多显示 5 条
                    lines.append(f"- {match.get('rule_name', 'Unknown')} ({match.get('severity', 'unknown')})")
                lines.append("")
        else:
            lines.append("✅ 未发现恶意文件")
            lines.append("")
        
        # 建议
        lines.append("## 💡 建议")
        lines.append("")
        for i, rec in enumerate(report['recommendations'], 1):
            lines.append(f"{i}. {rec}")
        lines.append("")
        
        return '\n'.join(lines)
    
    def _format_html(self, report: Dict) -> str:
        """格式化为 HTML"""
        # 简化的 HTML 报告
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{report['title']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .malicious {{ color: red; }}
        .benign {{ color: green; }}
    </style>
</head>
<body>
    <h1>{report['title']}</h1>
    <p>生成时间：{report['generated_at']}</p>
    <div class="summary">
        <h2>检测摘要</h2>
        <p>总文件数：{report['summary']['total_files']}</p>
        <p class="malicious">恶意文件：{report['summary']['malicious_files']}</p>
        <p class="benign">良性文件：{report['summary']['benign_files']}</p>
    </div>
</body>
</html>
"""
        return html
    
    async def _generate_stats(self, task: Task) -> Result:
        """生成统计信息"""
        time_range = task.parameters.get("time_range", "all")
        
        # 从历史报告中统计
        stats = {
            'total_reports': len(self.report_history),
            'total_files_scanned': 0,
            'total_malicious': 0,
            'average_detection_rate': 0
        }
        
        return Result(success=True, data=stats)
    
    async def _generate_summary(self, task: Task) -> Result:
        """生成摘要"""
        scan_results = task.parameters.get("scan_results", [])
        
        summary = self._generate_summary_data(scan_results)
        
        return Result(
            success=True,
            data=summary
        )
    
    async def _export_report(self, task: Task) -> Result:
        """导出报告"""
        report_file = task.parameters.get("report_file")
        export_format = task.parameters.get("format", "pdf")
        
        # 简化的导出逻辑
        return Result(
            success=True,
            data={
                'exported': True,
                'format': export_format,
                'message': '导出功能待实现'
            }
        )
    
    async def _generate_visualization(self, task: Task) -> Result:
        """生成可视化"""
        scan_results = task.parameters.get("scan_results", [])
        viz_type = task.parameters.get("type", "chart")
        
        # 简化的可视化逻辑
        return Result(
            success=True,
            data={
                'type': viz_type,
                'data': self._generate_summary_data(scan_results),
                'message': '可视化功能待实现 (可使用 matplotlib/plotly)'
            }
        )
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            'name': self.name,
            'status': self._status.value,
            'capabilities': self.capabilities,
            'tasks_completed': self._tasks_completed,
            'report_history_count': len(self.report_history),
            'reports_path': str(self.reports_path)
        }
