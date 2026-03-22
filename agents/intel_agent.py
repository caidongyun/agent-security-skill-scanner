"""
Intel Agent - 威胁情报代理

负责威胁情报采集、分析和更新
"""

import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path
import json

from agents.base_agent import BaseAgent, Task, Result, AgentStatus


class IntelAgent(BaseAgent):
    """情报 Agent - 威胁情报"""
    
    def __init__(self, intel_path: str = "./data/intel/"):
        super().__init__(
            name="IntelAgent",
            description="威胁情报 - 采集/分析/更新",
            capabilities=["intel", "threat", "ioc", "mitre"]
        )
        self.intel_path = Path(intel_path)
        self.intel_path.mkdir(parents=True, exist_ok=True)
        self.ioc_cache = []
        self.mitre_cache = {}
    
    async def execute(self, task: Task) -> Result:
        """执行情报任务"""
        try:
            if task.type == "collect":
                return await self._collect_intel(task)
            elif task.type == "ioc":
                return await self._query_ioc(task)
            elif task.type == "mitre":
                return await self._query_mitre(task)
            elif task.type == "update":
                return await self._update_intel(task)
            elif task.type == "analyze":
                return await self._analyze_threat(task)
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
    
    async def _collect_intel(self, task: Task) -> Result:
        """采集威胁情报"""
        sources = task.parameters.get("sources", ["github", "mitre", "cve"])
        
        collected = {
            'github': [],
            'mitre': [],
            'cve': [],
            'timestamp': asyncio.get_event_loop().time()
        }
        
        for source in sources:
            if source == "github":
                collected['github'] = await self._collect_github_intel()
            elif source == "mitre":
                collected['mitre'] = await self._collect_mitre_intel()
            elif source == "cve":
                collected['cve'] = await self._collect_cve_intel()
        
        # 保存到文件
        self._save_intel(collected)
        
        return Result(
            success=True,
            data=collected
        )
    
    async def _collect_github_intel(self) -> List[Dict]:
        """从 GitHub 采集威胁情报"""
        # 模拟 GitHub 威胁情报采集
        # 实际实现需要调用 GitHub API
        return [
            {
                'source': 'github',
                'type': 'malicious_repo',
                'url': 'https://github.com/example/malicious-skill',
                'description': 'Malicious AI skill with backdoor',
                'severity': 'high',
                'tags': ['backdoor', 'skill-poisoning']
            }
        ]
    
    async def _collect_mitre_intel(self) -> List[Dict]:
        """从 MITRE ATT&CK 采集威胁情报"""
        # 模拟 MITRE ATT&CK 采集
        # 实际实现需要调用 MITRE ATT&CK API
        return [
            {
                'source': 'mitre',
                'technique_id': 'T1190',
                'name': 'Exploit Public-Facing Application',
                'description': 'Adversaries may attempt to exploit a weakness in an Internet-facing host',
                'tactic': 'Initial Access',
                'platforms': ['Containers', 'Windows', 'Linux', 'macOS']
            }
        ]
    
    async def _collect_cve_intel(self) -> List[Dict]:
        """从 CVE 采集威胁情报"""
        # 模拟 CVE 采集
        # 实际实现需要调用 NVD API
        return [
            {
                'source': 'cve',
                'cve_id': 'CVE-2024-1234',
                'description': 'Vulnerability in AI framework',
                'cvss_score': 9.8,
                'severity': 'critical',
                'affected_products': ['AI Framework X']
            }
        ]
    
    async def _query_ioc(self, task: Task) -> Result:
        """查询 IOC (Indicators of Compromise)"""
        query = task.parameters.get("query")
        ioc_type = task.parameters.get("type", "all")
        
        # 从缓存查询
        results = []
        for ioc in self.ioc_cache:
            if ioc_type != "all" and ioc.get('type') != ioc_type:
                continue
            if query and query not in str(ioc):
                continue
            results.append(ioc)
        
        return Result(
            success=True,
            data={
                'count': len(results),
                'iocs': results
            }
        )
    
    async def _query_mitre(self, task: Task) -> Result:
        """查询 MITRE ATT&CK"""
        technique_id = task.parameters.get("technique_id")
        tactic = task.parameters.get("tactic")
        
        # 从缓存查询
        results = []
        for tech in self.mitre_cache.get('techniques', []):
            if technique_id and tech.get('technique_id') != technique_id:
                continue
            if tactic and tech.get('tactic') != tactic:
                continue
            results.append(tech)
        
        return Result(
            success=True,
            data={
                'count': len(results),
                'techniques': results
            }
        )
    
    async def _update_intel(self, task: Task) -> Result:
        """更新威胁情报"""
        intel_data = task.parameters.get("intel_data")
        
        if not intel_data:
            return Result(success=False, error="缺少情报数据")
        
        # 更新 IOC 缓存
        if 'iocs' in intel_data:
            self.ioc_cache.extend(intel_data['iocs'])
        
        # 更新 MITRE 缓存
        if 'mitre' in intel_data:
            self.mitre_cache.update(intel_data['mitre'])
        
        # 保存到文件
        self._save_intel({
            'iocs': self.ioc_cache,
            'mitre': self.mitre_cache,
            'updated_at': asyncio.get_event_loop().time()
        })
        
        return Result(
            success=True,
            data={
                'updated': True,
                'ioc_count': len(self.ioc_cache),
                'mitre_count': len(self.mitre_cache.get('techniques', []))
            }
        )
    
    async def _analyze_threat(self, task: Task) -> Result:
        """分析威胁"""
        target = task.parameters.get("target")
        
        if not target:
            return Result(success=False, error="缺少目标")
        
        # 读取目标内容
        if isinstance(target, str):
            if Path(target).exists():
                with open(target, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = target
        else:
            content = str(target)
        
        # 与 IOC 匹配
        matches = []
        for ioc in self.ioc_cache:
            if ioc.get('pattern') and ioc['pattern'] in content:
                matches.append({
                    'ioc': ioc,
                    'matched_at': content.find(ioc['pattern'])
                })
        
        # 威胁评分
        threat_score = len(matches) * 0.2
        
        return Result(
            success=True,
            data={
                'target': target if isinstance(target, str) else '<content>',
                'ioc_matches': len(matches),
                'matches': matches[:10],  # 最多返回 10 个
                'threat_score': min(threat_score, 1.0),
                'risk_level': self._get_risk_level(threat_score)
            }
        )
    
    def _get_risk_level(self, score: float) -> str:
        """获取风险等级"""
        if score >= 0.8:
            return "critical"
        elif score >= 0.6:
            return "high"
        elif score >= 0.4:
            return "medium"
        elif score >= 0.2:
            return "low"
        else:
            return "none"
    
    def _save_intel(self, intel_data: Dict):
        """保存情报到文件"""
        intel_file = self.intel_path / "threat_intel.json"
        with open(intel_file, 'w', encoding='utf-8') as f:
            json.dump(intel_data, f, indent=2, ensure_ascii=False)
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            'name': self.name,
            'status': self._status.value,
            'capabilities': self.capabilities,
            'tasks_completed': self._tasks_completed,
            'ioc_cache_size': len(self.ioc_cache),
            'mitre_cache_size': len(self.mitre_cache.get('techniques', [])),
            'intel_path': str(self.intel_path)
        }
