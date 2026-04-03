#!/usr/bin/env python3
"""
🌐 P2 威胁情报 API 集成
Threat Intelligence API Integration

功能:
1. MITRE ATLAS API (AI 威胁)
2. MITRE ATT&CK API (攻击战术)
3. NVD CVE API (漏洞)
4. GitHub Advisory API (安全公告)
5. 情报自动关联分析
"""

import json
import aiohttp
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

WORKSPACE = Path('/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master')
INTEL_DIR = WORKSPACE / 'intel'
INTEL_DIR.mkdir(exist_ok=True)

@dataclass
class ThreatIntel:
    """威胁情报"""
    id: str
    source: str
    type: str
    title: str
    description: str
    severity: str
    mitre_id: Optional[str]
    published_at: str
    url: str

class ThreatIntelAPI:
    """威胁情报 API 客户端"""
    
    def __init__(self):
        self.session = None
        self.cache = {}
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_mitre_atlas(self, limit: int = 20) -> List[ThreatIntel]:
        """获取 MITRE ATLAS 威胁情报 (AI/ML 威胁)
        
        Args:
            limit: 返回数量限制
        
        Returns:
            威胁情报列表
        """
        print(f"\n📡 采集 MITRE ATLAS (AI 威胁情报)...")
        
        url = "https://raw.githubusercontent.com/mitre-atlas/atlas-staging/master/stix-bundles/attack-pattern.json"
        
        try:
            async with self.session.get(url, timeout=30) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    objects = data.get('objects', [])
                    
                    intel_list = []
                    for obj in objects[:limit]:
                        if obj.get('type') == 'attack-pattern':
                            intel = ThreatIntel(
                                id=obj.get('id', ''),
                                source='MITRE ATLAS',
                                type='ai_threat',
                                title=obj.get('name', ''),
                                description=obj.get('description', ''),
                                severity='high',
                                mitre_id=obj.get('external_references', [{}])[0].get('external_id'),
                                published_at=datetime.now().isoformat(),
                                url=f"https://atlas.mitre.org/techniques/{obj.get('external_references', [{}])[0].get('external_id', '')}"
                            )
                            intel_list.append(intel)
                    
                    print(f"  ✅ 获取 {len(intel_list)} 条 AI 威胁情报")
                    return intel_list
        except Exception as e:
            print(f"  ❌ MITRE ATLAS 采集失败：{e}")
        
        return []
    
    async def fetch_mitre_attack(self, limit: int = 20) -> List[ThreatIntel]:
        """获取 MITRE ATT&CK 威胁情报
        
        Args:
            limit: 返回数量限制
        
        Returns:
            威胁情报列表
        """
        print(f"\n📡 采集 MITRE ATT&CK (企业战术)...")
        
        url = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
        
        try:
            async with self.session.get(url, timeout=30) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    objects = data.get('objects', [])
                    
                    intel_list = []
                    for obj in objects[:limit]:
                        if obj.get('type') == 'attack-pattern':
                            external_refs = obj.get('external_references', [])
                            mitre_id = external_refs[0].get('external_id') if external_refs else ''
                            
                            intel = ThreatIntel(
                                id=obj.get('id', ''),
                                source='MITRE ATT&CK',
                                type='ttp',
                                title=obj.get('name', ''),
                                description=obj.get('description', ''),
                                severity='high',
                                mitre_id=mitre_id,
                                published_at=datetime.now().isoformat(),
                                url=f"https://attack.mitre.org/techniques/{mitre_id.replace('-', '/')}/" if mitre_id else ''
                            )
                            intel_list.append(intel)
                    
                    print(f"  ✅ 获取 {len(intel_list)} 条 ATT&CK 战术")
                    return intel_list
        except Exception as e:
            print(f"  ❌ MITRE ATT&CK 采集失败：{e}")
        
        return []
    
    async def fetch_nvd_cve(self, days: int = 7, limit: int = 20) -> List[ThreatIntel]:
        """获取 NVD CVE 漏洞情报
        
        Args:
            days: 最近 N 天
            limit: 返回数量限制
        
        Returns:
            威胁情报列表
        """
        print(f"\n📡 采集 NVD CVE (最近 {days} 天)...")
        
        base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            "pubStartDate": start_date.strftime('%Y-%m-%dT%H:%M:%S'),
            "resultsPerPage": limit,
        }
        
        try:
            async with self.session.get(base_url, params=params, timeout=30) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    vulnerabilities = data.get('vulnerabilities', [])
                    
                    intel_list = []
                    for vuln in vulnerabilities:
                        cve = vuln.get('cve', {})
                        cve_id = cve.get('id', '')
                        
                        # 获取描述
                        descriptions = cve.get('descriptions', [])
                        description = next(
                            (d.get('value', '') for d in descriptions if d.get('lang') == 'en'),
                            ''
                        )
                        
                        # 获取严重程度
                        metrics = cve.get('metrics', {})
                        cvss = metrics.get('cvssMetricV31', [{}])[0].get('cvssData', {})
                        severity = cvss.get('baseSeverity', 'medium').lower()
                        
                        intel = ThreatIntel(
                            id=cve_id,
                            source='NVD CVE',
                            type='vulnerability',
                            title=cve_id,
                            description=description[:200],  # 截断
                            severity=severity,
                            mitre_id=None,
                            published_at=cve.get('published', datetime.now().isoformat()),
                            url=f"https://nvd.nist.gov/vuln/detail/{cve_id}"
                        )
                        intel_list.append(intel)
                    
                    print(f"  ✅ 获取 {len(intel_list)} 条 CVE 漏洞")
                    return intel_list
        except Exception as e:
            print(f"  ❌ NVD CVE 采集失败：{e}")
        
        return []
    
    async def fetch_github_advisory(self, limit: int = 20) -> List[ThreatIntel]:
        """获取 GitHub Security Advisory
        
        Args:
            limit: 返回数量限制
        
        Returns:
            威胁情报列表
        """
        print(f"\n📡 采集 GitHub Security Advisory...")
        
        url = "https://api.github.com/advisories"
        headers = {'Accept': 'application/vnd.github+json'}
        
        try:
            async with self.session.get(url, headers=headers, timeout=30) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    intel_list = []
                    for advisory in data[:limit]:
                        intel = ThreatIntel(
                            id=advisory.get('ghsa_id', ''),
                            source='GitHub Advisory',
                            type='advisory',
                            title=advisory.get('summary', ''),
                            description=advisory.get('description', '')[:200],
                            severity=advisory.get('severity', 'medium'),
                            mitre_id=None,
                            published_at=advisory.get('published_at', datetime.now().isoformat()),
                            url=advisory.get('html_url', '')
                        )
                        intel_list.append(intel)
                    
                    print(f"  ✅ 获取 {len(intel_list)} 条 GitHub 安全公告")
                    return intel_list
        except Exception as e:
            print(f"  ❌ GitHub Advisory 采集失败：{e}")
        
        return []
    
    async def fetch_all(self) -> Dict[str, List[ThreatIntel]]:
        """并发获取所有威胁情报
        
        Returns:
            各情报源的威胁情报字典
        """
        print("\n" + "="*70)
        print("🌐 并发采集威胁情报 (4 个情报源)...")
        print("="*70)
        
        # 并发执行
        tasks = [
            self.fetch_mitre_atlas(),
            self.fetch_mitre_attack(),
            self.fetch_nvd_cve(),
            self.fetch_github_advisory()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            'mitre_atlas': results[0] if isinstance(results[0], list) else [],
            'mitre_attack': results[1] if isinstance(results[1], list) else [],
            'nvd_cve': results[2] if isinstance(results[2], list) else [],
            'github_advisory': results[3] if isinstance(results[3], list) else []
        }
    
    def save_intel(self, intel_list: List[ThreatIntel], filename: str = None):
        """保存威胁情报到文件
        
        Args:
            intel_list: 威胁情报列表
            filename: 文件名 (默认为时间戳)
        """
        if not filename:
            filename = f"intel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_file = INTEL_DIR / filename
        
        data = [
            {
                'id': intel.id,
                'source': intel.source,
                'type': intel.type,
                'title': intel.title,
                'description': intel.description,
                'severity': intel.severity,
                'mitre_id': intel.mitre_id,
                'published_at': intel.published_at,
                'url': intel.url
            }
            for intel in intel_list
        ]
        
        output_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        print(f"\n💾 保存 {len(data)} 条情报到：{output_file.name}")

# === 便捷函数 ===

async def collect_threat_intel() -> Dict:
    """采集威胁情报 (便捷函数)
    
    Returns:
        采集结果
    """
    async with ThreatIntelAPI() as api:
        results = await api.fetch_all()
        
        # 合并所有情报
        all_intel = []
        for source, intel_list in results.items():
            all_intel.extend(intel_list)
        
        # 保存
        if all_intel:
            api.save_intel(all_intel)
        
        return {
            'total': len(all_intel),
            'by_source': {k: len(v) for k, v in results.items()},
            'timestamp': datetime.now().isoformat()
        }

# === CLI ===

async def main():
    """主函数"""
    print("="*70)
    print("🌐 P2 威胁情报 API 集成")
    print("="*70)
    
    results = await collect_threat_intel()
    
    print("\n" + "="*70)
    print("📊 采集结果")
    print("="*70)
    print(f"总情报数：{results['total']} 条")
    for source, count in results['by_source'].items():
        print(f"  - {source}: {count} 条")

if __name__ == '__main__':
    asyncio.run(main())
