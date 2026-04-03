#!/usr/bin/env python3
"""
整理样本目录 - 将样本按攻击类型分类
"""

import os
import json
from pathlib import Path
import shutil

def organize_samples(samples_dir: str):
    """整理样本目录"""
    samples_dir = Path(samples_dir)
    index_file = samples_dir / "samples_index.json"
    
    if not index_file.exists():
        print(f"❌ 索引文件不存在：{index_file}")
        return
    
    # 加载索引
    index = json.loads(index_file.read_text())
    samples = index.get("samples", [])
    
    print(f"📊 总样本数：{len(samples)}")
    
    # 创建攻击类型目录映射
    attack_type_dirs = {
        "tool_poisoning": "tool_poisoning",
        "remote_load": "remote_load",
        "data_exfil": "data_exfiltration",
        "prompt_injection": "prompt_injection",
        "resource_exhaustion": "resource_exhaustion",
        "memory_pollution": "memory_pollution",
        "supply_chain": "supply_chain",
        "credential_theft": "credential_theft",
        "persistence": "persistence",
        "evasion": "evasion",
    }
    
    # 统计
    stats = {}
    
    for sample in samples:
        sample_id = sample.get("id", "")
        attack_type = sample.get("attack_type", "unknown")
        dir_name = attack_type_dirs.get(attack_type, attack_type)
        
        # 创建目录
        target_dir = samples_dir / dir_name
        target_dir.mkdir(exist_ok=True)
        
        # 查找样本目录
        sample_dir = samples_dir / sample_id
        if sample_dir.exists():
            # 移动样本文件
            for f in sample_dir.iterdir():
                if f.is_file():
                    dest = target_dir / f.name
                    if not dest.exists():
                        shutil.move(str(f), str(dest))
            
            # 删除空目录
            try:
                sample_dir.rmdir()
            except:
                pass
        
        # 统计
        stats[attack_type] = stats.get(attack_type, 0) + 1
    
    # 删除旧的分类目录
    old_dirs = ["data_exfiltration", "memory_pollution", "prompt_injection", 
                "remote_load", "resource_exhaustion", "tool_poisoning"]
    for old_dir in old_dirs:
        old_path = samples_dir / old_dir
        if old_path.exists() and old_path.is_dir():
            # 保留旧样本
            pass
    
    print("\n✅ 样本整理完成！")
    print("\n📊 按攻击类型统计:")
    for at, count in sorted(stats.items()):
        print(f"   {at}: {count}")

if __name__ == "__main__":
    samples_dir = "/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/samples/malicious"
    organize_samples(samples_dir)
