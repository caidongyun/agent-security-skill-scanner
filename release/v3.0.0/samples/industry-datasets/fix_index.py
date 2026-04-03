#!/usr/bin/env python3
"""修复行业数据集索引"""

import json
from pathlib import Path
from datetime import datetime

def fix_index():
    base_dir = Path("/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/samples/industry-datasets")
    index_file = base_dir / "industry_samples_index.json"
    
    index = {
        "version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "sources": ["MITRE ATLAS", "OWASP LLM Top 10", "Industry False Positives"],
        "total_samples": 0,
        "samples": []
    }
    
    # 统计所有样本
    for attack_type_dir in base_dir.iterdir():
        if not attack_type_dir.is_dir():
            continue
        
        for sample_file in attack_type_dir.glob('*.txt'):
            # 判断来源
            if sample_file.name.startswith("MITRE-"):
                source = "MITRE ATLAS"
            elif sample_file.name.startswith("OWASP-"):
                source = "OWASP LLM Top 10"
            elif sample_file.name.startswith("FP-"):
                source = "False Positive"
            else:
                source = "Unknown"
            
            sample_info = {
                "file": sample_file.name,
                "attack_type": attack_type_dir.name,
                "source": source,
                "path": str(sample_file)
            }
            index["samples"].append(sample_info)
            index["total_samples"] += 1
    
    index_file.write_text(json.dumps(index, indent=2, ensure_ascii=False))
    
    print(f"✅ 索引已修复：{index_file}")
    print(f"📊 总样本数：{index['total_samples']}")
    
    # 按攻击类型统计
    from collections import Counter
    by_type = Counter(s['attack_type'] for s in index['samples'])
    print("\n按攻击类型分布:")
    for at, count in sorted(by_type.items()):
        print(f"  {at}: {count}")
    
    # 按来源统计
    by_source = Counter(s['source'] for s in index['samples'])
    print("\n按来源分布:")
    for src, count in sorted(by_source.items()):
        print(f"  {src}: {count}")
    
    return index

if __name__ == "__main__":
    fix_index()
