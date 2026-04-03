#!/usr/bin/env python3
"""
威胁情报采集器
自动采集 CVE/NVD, MITRE ATLAS, GitHub Advisory 数据
"""

import json
import asyncio
import aiohttp
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class ThreatIntel:
    """威胁情报数据"""
    id: str
    source: str
    type: str  # cve, mitre, github
    title: str
    description: str
    severity: str  # critical, high, medium, low
    published_at: str
    attack_patterns: List[str]
    raw: Dict


class IntelligenceCollector:
    """威胁情报采集器"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or "intel")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.intel: List[ThreatIntel] = []
    
    async def fetch_cve(self, days: int = 7) -> List[ThreatIntel]:
        """从 NVD API 获取最新 CVE"""
        print(f"📡 采集 CVE 数据 (最近 {days} 天)...")
        
        # NVD API 2.0 endpoint
        base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        
        # 计算时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            "pubStartDate": start_date.isoformat(),
            "resultsPerPage": 50,
        }
        
        cve_list = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(base_url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        vulnerabilities = data.get("vulnerabilities", [])
                        
                        for vuln in vulnerabilities:
                            cve = vuln.get("cve", {})
                            cve_id = cve.get("id", "")
                            descriptions = cve.get("descriptions", [])
                            
                            # 获取英文描述
                            description = ""
                            for desc in descriptions:
                                if desc.get("lang") == "en":
                                    description = desc.get("value", "")
                                    break
                            
                            # 获取严重程度
                            metrics = cve.get("metrics", {})
                            severity = "medium"
                            if metrics.get("cvssMetricV31"):
                                severity = metrics["cvssMetricV31"][0]["cvssData"]["baseSeverity"].lower()
                            
                            # 提取关键词
                            keywords = self._extract_keywords(description)
                            
                            intel = ThreatIntel(
                                id=cve_id,
                                source="nvd",
                                type="cve",
                                title=cve_id,
                                description=description[:500],
                                severity=severity,
                                published_at=cve.get("published", ""),
                                attack_patterns=keywords,
                                raw=cve
                            )
                            cve_list.append(intel)
                        
                        print(f"  ✅ 获取 {len(cve_list)} 个 CVE")
                    else:
                        print(f"  ⚠️ NVD API 返回: {resp.status}")
        
        except Exception as e:
            print(f"  ❌ CVE 采集失败: {e}")
        
        return cve_list
    
    async def fetch_github_advisory(self, ecosystem: str = "pip", count: int = 20) -> List[ThreatIntel]:
        """从 GitHub Advisory 获取安全公告"""
        print(f"📡 采集 GitHub Advisory ({ecosystem})...")
        
        # GraphQL API
        query = """
        query($ecosystem: SecurityAdvisoryEcosystem, $first: Int) {
          securityAdvisories(
            ecosystem: $ecosystem,
            first: $first,
            orderBy: {field: PUBLISHED_AT, direction: DESC}
          ) {
            nodes {
              ghsaId
              summary
              description
              severity
              publishedAt
              vulnerabilities(first: 5) {
                nodes {
                  package {
                    name
                    ecosystem
                  }
                }
              }
            }
          }
        }
        """
        
        # 使用 REST API 替代
        url = f"https://api.github.com/advisories?type=reviewed&ecosystem={ecosystem}&per_page={count}"
        
        advisories = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        for adv in data:
                            keywords = self._extract_keywords(adv.get("description", ""))
                            
                            intel = ThreatIntel(
                                id=adv.get("ghsa_id", ""),
                                source="github",
                                type="advisory",
                                title=adv.get("summary", "")[:100],
                                description=adv.get("description", "")[:500],
                                severity=adv.get("severity", "medium").lower(),
                                published_at=adv.get("published_at", ""),
                                attack_patterns=keywords,
                                raw=adv
                            )
                            advisories.append(intel)
                        
                        print(f"  ✅ 获取 {len(advisories)} 个 GitHub Advisory")
                    else:
                        print(f"  ⚠️ GitHub API 返回: {resp.status}")
        
        except Exception as e:
            print(f"  ❌ GitHub Advisory 采集失败: {e}")
        
        return advisories
    
    async def fetch_mitre_atlas(self) -> List[ThreatIntel]:
        """从 MITRE ATLAS 获取攻击战术"""
        print("📡 采集 MITRE ATLAS 攻击战术...")
        
        # MITRE ATLAS API
        url = "https://atlas.mitre.org/api/techniques"
        
        techniques = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        for technique in data.get("objects", []):
                            # 提取 tactic
                            kill_chain = technique.get("kill_chain_phases", [])
                            tactics = [kc.get("phase_name", "") for kc in kill_chain]
                            
                            intel = ThreatIntel(
                                id=technique.get("external_id", technique.get("name", "")),
                                source="mitre",
                                type="attack-pattern",
                                title=technique.get("name", ""),
                                description=technique.get("description", "")[:500],
                                severity="high",
                                published_at="",
                                attack_patterns=tactics,
                                raw=technique
                            )
                            techniques.append(intl)
                        
                        print(f"  ✅ 获取 {len(techniques)} 个 ATLAS 技术")
                    else:
                        print(f"  ⚠️ MITRE API 返回: {resp.status}")
        
        except Exception as e:
            print(f"  ❌ MITRE ATLAS 采集失败: {e}")
        
        return techniques
    
    def _extract_keywords(self, text: str) -> List[str]:
        """从文本提取关键词"""
        keywords = []
        
        # 攻击相关关键词
        attack_keywords = [
            "inject", "execute", "bypass", "overflow", "xss", "sql",
            "remote", "code", "privilege", "escalation", "upload",
            "deserialization", "path", "traversal", "csrf", "spoofing"
        ]
        
        text_lower = text.lower()
        for kw in attack_keywords:
            if kw in text_lower:
                keywords.append(kw)
        
        return keywords[:10]
    
    async def collect_all(self) -> List[ThreatIntel]:
        """采集所有来源的情报"""
        print("\n" + "="*50)
        print("🔍 开始威胁情报采集")
        print("="*50)
        
        # 并行采集
        tasks = [
            self.fetch_cve(days=30),
            self.fetch_github_advisory(ecosystem="pip"),
            self.fetch_mitre_atlas(),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合并结果
        all_intel = []
        for result in results:
            if isinstance(result, list):
                all_intel.extend(result)
        
        self.intel = all_intel
        
        # 保存
        self.save()
        
        print(f"\n📊 采集完成: {len(all_intel)} 条威胁情报")
        
        return all_intel
    
    def save(self):
        """保存到文件"""
        output_file = self.output_dir / f"intel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = [asdict(i) for i in self.intel]
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 已保存到: {output_file}")
    
    def get_summary(self) -> Dict:
        """获取情报摘要"""
        summary = {
            "total": len(self.intel),
            "by_source": {},
            "by_severity": {},
            "by_type": {}
        }
        
        for intel in self.intel:
            # 按来源
            source = intel.source
            summary["by_source"][source] = summary["by_source"].get(source, 0) + 1
            
            # 按严重程度
            severity = intel.severity
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
            
            # 按类型
            intel_type = intel.type
            summary["by_type"][intel_type] = summary["by_type"].get(intel_type, 0) + 1
        
        return summary


async def main():
    """主函数"""
    collector = IntelligenceCollector()
    
    # 采集所有情报
    intel_list = await collector.collect_all()
    
    # 输出摘要
    summary = collector.get_summary()
    print("\n📊 情报摘要:")
    print(f"  总数: {summary['total']}")
    print(f"  来源: {summary['by_source']}")
    print(f"  严重程度: {summary['by_severity']}")


if __name__ == "__main__":
    asyncio.run(main())
