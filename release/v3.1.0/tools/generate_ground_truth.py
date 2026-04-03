#!/usr/bin/env python3
"""生成 Ground Truth - 标记所有恶意样本"""

import json
from pathlib import Path
from datetime import datetime

def generate_ground_truth():
    base_dir = Path("/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/samples")
    
    ground_truth = {
        "version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "samples": []
    }
    
    # 方案 B - 所有样本都是恶意
    malicious_dir = base_dir / "malicious"
    for attack_type in ['tool_poisoning', 'remote_load', 'data_exfiltration', 'prompt_injection', 
                        'resource_exhaustion', 'memory_pollution', 'supply_chain', 
                        'credential_theft', 'persistence', 'evasion']:
        dir_path = malicious_dir / attack_type
        if not dir_path.exists():
            continue
        
        for i, sample_file in enumerate(dir_path.glob('*.txt'), 1):
            sample_id = sample_file.stem  # 使用文件名作为 sample_id
            ground_truth["samples"].append({
                "sample_id": sample_id,
                "file": str(sample_file),
                "label": "malicious",
                "attack_type": attack_type
            })
    
    # 方案 C - 行业数据集中的恶意样本（排除 FP）
    industry_dir = base_dir / "industry-datasets"
    for attack_type in ['tool_poisoning', 'evasion', 'resource_exhaustion', 
                        'data_exfiltration', 'remote_load', 'prompt_injection',
                        'credential_theft', 'persistence', 'supply_chain', 
                        'memory_pollution', 'data_exfil']:
        dir_path = industry_dir / attack_type
        if not dir_path.exists():
            continue
        
        for i, sample_file in enumerate(dir_path.glob('*.txt'), 1):
            # 排除误报样本
            if sample_file.name.startswith("FP-"):
                continue
            
            sample_id = sample_file.stem
            ground_truth["samples"].append({
                "sample_id": sample_id,
                "file": str(sample_file),
                "label": "malicious",
                "attack_type": attack_type,
                "source": "industry"
            })
    
    # 保存
    gt_file = base_dir / "ground_truth.json"
    gt_file.write_text(json.dumps(ground_truth, indent=2, ensure_ascii=False))
    
    print(f"✅ Ground Truth 已生成：{gt_file}")
    print(f"📊 总样本数：{len(ground_truth['samples'])}")
    
    # 统计
    from collections import Counter
    by_type = Counter(s['attack_type'] for s in ground_truth['samples'])
    print("\n按攻击类型分布:")
    for at, count in sorted(by_type.items()):
        print(f"  {at}: {count}")

if __name__ == "__main__":
    generate_ground_truth()
