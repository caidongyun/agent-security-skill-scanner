#!/usr/bin/env python3
"""
智能分片脚本 - 支持嵌套 JSON 结构
"""

import json
import os
from pathlib import Path
from datetime import datetime

def shard_kb_index(base_dir: str):
    """为 kb_index.json 创建智能分片"""
    
    kb_path = Path(base_dir) / "kb_index.json"
    if not kb_path.exists():
        print(f"文件不存在：{kb_path}")
        return
    
    with open(kb_path, 'r') as f:
        data = json.load(f)
    
    shards_dir = Path(base_dir) / "shards"
    shards_dir.mkdir(exist_ok=True)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "shards_created": []
    }
    
    # 策略 1: 按 categories 分片
    if 'categories' in data and isinstance(data['categories'], dict):
        cat_dir = shards_dir / "categories"
        cat_dir.mkdir(exist_ok=True)
        
        for category, items in data['categories'].items():
            if isinstance(items, list) and len(items) > 0:
                shard_path = cat_dir / f"{category}.json"
                with open(shard_path, 'w') as f:
                    json.dump(items, f, ensure_ascii=False, indent=2)
                
                report["shards_created"].append({
                    "type": "category",
                    "name": category,
                    "items": len(items),
                    "path": str(shard_path)
                })
                print(f"✅ 分类分片：{category} ({len(items)} 条)")
    
    # 策略 2: 按 rounds 分片（如果存在）
    if 'rounds' in data and isinstance(data['rounds'], dict):
        round_dir = shards_dir / "rounds"
        round_dir.mkdir(exist_ok=True)
        
        for round_name, round_data in data['rounds'].items():
            shard_path = round_dir / f"{round_name}.json"
            with open(shard_path, 'w') as f:
                json.dump(round_data, f, ensure_ascii=False, indent=2)
            
            report["shards_created"].append({
                "type": "round",
                "name": round_name,
                "path": str(shard_path)
            })
            print(f"✅ 轮次分片：{round_name}")
    
    # 保存分片索引
    index_path = shards_dir / "kb_index_shards.json"
    with open(index_path, 'w') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 分片索引：{index_path}")
    print(f"📈 总分片数：{len(report['shards_created'])}")
    
    return report


def shard_knowledge_base(base_dir: str):
    """为 knowledge_base.json 创建智能分片"""
    
    kb_path = Path(base_dir) / "knowledge_base.json"
    if not kb_path.exists():
        print(f"文件不存在：{kb_path}")
        return
    
    with open(kb_path, 'r') as f:
        data = json.load(f)
    
    shards_dir = Path(base_dir) / "shards" / "knowledge_base"
    shards_dir.mkdir(parents=True, exist_ok=True)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "shards_created": []
    }
    
    # 如果是字典，按顶层键分片
    if isinstance(data, dict):
        for key, value in data.items():
            shard_path = shards_dir / f"{key}.json"
            with open(shard_path, 'w') as f:
                json.dump({key: value}, f, ensure_ascii=False, indent=2)
            
            size = len(value) if isinstance(value, (list, dict)) else 1
            report["shards_created"].append({
                "key": key,
                "size": size,
                "path": str(shard_path)
            })
            print(f"✅ 知识库分片：{key} ({size} 项)")
    
    # 如果是列表，按 attack_type 分片
    elif isinstance(data, list):
        by_attack = {}
        for item in data:
            if isinstance(item, dict):
                attack_type = item.get('attack_type', 'unknown')
                if attack_type not in by_attack:
                    by_attack[attack_type] = []
                by_attack[attack_type].append(item)
        
        for attack_type, items in by_attack.items():
            shard_path = shards_dir / f"{attack_type}.json"
            with open(shard_path, 'w') as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
            
            report["shards_created"].append({
                "attack_type": attack_type,
                "items": len(items),
                "path": str(shard_path)
            })
            print(f"✅ 攻击类型分片：{attack_type} ({len(items)} 条)")
    
    # 保存索引
    index_path = shards_dir / "index.json"
    with open(index_path, 'w') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 分片索引：{index_path}")
    print(f"📈 总分片数：{len(report['shards_created'])}")
    
    return report


if __name__ == "__main__":
    import sys
    base_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    print("=== 智能分片处理 ===\n")
    
    print("1️⃣ 处理 kb_index.json...")
    shard_kb_index(base_dir)
    
    print("\n2️⃣ 处理 knowledge_base.json...")
    shard_knowledge_base(base_dir)
    
    print("\n✅ 分片完成!")
