#!/usr/bin/env python3
"""
智能扫描 ClawHub Skills
- 扫描每个技能文件夹的关键文件
- 综合评估整个技能的风险
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.engines import Scanner

# 关键文件模式
KEY_FILE_PATTERNS = [
    'SKILL.md',
    '*.py', '*.js', '*.ts', '*.go', '*.sh', '*.bash',
    '*.yaml', '*.yml', '*.json',
    'Dockerfile', 'docker-compose.yml',
    'requirements.txt', 'package.json', 'go.mod',
]

def is_key_file(filename: str) -> bool:
    """判断是否是关键文件"""
    filename_lower = filename.lower()
    
    # 直接匹配
    if filename_lower in ['skill.md', 'dockerfile', 'requirements.txt', 'package.json', 'go.mod']:
        return True
    
    # 扩展名匹配
    key_extensions = ['.py', '.js', '.ts', '.go', '.sh', '.bash', '.yaml', '.yml', '.json']
    return any(filename_lower.endswith(ext) for ext in key_extensions)


def scan_skill_folder(skill_folder: Path, scanner: Scanner) -> dict:
    """扫描单个技能文件夹"""
    results = []
    total_score = 0
    max_score = 0
    file_count = 0
    
    # 找到所有关键文件
    key_files = []
    for pattern in ['*.md', '*.py', '*.js', '*.ts', '*.go', '*.sh', '*.yaml', '*.yml', '*.json']:
        key_files.extend(skill_folder.glob(pattern))
    
    # 扫描每个文件
    for file_path in key_files:
        if not file_path.is_file():
            continue
        
        try:
            result = scanner.scan_file(file_path)
            file_count += 1
            total_score += result.score
            max_score = max(max_score, result.score)
            
            if result.is_malicious or result.score >= 30:
                results.append({
                    'file': str(file_path.relative_to(skill_folder.parent.parent)),
                    'score': result.score,
                    'is_malicious': result.is_malicious,
                    'risk_level': result.risk_level,
                    'attack_types': result.attack_types
                })
        except Exception as e:
            pass
    
    # 综合评估整个技能
    avg_score = total_score / file_count if file_count > 0 else 0
    
    # 技能风险等级：取最高分 + 平均分加成
    final_score = min(max_score + int(avg_score * 0.3), 100)
    
    is_malicious = final_score >= 70 or max_score >= 90
    is_suspicious = 30 <= final_score < 70
    
    return {
        'skill_folder': str(skill_folder.name),
        'skill_path': str(skill_folder),
        'file_count': file_count,
        'final_score': final_score,
        'max_score': max_score,
        'avg_score': avg_score,
        'is_malicious': is_malicious,
        'is_suspicious': is_suspicious,
        'is_safe': not is_malicious and not is_suspicious,
        'risk_level': 'CRITICAL' if final_score >= 90 else 'HIGH' if final_score >= 70 else 'MEDIUM' if final_score >= 30 else 'SAFE',
        'flagged_files': results[:10]  # 最多 10 个风险文件
    }


def smart_scan(skills_dir: str, output_json: str, output_md: str, max_workers: int = 8):
    """智能扫描所有技能"""
    
    skills_path = Path(skills_dir)
    if not skills_path.exists():
        print(f"❌ 错误：目录不存在 - {skills_dir}")
        sys.exit(1)
    
    # 找到所有技能文件夹（一级子目录）
    skill_folders = [d for d in skills_path.iterdir() if d.is_dir()]
    total_skills = len(skill_folders)
    
    print(f"🔍 智能扫描 ClawHub Skills")
    print(f"📁 扫描目录：{skills_dir}")
    print(f"📦 技能数量：{total_skills:,}")
    print(f"👷 工作线程：{max_workers}")
    print()
    
    # 扫描结果
    results = []
    malicious = 0
    suspicious = 0
    safe = 0
    
    start_time = time.time()
    
    def scan_with_own_scanner(skill_folder):
        s = Scanner()
        return scan_skill_folder(skill_folder, s)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_folder = {executor.submit(scan_with_own_scanner, f): f for f in skill_folders}
        
        for i, future in enumerate(as_completed(future_to_folder), 1):
            skill_folder = future_to_folder[future]
            try:
                result = future.result()
                results.append(result)
                
                if result['is_malicious']:
                    malicious += 1
                elif result['is_suspicious']:
                    suspicious += 1
                else:
                    safe += 1
                
                # 进度显示
                if i % 5000 == 0 or i == total_skills:
                    elapsed = time.time() - start_time
                    speed = i / elapsed if elapsed > 0 else 0
                    print(f"  进度：{i:,}/{total_skills:,} ({i/total_skills*100:.1f}%) - 速度：{speed:.0f} skills/s")
                    print(f"    恶意：{malicious:,} ({malicious/i*100:.2f}%) | 可疑：{suspicious:,} ({suspicious/i*100:.2f}%) | 安全：{safe:,} ({safe/i*100:.2f}%)")
                    
            except Exception as e:
                print(f"⚠️ 扫描失败 {skill_folder}: {e}")
    
    elapsed_time = time.time() - start_time
    
    # 生成报告
    print()
    print("📊 生成报告...")
    
    report = {
        "report_metadata": {
            "scanner": f"agent-security-skill-scanner/v5.8.0 (Smart Scan)",
            "generated_at": datetime.now().isoformat(),
            "scan_path": str(skills_path),
            "total_skills": total_skills,
            "malicious_count": malicious,
            "suspicious_count": suspicious,
            "safe_count": safe,
            "elapsed_seconds": round(elapsed_time, 2),
            "speed": round(total_skills / elapsed_time, 1) if elapsed_time > 0 else 0
        },
        "results": [r for r in results if r['is_malicious'] or r['is_suspicious']]
    }
    
    # 保存 JSON
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON 报告：{output_json}")
    
    # 生成 Markdown 摘要
    md_content = generate_markdown_report(report)
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"✅ Markdown 报告：{output_md}")
    
    # 打印摘要
    print()
    print("=" * 80)
    print("📊 扫描摘要")
    print("=" * 80)
    print(f"总技能数：{total_skills:,}")
    print(f"🔴 恶意：{malicious:,} ({malicious/total_skills*100:.2f}%)")
    print(f"🟠 可疑：{suspicious:,} ({suspicious/total_skills*100:.2f}%)")
    print(f"🟢 安全：{safe:,} ({safe/total_skills*100:.2f}%)")
    print(f"耗时：{elapsed_time:.1f}秒 ({elapsed_time/60:.1f}分钟)")
    print(f"速度：{total_skills/elapsed_time:.0f} skills/s")
    print("=" * 80)
    
    return report


def generate_markdown_report(report: dict) -> str:
    """生成 Markdown 摘要报告"""
    meta = report["report_metadata"]
    results = report["results"]
    
    # 按风险排序
    sorted_results = sorted(results, key=lambda x: x['final_score'], reverse=True)
    
    md = f"""# ClawHub Skills 智能扫描报告

**扫描日期**: {meta['generated_at'][:10]}  
**Scanner 版本**: {meta['scanner']}  
**扫描目标**: {meta['scan_path']}

---

## 📊 扫描结果

| 风险等级 | 数量 | 占比 |
|---------|------|------|
| 🔴 恶意 | {meta['malicious_count']:,} | {meta['malicious_count']/meta['total_skills']*100:.2f}% |
| 🟠 可疑 | {meta['suspicious_count']:,} | {meta['suspicious_count']/meta['total_skills']*100:.2f}% |
| 🟢 安全 | {meta['safe_count']:,} | {meta['safe_count']/meta['total_skills']*100:.2f}% |
| **总计** | **{meta['total_skills']:,}** | **100%** |

---

## ⚡ 性能指标

| 指标 | 数值 |
|------|------|
| 总耗时 | {meta['elapsed_seconds']:.1f}秒 ({meta['elapsed_seconds']/60:.1f}分钟) |
| 扫描速度 | {meta['speed']:.0f} skills/s |
| 平均每个技能 | {meta['elapsed_seconds']/meta['total_skills']*1000:.0f}ms |

---

## 🔴 高风险技能 Top 20

**总数**: {len(sorted_results)} 个

"""
    
    for i, r in enumerate(sorted_results[:20], 1):
        md += f"{i}. **{r['skill_folder']}** (Score: {r['final_score']})\n"
        md += f"   - 路径：`{r['skill_path']}`\n"
        md += f"   - 文件数：{r['file_count']}\n"
        if r['flagged_files']:
            md += f"   - 风险文件:\n"
            for f in r['flagged_files'][:3]:
                md += f"     - `{Path(f['file']).name}` (score={f['score']}, {f['risk_level']})\n"
        md += "\n"
    
    md += f"""---

## 📁 报告文件

- **JSON 详细报告**: `{Path(report.get('output_json', 'report.json')).name}`
- **Markdown 摘要**: `{Path(report.get('output_md', 'report.md')).name}`

---

*本报告由 v5.8.0 smart_scan_clawhub.py 自动生成*
"""
    
    return md


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="智能扫描 ClawHub Skills")
    parser.add_argument('skills_dir', help='技能目录')
    parser.add_argument('--output', '-o', help='输出 JSON 文件')
    parser.add_argument('--output-md', '-m', help='输出 Markdown 文件')
    parser.add_argument('--workers', '-w', type=int, default=8, help='工作线程数')
    
    args = parser.parse_args()
    
    output_json = args.output or f"clawhub_smart_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_md = args.output_md or f"clawhub_smart_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    smart_scan(args.skills_dir, output_json, output_md, args.workers)
