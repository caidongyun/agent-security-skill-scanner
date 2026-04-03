#!/usr/bin/env python3
"""
整合方案 B+C 样本到 security-benchmark

目标：将 752 个样本整合到 /home/cdy/Desktop/security-benchmark/samples/
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

def integrate_samples():
    """整合样本"""
    print("=" * 60)
    print("🚀 整合方案 B+C 样本到 security-benchmark")
    print("=" * 60)
    print()
    
    # 源目录
    source_malicious = Path("/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/samples/malicious")
    source_industry = Path("/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/samples/industry-datasets")
    
    # 目标目录
    target_base = Path("/home/cdy/Desktop/security-benchmark/samples")
    target_malicious = target_base / "malicious-new"  # 新建目录避免覆盖
    target_industry = target_base / "industry-datasets"
    
    # 创建目标目录
    target_malicious.mkdir(parents=True, exist_ok=True)
    target_industry.mkdir(parents=True, exist_ok=True)
    
    stats = {
        "scheme_b": {"copied": 0, "by_type": {}},
        "scheme_c": {"copied": 0, "by_type": {}},
        "total": 0
    }
    
    # 1. 整合方案 B 样本
    print("📦 整合方案 B 样本...")
    malicious_dirs = [
        'tool_poisoning', 'remote_load', 'data_exfiltration',
        'prompt_injection', 'resource_exhaustion', 'memory_pollution',
        'supply_chain', 'credential_theft', 'persistence', 'evasion'
    ]
    
    for dir_name in malicious_dirs:
        source_dir = source_malicious / dir_name
        target_dir = target_malicious / dir_name
        
        if not source_dir.exists():
            continue
        
        target_dir.mkdir(exist_ok=True)
        count = 0
        
        for sample_file in source_dir.glob('*.txt'):
            dest = target_dir / sample_file.name
            if not dest.exists():
                shutil.copy2(sample_file, dest)
                count += 1
        
        stats["scheme_b"]["by_type"][dir_name] = count
        stats["scheme_b"]["copied"] += count
        print(f"   ✅ {dir_name}: {count} 个样本")
    
    # 2. 整合方案 C 样本
    print()
    print("📦 整合方案 C 行业数据集...")
    industry_dirs = [
        'tool_poisoning', 'evasion', 'resource_exhaustion',
        'data_exfiltration', 'remote_load', 'prompt_injection',
        'credential_theft', 'persistence', 'supply_chain',
        'memory_pollution', 'data_exfil'
    ]
    
    for dir_name in industry_dirs:
        source_dir = source_industry / dir_name
        target_dir = target_industry / dir_name
        
        if not source_dir.exists():
            continue
        
        target_dir.mkdir(exist_ok=True)
        count = 0
        
        for sample_file in source_dir.glob('*.txt'):
            dest = target_dir / sample_file.name
            if not dest.exists():
                shutil.copy2(sample_file, dest)
                count += 1
        
        if count > 0:
            stats["scheme_c"]["by_type"][dir_name] = count
            stats["scheme_c"]["copied"] += count
            print(f"   ✅ {dir_name}: {count} 个样本")
    
    # 3. 复制索引文件
    print()
    print("📦 复制索引文件...")
    
    if (source_malicious / "samples_index.json").exists():
        shutil.copy2(
            source_malicious / "samples_index.json",
            target_malicious / "samples_index.json"
        )
        print(f"   ✅ malicious/samples_index.json")
    
    if (source_industry / "industry_samples_index.json").exists():
        shutil.copy2(
            source_industry / "industry_samples_index.json",
            target_industry / "industry_samples_index.json"
        )
        print(f"   ✅ industry-datasets/industry_samples_index.json")
    
    # 4. 生成整合报告
    stats["total"] = stats["scheme_b"]["copied"] + stats["scheme_c"]["copied"]
    stats["timestamp"] = datetime.now().isoformat()
    stats["target_directory"] = str(target_base)
    
    report_file = target_base / "INTEGRATION_REPORT.json"
    report_file.write_text(json.dumps(stats, indent=2, ensure_ascii=False))
    
    # 5. 生成 Markdown 报告
    md_report = f"""# 样本整合报告

**日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**来源**: agent-security-skill-scanner-master (方案 B + C)
**目标**: /home/cdy/Desktop/security-benchmark/samples/

## 📊 整合统计

### 总体统计
| 指标 | 数量 |
|------|------|
| **总样本数** | {stats['total']} |
| **方案 B** | {stats['scheme_b']['copied']} |
| **方案 C** | {stats['scheme_c']['copied']} |

### 方案 B - 重新生成样本
| 攻击类型 | 样本数 |
|---------|--------|
"""
    
    for at, count in sorted(stats["scheme_b"]["by_type"].items()):
        md_report += f"| {at} | {count} |\n"
    
    md_report += f"""
### 方案 C - 行业数据集
| 攻击类型 | 样本数 |
|---------|--------|
"""
    
    for at, count in sorted(stats["scheme_c"]["by_type"].items()):
        md_report += f"| {at} | {count} |\n"
    
    md_report += f"""
## 📁 目录结构

```
samples/
├── malicious-new/          (方案 B: {stats['scheme_b']['copied']} 个样本)
│   ├── tool_poisoning/
│   ├── remote_load/
│   ├── data_exfiltration/
│   ├── prompt_injection/
│   ├── resource_exhaustion/
│   ├── memory_pollution/
│   ├── supply_chain/
│   ├── credential_theft/
│   ├── persistence/
│   └── evasion/
│
└── industry-datasets/      (方案 C: {stats['scheme_c']['copied']} 个样本)
    ├── tool_poisoning/
    ├── evasion/
    ├── resource_exhaustion/
    ├── data_exfiltration/
    ├── remote_load/
    ├── prompt_injection/
    ├── credential_theft/
    ├── persistence/
    ├── supply_chain/
    ├── memory_pollution/
    └── data_exfil/
```

## ✅ 整合完成

- 所有样本已复制到目标目录
- 索引文件已复制
- 报告已生成：`INTEGRATION_REPORT.json`

---
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    md_report_file = target_base / "INTEGRATION_REPORT.md"
    md_report_file.write_text(md_report)
    
    print()
    print("=" * 60)
    print("✅ 整合完成!")
    print("=" * 60)
    print(f"📊 总样本数：{stats['total']}")
    print(f"   - 方案 B: {stats['scheme_b']['copied']}")
    print(f"   - 方案 C: {stats['scheme_c']['copied']}")
    print(f"📁 目标目录：{target_base}")
    print(f"📄 报告：{report_file}")
    print(f"📄 Markdown 报告：{md_report_file}")
    
    return stats

if __name__ == "__main__":
    integrate_samples()
