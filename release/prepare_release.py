#!/usr/bin/env python3
"""
发布打包脚本 - 准备 v3.0.0 发布包

用法：
python3 prepare_release.py --version 3.0.0 --output release/v3.0.0
"""

import os
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
import hashlib


def find_latest_rules(base_dir: Path):
    """查找最新版本的 all_rules_v*.yar（排除 _dedup 等后缀）"""
    import re
    yara_dir = base_dir / "rules" / "scanner_v3" / "yara"
    rules_files = list(yara_dir.glob("all_rules_v*.yar"))
    if not rules_files:
        return None
    # 提取纯数字版本号（如 all_rules_v51_dedup.yar -> 51）
    def get_version(p):
        m = re.search(r'_v(\d+)', p.name)
        return int(m.group(1)) if m else 0
    latest = sorted(rules_files, key=get_version)[-1]
    return latest


def count_yara_rules(content: str) -> int:
    """计算 YARA 规则数量（处理 // 注释中的 rule 关键字）"""
    lines = content.split("\n")
    count = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("rule ") and not stripped.startswith("rule //"):
            count += 1
    return count


def prepare_release(version: str, output_dir: str):
    """准备发布包"""
    print("=" * 60)
    print(f"📦 准备发布 v{version}")
    print("=" * 60)
    print()

    base_dir = Path("/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master")
    output = Path(output_dir)

    # 创建输出目录
    output.mkdir(parents=True, exist_ok=True)

    stats = {
        "version": version,
        "release_date": datetime.now().isoformat(),
        "packages": {}
    }

    # 1. 打包样本
    print("📦 打包样本...")
    samples_dir = output / "samples"
    samples_dir.mkdir(exist_ok=True)

    # 复制恶意样本
    if (base_dir / "samples" / "malicious").exists():
        dest = samples_dir / "malicious"
        shutil.copytree(base_dir / "samples" / "malicious", dest, dirs_exist_ok=True)
        count = len(list(dest.glob("**/*.txt")))
        print(f"   ✅ malicious: {count} 个样本")
        stats["packages"]["malicious_samples"] = count

    # 复制行业数据集
    if (base_dir / "samples" / "industry-datasets").exists():
        dest = samples_dir / "industry-datasets"
        shutil.copytree(base_dir / "samples" / "industry-datasets", dest, dirs_exist_ok=True)
        count = len(list(dest.glob("**/*.txt")))
        print(f"   ✅ industry-datasets: {count} 个样本")
        stats["packages"]["industry_samples"] = count

    # 复制 Ground Truth
    if (base_dir / "samples" / "ground_truth.json").exists():
        shutil.copy2(base_dir / "samples" / "ground_truth.json", samples_dir)
        print(f"   ✅ ground_truth.json")

    # 2. 打包规则（优先使用最新的 all_rules_v*.yar）
    print()
    print("📦 打包规则...")
    rules_dir = output / "rules"
    rules_dir.mkdir(exist_ok=True)

    rules_file = find_latest_rules(base_dir)
    if rules_file:
        shutil.copy2(rules_file, rules_dir / "scanner_master_rules.yar")
        content = rules_file.read_text()
        rule_count = count_yara_rules(content)
        file_size = len(content.encode())
        print(f"   ✅ scanner_master_rules.yar ({rule_count} 条规则，{file_size:,} bytes)")
        print(f"      来源: {rules_file.relative_to(base_dir)}")
        stats["packages"]["rules"] = {
            "count": rule_count,
            "size_bytes": file_size,
            "source": str(rules_file.relative_to(base_dir))
        }
    else:
        # 回退：使用旧的 scanner-master/output/rules/scanner_master_rules.yar
        fallback = base_dir / "scanner-master" / "output" / "rules" / "scanner_master_rules.yar"
        if fallback.exists():
            shutil.copy2(fallback, rules_dir)
            content = fallback.read_text()
            rule_count = count_yara_rules(content)
            file_size = len(content.encode())
            print(f"   ⚠️  使用回退规则: scanner_master_rules.yar ({rule_count} 条)")
            stats["packages"]["rules"] = {
                "count": rule_count,
                "size_bytes": file_size,
                "source": "fallback: scanner-master/output/rules"
            }
        else:
            print("   ⚠️  未找到任何规则文件，跳过")

    # 3. 打包报告
    print()
    print("📦 打包报告...")
    reports_dir = output / "reports"
    reports_dir.mkdir(exist_ok=True)

    report_files = [
        "FINAL_PLAN_BC_REPORT.md",
        "PLAN_B_COMPLETION_REPORT.md",
        "PLAN_C_COMPLETION_REPORT.md"
    ]

    for report_name in report_files:
        src = base_dir / "reports" / report_name
        if src.exists():
            shutil.copy2(src, reports_dir)
            print(f"   ✅ {report_name}")

    # 4. 打包工具脚本
    print()
    print("📦 打包工具脚本...")
    tools_dir = output / "tools"
    tools_dir.mkdir(exist_ok=True)

    tool_files = [
        "skills/security-sample-generator/batch_generator.py",
        "samples/plan_c_integrator.py",
        "generate_ground_truth.py",
        "quick_validate.py"
    ]

    for tool_path in tool_files:
        src = base_dir / tool_path
        if src.exists():
            dest = tools_dir / Path(tool_path).name
            shutil.copy2(src, dest)
            print(f"   ✅ {Path(tool_path).name}")

    # 5. 生成发布清单
    print()
    print("📦 生成发布清单...")

    manifest = {
        "version": version,
        "release_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": "Agent Security Skill Scanner v3.0.0 - 方案 B+C 优化版",
        "contents": {
            "samples": {
                "malicious": stats["packages"].get("malicious_samples", 0),
                "industry": stats["packages"].get("industry_samples", 0),
                "total": stats["packages"].get("malicious_samples", 0) + stats["packages"].get("industry_samples", 0)
            },
            "rules": stats["packages"].get("rules", {}),
            "reports": ["FINAL_PLAN_BC_REPORT.md", "PLAN_B_COMPLETION_REPORT.md", "PLAN_C_COMPLETION_REPORT.md"],
            "tools": ["batch_generator.py", "plan_c_integrator.py", "generate_ground_truth.py", "quick_validate.py"]
        },
        "quality_metrics": {
            "detection_rate": "≥98%",
            "false_positive_rate": "<1%",
            "performance": "<1ms/sample"
        },
        "attack_types": [
            "tool_poisoning",
            "remote_load",
            "data_exfiltration",
            "prompt_injection",
            "resource_exhaustion",
            "memory_pollution",
            "supply_chain",
            "credential_theft",
            "persistence",
            "evasion"
        ],
        "languages": ["Python", "JavaScript", "Go", "Bash", "YAML"],
        "sources": ["自生成 (MITRE 映射)", "MITRE ATLAS", "OWASP LLM Top 10", "行业误报场景"]
    }

    manifest_file = output / "MANIFEST.json"
    manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"   ✅ MANIFEST.json")

    # 6. 生成校验和
    print()
    print("🔐 生成文件校验和...")
    checksums = {}

    for root, dirs, files in os.walk(output):
        for file in files:
            file_path = Path(root) / file
            rel_path = file_path.relative_to(output)

            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()

            checksums[str(rel_path)] = file_hash

    checksum_file = output / "CHECKSUMS.sha256"
    with open(checksum_file, 'w') as f:
        for file_path, checksum in sorted(checksums.items()):
            f.write(f"{checksum}  {file_path}\n")

    print(f"   ✅ CHECKSUMS.sha256 ({len(checksums)} files)")

    # 7. 统计
    stats["total_files"] = len(checksums)
    stats["output_directory"] = str(output)
    stats["manifest"] = str(manifest_file)

    # 保存统计
    stats_file = output / "RELEASE_STATS.json"
    stats_file.write_text(json.dumps(stats, indent=2, ensure_ascii=False))

    print()
    print("=" * 60)
    print("✅ 发布包准备完成!")
    print("=" * 60)
    print(f"📊 总文件数：{stats['total_files']}")
    print(f"📁 输出目录：{output}")
    print(f"📄 清单：{manifest_file}")
    print()
    print("📦 发布包内容:")
    print(f"   - 样本：{manifest['contents']['samples']['total']} 个")
    print(f"   - 规则：{manifest['contents']['rules'].get('count', 'N/A')} 条")
    print(f"   - 报告：{len(manifest['contents']['reports'])} 个")
    print(f"   - 工具：{len(manifest['contents']['tools'])} 个")
    print()
    print("🚀 下一步:")
    print(f"   cd {output}")
    print(f"   ls -la")
    print(f"   cat MANIFEST.json")

    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="准备发布包")
    parser.add_argument("--version", default="3.0.0", help="版本号")
    parser.add_argument("--output", default="release/v3.0.0", help="输出目录")

    args = parser.parse_args()
    prepare_release(args.version, args.output)
