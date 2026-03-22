#!/usr/bin/env python3
"""
样本探索发现系统
自动发现主流样本特征，持续研究改进
"""

import asyncio
import subprocess
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set

sys.path.insert(0, str(Path(__file__).parent.parent))

from expert_mode.risk_assessor import RiskRule


class SampleExplorer:
    """
    样本探索发现系统
    - 扫描真实样本
    - 提取特征
    - 发现新模式
    - 输出报告
    """
    
    def __init__(self, project_path: str = None):
        self.project_path = project_path or str(Path(__file__).parent.parent)
        self.discovered_patterns = {}  # 发现的模式
        self.feature_cache = set()     # 特征缓存
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "explored_dirs": [],
            "total_files": 0,
            "patterns_found": [],
            "new_discoveries": [],
            "recommendations": []
        }
        
    async def explore(self, scan_dirs: List[str] = None):
        """执行探索"""
        print("\n" + "="*60)
        print("🔍 样本探索发现")
        print("="*60)
        
        if scan_dirs is None:
            scan_dirs = [
                "samples/",                    # 本地样本
                str(Path.home() / ".openclaw/workspace/skills"),  # 技能
            ]
            
        # 1. 扫描目录
        print("\n📁 扫描目录...")
        for scan_dir in scan_dirs:
            await self._scan_directory(scan_dir)
            
        # 2. 提取特征
        print("\n🔎 提取特征...")
        features = self._extract_features()
        
        # 3. 发现新模式
        print("\n✨ 发现新模式...")
        new_patterns = self._discover_patterns(features)
        
        # 4. 生成报告
        print("\n📋 生成报告...")
        self._generate_report(features, new_patterns)
        
        # 5. 建议
        print("\n💡 改进建议...")
        recommendations = self._generate_recommendations(new_patterns)
        
        print(f"\n✅ 探索完成!")
        print(f"   扫描文件: {self.report['total_files']}")
        print(f"   发现模式: {len(self.report['patterns_found'])}")
        print(f"   新发现: {len(self.report['new_discoveries'])}")
        
        return self.report
        
    async def _scan_directory(self, scan_dir: str):
        """扫描目录"""
        path = Path(scan_dir)
        if not path.exists():
            print(f"   ⚠️ 目录不存在: {scan_dir}")
            return
            
        count = 0
        for ext in ['.py', '.js', '.sh', '.md']:
            for code_file in path.rglob(f'*{ext}'):
                # 跳过测试和隐藏
                if 'test' in code_file.name or code_file.name.startswith('.'):
                    continue
                    
                try:
                    content = code_file.read_text(errors='ignore')
                    if content:
                        # 提取特征
                        self._analyze_file(code_file, content)
                        count += 1
                except:
                    pass
                    
        self.report['explored_dirs'].append({
            "dir": scan_dir,
            "files": count
        })
        self.report['total_files'] += count
        print(f"   ✓ {scan_dir}: {count} 个文件")
        
    def _analyze_file(self, filepath: Path, content: str):
        """分析单个文件"""
        # 风险匹配
        findings = RiskRule.match(content)
        
        for finding in findings:
            pattern = finding.get("pattern", "")
            if pattern:
                if pattern not in self.discovered_patterns:
                    self.discovered_patterns[pattern] = []
                self.discovered_patterns[pattern].append({
                    "file": str(filepath),
                    "risk": finding.get("score", 0)
                })
                
        # 提取其他特征
        self._extract_additional_features(content)
        
    def _extract_features(self) -> Dict:
        """提取特征统计"""
        features = {
            "total_patterns": len(self.discovered_patterns),
            "by_risk": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
            "top_patterns": []
        }
        
        # 统计
        for pattern, occurrences in self.discovered_patterns.items():
            risk = sum(o.get("risk", 0) for o in occurrences)
            if risk >= 70:
                features["by_risk"]["HIGH"] += 1
            elif risk >= 40:
                features["by_risk"]["MEDIUM"] += 1
            else:
                features["by_risk"]["LOW"] += 1
                
        # 排序
        sorted_patterns = sorted(
            self.discovered_patterns.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:10]
        
        features["top_patterns"] = [
            {"pattern": p, "count": len(occ)} 
            for p, occ in sorted_patterns
        ]
        
        return features
        
    def _extract_additional_features(self, content: str):
        """提取额外特征"""
        # 编码特征
        if "base64" in content.lower():
            self.feature_cache.add("encoding:base64")
        if "zlib" in content.lower():
            self.feature_cache.add("encoding:zlib")
            
        # 网络特征
        if "http://" in content or "https://" in content:
            self.feature_cache.add("network:http")
        if "socket" in content.lower():
            self.feature_cache.add("network:socket")
            
        # 文件操作
        if ".write" in content or "open(" in content:
            self.feature_cache.add("file:write")
        if "os.system" in content or "subprocess" in content:
            self.feature_cache.add("exec:system")
            
    def _discover_patterns(self, features: Dict) -> List[Dict]:
        """发现新模式"""
        new_patterns = []
        
        # 检查现有规则
        existing = set()
        for rule_class in [RiskRule.TOOL_POISONING, RiskRule.REMOTE_LOAD, 
                          RiskRule.DATA_EXFIL, RiskRule.PROMPT_INJECTION,
                          RiskRule.RESOURCE_EXHAUSTION, RiskRule.MEMORY_POLLUTION]:
            existing.update(rule_class.keys())
            
        # 发现的新模式
        for pattern, occurrences in self.discovered_patterns.items():
            if pattern.lower() not in [p.lower() for p in existing]:
                # 新模式!
                new_patterns.append({
                    "pattern": pattern,
                    "occurrences": len(occurrences),
                    "files": [o["file"] for o in occurrences[:3]],
                    "suggested_risk": min(100, len(occurrences) * 10)
                })
                
        self.report["new_discoveries"] = new_patterns
        return new_patterns
        
    def _generate_report(self, features: Dict, new_patterns: List[Dict]):
        """生成报告"""
        self.report["patterns_found"] = features["top_patterns"]
        
        # 保存报告
        report_file = Path(self.project_path) / "reports" / "exploration_report.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
            
        print(f"   📄 报告: {report_file}")
        
    def _generate_recommendations(self, new_patterns: List[Dict]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if new_patterns:
            recommendations.append(
                f"发现 {len(new_patterns)} 个新模式，建议添加到检测规则"
            )
            
        # 基于特征的建议
        feature_list = list(self.feature_cache)
        if "network:http" in feature_list:
            recommendations.append("大量网络请求，建议增强网络行为监控")
        if "encoding:base64" in feature_list:
            recommendations.append("发现Base64编码，建议增加解码后检测")
        if "exec:system" in feature_list:
            recommendations.append("发现系统命令执行，建议加强权限检查")
            
        self.report["recommendations"] = recommendations
        
        for rec in recommendations:
            print(f"   💡 {rec}")
            
        return recommendations


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="样本探索发现系统")
    parser.add_argument("--dirs", nargs="+", default=None, help="扫描目录")
    parser.add_argument("--output", default="reports/exploration_report.md", help="报告输出")
    
    args = parser.parse_args()
    
    explorer = SampleExplorer()
    report = await explorer.explore(args.dirs)
    
    # 输出Markdown报告
    md_report = f"""# 样本探索发现报告

**时间**: {report['timestamp']}
**扫描文件**: {report['total_files']}
**发现模式**: {len(report['patterns_found'])}

## 扫描目录

"""
    for d in report['explored_dirs']:
        md_report += f"- {d['dir']}: {d['files']} 个文件\n"
        
    md_report += """
## 发现的高频模式

"""
    for p in report['patterns_found'][:10]:
        md_report += f"- `{p['pattern']}`: {p['count']} 次\n"
        
    if report['new_discoveries']:
        md_report += """
## 新发现模式

"""
        for p in report['new_discoveries']:
            md_report += f"- `{p['pattern']}`: 建议风险分 {p['suggested_risk']}\n"
            
    if report['recommendations']:
        md_report += """
## 改进建议

"""
        for r in report['recommendations']:
            md_report += f"- {r}\n"
            
    # 保存
    output_path = Path(args.output)
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_report)
        
    print(f"\n📄 Markdown报告: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
