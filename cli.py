#!/usr/bin/env python3
"""
Agent Security Skill Scanner CLI

Usage:
    python cli.py scan <skill_directory>
    python cli.py scan-all <skills_directory>
"""

import sys
import json
import logging
from pathlib import Path

from detectors.malware import MalwareDetector
from detectors.metadata import MetadataDetector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_skill_whitelist():
    """加载技能白名单"""
    import json
    from pathlib import Path
    
    whitelist_file = Path(__file__).parent / 'data' / 'whitelist' / 'false_positive_whitelist.json'
    if whitelist_file.exists():
        with open(whitelist_file) as f:
            data = json.load(f)
            return data.get('whitelist_skills', [])
    return []

def is_whitelisted_skill(skill_name: str) -> tuple:
    """检查技能是否在白名单中"""
    whitelist = load_skill_whitelist()
    for item in whitelist:
        if item['name'] == skill_name:
            return True, item.get('reason', '白名单')
    return False, None

def scan_skill(skill_path: str, output_format: str = 'text') -> dict:
    """扫描单个 Skill"""
    from pathlib import Path
    
    logger.info(f"Scanning skill: {skill_path}")
    
    # 检查是否在白名单
    skill_name = Path(skill_path).name
    whitelisted, reason = is_whitelisted_skill(skill_name)
    
    results = {
        'skill_path': skill_path,
        'skill_name': skill_name,
        'whitelisted': whitelisted,
        'whitelist_reason': reason,
        'metadata': None,
        'malware': None,
        'overall': None
    }
    
    # 如果在白名单，直接返回安全
    if whitelisted:
        results['overall'] = {
            'score': 0,
            'level': 'SAFE',
            'verdict': f'WHITELISTED: {reason}'
        }
        return results
    
    # 1. 元数据检查
    logger.info("Running metadata analysis...")
    metadata_detector = MetadataDetector()
    metadata_result = metadata_detector.scan_skill(skill_path)
    results['metadata'] = metadata_result
    
    # 2. 恶意代码检查
    logger.info("Running malware detection...")
    malware_detector = MalwareDetector()
    malware_findings = malware_detector.scan_directory(skill_path)
    results['malware'] = {
        'findings': malware_findings,
        'count': len(malware_findings)
    }
    
    # 3. 综合评分
    metadata_score = metadata_result.get('risk_score', 0)
    malware_score = min(len(malware_findings) * 10, 100)
    overall_score = max(metadata_score, malware_score)
    
    results['overall'] = {
        'score': overall_score,
        'level': get_risk_level(overall_score),
        'verdict': get_verdict(overall_score)
    }
    
    return results


def get_risk_level(score: int) -> str:
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


def get_verdict(score: int) -> str:
    """获取处置建议"""
    if score >= 60:
        return 'REJECT'
    elif score >= 40:
        return 'REVIEW'
    else:
        return 'ALLOW'


def print_report(results: dict, output_format: str = 'text'):
    """打印报告"""
    if output_format == 'json':
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return
    
    # 文本格式
    print("\n" + "=" * 70)
    print("Agent Security Skill Scanner - Report")
    print("=" * 70)
    print(f"\nSkill: {results['skill_path']}")
    print("-" * 70)
    
    # 元数据检查
    print("\n📋 Metadata Analysis:")
    metadata = results['metadata']
    if metadata and metadata.get('findings'):
        for finding in metadata['findings']:
            print(f"  [{finding['severity']}] {finding['type']}")
            print(f"    {finding['finding']}")
            print(f"    → {finding['recommendation']}")
    else:
        print("  ✅ No issues found")
    
    # 恶意代码检查
    print("\n🦠 Malware Detection:")
    malware = results['malware']
    if malware and malware['count'] > 0:
        print(f"  Found {malware['count']} potential issues:")
        for finding in malware['findings'][:10]:  # 只显示前 10 个
            print(f"  [{finding.get('severity', 'INFO')}] {finding.get('risk_type', 'UNKNOWN')}")
            print(f"    {finding.get('file', 'Unknown')}:{finding.get('line', '?')}")
    else:
        print("  ✅ No malicious code patterns found")
    
    # 综合评分
    print("\n" + "=" * 70)
    print("Overall Assessment:")
    print("=" * 70)
    overall = results['overall']
    print(f"  Risk Score: {overall['score']}/100")
    print(f"  Risk Level: {overall['level']}")
    print(f"  Verdict: {overall['verdict']}")
    print("=" * 70 + "\n")


def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("Usage: python cli.py scan <skill_directory>")
        print("       python cli.py scan-all <skills_directory>")
        sys.exit(1)
    
    command = sys.argv[1]
    target = sys.argv[2]
    
    if command == 'scan':
        # 扫描单个 Skill
        results = scan_skill(target)
        print_report(results)
    
    elif command == 'scan-all':
        # 批量扫描
        skills_dir = Path(target)
        skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir()]
        
        print(f"Scanning {len(skill_dirs)} skills...\n")
        
        all_results = []
        whitelisted_count = 0
        for skill_dir in skill_dirs:
            results = scan_skill(str(skill_dir))
            all_results.append(results)
            
            # 打印简要报告
            overall = results['overall']
            if results.get('whitelisted'):
                emoji = "✅"
                print(f"{emoji} {skill_dir.name}: 0/100 (WHITELISTED)")
                whitelisted_count += 1
            else:
                emoji = "🔴" if overall['score'] >= 60 else "🟡" if overall['score'] >= 40 else "🟢"
                print(f"{emoji} {skill_dir.name}: {overall['score']}/100 ({overall['level']})")
        
        # 汇总
        print("\n" + "=" * 70)
        print("Summary:")
        print("=" * 70)
        print(f"Total Skills: {len(all_results)}")
        print(f"Whitelisted: {whitelisted_count}")
        print(f"Critical: {sum(1 for r in all_results if not r.get('whitelisted') and r['overall']['score'] >= 80)}")
        print(f"High: {sum(1 for r in all_results if not r.get('whitelisted') and 60 <= r['overall']['score'] < 80)}")
        print(f"Medium: {sum(1 for r in all_results if not r.get('whitelisted') and 40 <= r['overall']['score'] < 60)}")
        print(f"Low/Safe: {sum(1 for r in all_results if not r.get('whitelisted') and r['overall']['score'] < 40)}")
        print("=" * 70 + "\n")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
