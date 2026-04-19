#!/usr/bin/env python3
"""
v5.8.0 全量扫描器 - 扫描 OpenClaw Skills

用法:
    python3 scan_all_skills.py /path/to/skills --output /path/to/report.json
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# 导入 v5.8.0 Scanner
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.engines import Scanner, ScanResult, SCANNER_NAME, VERSION


def scan_skills(skills_dir: str, output_json: str, output_md: str, max_workers: int = 8):
    """扫描所有技能目录"""
    
    skills_path = Path(skills_dir)
    if not skills_path.exists():
        print(f"❌ 错误：目录不存在 - {skills_dir}")
        sys.exit(1)
    
    # 找到所有 SKILL.md 文件
    print(f"🔍 正在扫描：{skills_dir}")
    skill_files = list(skills_path.rglob("SKILL.md"))
    total_skills = len(skill_files)
    
    print(f"📦 发现 {total_skills:,} 个技能")
    print(f"👷 使用 {max_workers} 个工作线程")
    print()
    
    # 扫描结果
    results = []
    malicious = 0
    suspicious = 0
    safe = 0
    
    start_time = time.time()
    last_progress = 0
    
    # 批量扫描 - 每个线程独立的 Scanner
    def scan_with_own_scanner(file_path):
        s = Scanner()
        return s.scan_file(file_path)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(scan_with_own_scanner, str(f)): f for f in skill_files}
        
        for i, future in enumerate(as_completed(future_to_file), 1):
            file_path = future_to_file[future]
            try:
                result = future.result()
                results.append(result)
                
                # 统计
                if result.is_malicious:
                    malicious += 1
                elif result.score >= 30:
                    suspicious += 1
                else:
                    safe += 1
                
                # 调试：打印前 10 个结果
                if i <= 10:
                    print(f"  [DEBUG] {i}: score={result.score}, malicious={result.is_malicious}, file={Path(file_path).parent.name}")
                
                # 进度显示
                if i % 1000 == 0 or i == total_skills:
                    elapsed = time.time() - start_time
                    speed = i / elapsed if elapsed > 0 else 0
                    print(f"  进度：{i:,}/{total_skills:,} ({i/total_skills*100:.1f}%) - 速度：{speed:.0f} skills/s")
                    
            except Exception as e:
                print(f"⚠️ 扫描失败 {file_path}: {e}")
    
    elapsed_time = time.time() - start_time
    
    # 生成报告
    print()
    print("📊 生成报告...")
    
    report = {
        "report_metadata": {
            "scanner": f"{SCANNER_NAME}/{VERSION}",
            "generated_at": datetime.now().isoformat(),
            "scan_path": str(skills_path),
            "total_skills": total_skills,
            "malicious_count": malicious,
            "suspicious_count": suspicious,
            "safe_count": safe,
            "elapsed_seconds": round(elapsed_time, 2),
            "speed": round(total_skills / elapsed_time, 1) if elapsed_time > 0 else 0
        },
        "results": [r.to_dict() for r in results if r.is_malicious or r.score >= 30]
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
    print(f"🟢 安全：{safe:,} ({safe/total_skills*100:.2f}%)")
    print(f"🟠 可疑：{suspicious:,} ({suspicious/total_skills*100:.2f}%)")
    print(f"🔴 恶意：{malicious} ({malicious/total_skills*100:.4f}%)")
    print(f"耗时：{elapsed_time:.1f} 秒")
    print(f"速度：{total_skills/elapsed_time:.1f} skills/s")
    print("=" * 80)


def generate_markdown_report(report: dict) -> str:
    """生成 Markdown 摘要报告"""
    meta = report["report_metadata"]
    results = report["results"]
    
    # 按风险评分排序
    sorted_results = sorted(results, key=lambda x: -x["score"])
    
    md = f"""# 🔍 OpenClaw Skills 全量安全扫描报告 (v5.8.0)

**生成时间**: {meta['generated_at']}  
**扫描器版本**: {meta['scanner']}  
**扫描路径**: {meta['scan_path']}  
**耗时**: {meta['elapsed_seconds']:.1f} 秒  
**速度**: {meta['speed']:.1f} skills/s

---

## 📊 扫描摘要

| 指标 | 数量 | 占比 |
|------|------|------|
| **总技能数** | {meta['total_skills']:,} | 100% |
| 🟢 安全 | {meta['safe_count']:,} | {meta['safe_count']/meta['total_skills']*100:.2f}% |
| 🟠 可疑 | {meta['suspicious_count']:,} | {meta['suspicious_count']/meta['total_skills']*100:.2f}% |
| 🔴 恶意 | {meta['malicious_count']} | {meta['malicious_count']/meta['total_skills']*100:.4f}% |

---

## 🔴 高风险技能详情

**总数**: {len(sorted_results)} 个

"""
    
    # 前 50 个高风险技能
    for i, result in enumerate(sorted_results[:50], 1):
        risk_level = "🔴" if result["score"] >= 70 else "🟠"
        attack_types = ", ".join(result["attack_types"]) if result["attack_types"] else "未知"
        
        md += f"""
### {i}. {Path(result['file_path']).parent.name}

- **路径**: `{result['file_path']}`
- **风险评分**: {risk_level} {result['score']}/100
- **攻击类型**: {attack_types}
- **匹配模式**: {len(result['matched_patterns'])} 个
- **匹配规则**: {len(result['matched_rules'])} 个

"""
    
    if len(sorted_results) > 50:
        md += f"\n*... 还有 {len(sorted_results) - 50} 个高风险技能，详见 JSON 报告*\n"
    
    md += f"""
---

## 📁 完整数据

- **JSON 详细报告**: 包含所有 {len(sorted_results)} 个高风险技能的完整信息
- **扫描器**: v5.8.0 (三层检测架构)

---

*报告生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    return md


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="v5.8.0 全量扫描器")
    parser.add_argument("skills_dir", help="技能目录路径")
    parser.add_argument("--output", "-o", default="scan_report.json", help="JSON 输出路径")
    parser.add_argument("--output-md", "-m", default="scan_report.md", help="Markdown 输出路径")
    parser.add_argument("--workers", "-w", type=int, default=8, help="工作线程数")
    
    args = parser.parse_args()
    
    scan_skills(args.skills_dir, args.output, args.output_md, args.workers)
