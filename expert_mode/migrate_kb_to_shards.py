#!/usr/bin/env python3
"""
📦 知识库迁移工具 - 按 Round 分片归档
======================================
功能:
1. 读取 knowledge_base.json
2. 按 round 分片存储
3. 验证迁移完整性
4. 压缩备份原文件

使用方式:
    python3 migrate_kb_to_shards.py
"""

import json
import gzip
import shutil
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def migrate_to_shards(base_dir: Path):
    """迁移知识库到分片格式"""
    
    kb_file = base_dir / "knowledge_base.json"
    
    if not kb_file.exists():
        print("❌ knowledge_base.json 不存在")
        return False
    
    # 加载数据
    print("📥 加载原始数据...")
    start = time.time()
    with open(kb_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    load_time = time.time() - start
    print(f"   加载完成 ({load_time:.2f}s, {kb_file.stat().st_size/1024/1024:.2f}MB)")
    
    # 分析 round 分布
    print("\n📊 分析 Round 分布...")
    rounds_data = defaultdict(lambda: defaultdict(list))
    
    categories = ['risks', 'patterns', 'lessons', 'fixes', 'test_cases', 'experiments']
    total_entries = 0
    
    for category in categories:
        items = data.get(category, [])
        if not isinstance(items, list):
            continue
        
        for item in items:
            r = item.get('round', 0)
            if r == 0:
                r = 1  # 默认归入 Round 1
            rounds_data[r][category].append(item)
            total_entries += 1
    
    round_list = sorted(rounds_data.keys())
    print(f"   发现 {len(round_list)} 个轮次：Round {min(round_list)} - {max(round_list)}")
    print(f"   总条目数：{total_entries:,}")
    
    # 创建分片目录
    print("\n📁 创建分片目录...")
    rounds_dir = base_dir / "rounds"
    rounds_dir.mkdir(exist_ok=True)
    
    # 按 round 保存
    print("\n💾 保存分片...")
    saved_entries = 0
    
    for round_num in round_list:
        round_dir = rounds_dir / f"round_{round_num:02d}"
        round_dir.mkdir(exist_ok=True)
        
        print(f"\n   Round {round_num}:")
        
        for category in categories:
            items = rounds_data[round_num].get(category, [])
            if not items:
                continue
            
            file = round_dir / f"{category}.json"
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
            
            size = file.stat().st_size
            print(f"      {category}: {len(items):,} 条 ({size/1024:.1f}KB)")
            saved_entries += len(items)
    
    print(f"\n✅ 迁移完成：{saved_entries:,} 条记录")
    
    # 生成索引
    print("\n📇 生成索引...")
    index = {
        "version": "3.0",
        "migrated_at": datetime.now().isoformat(),
        "rounds": {},
        "categories": {}
    }
    
    for round_num in round_list:
        round_dir = rounds_dir / f"round_{round_num:02d}"
        index["rounds"][f"round_{round_num:02d}"] = {
            "categories": list(rounds_data[round_num].keys()),
            "total_entries": sum(len(v) for v in rounds_data[round_num].values())
        }
    
    for category in categories:
        total = sum(len(rounds_data[r].get(category, [])) for r in round_list)
        index["categories"][category] = {
            "total": total,
            "rounds": {r: len(rounds_data[r].get(category, [])) for r in round_list if rounds_data[r].get(category)}
        }
    
    index_file = base_dir / "kb_index.json"
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    print(f"   索引已保存：{index_file.name}")
    
    # 压缩备份原文件
    print("\n🗜️ 压缩备份原文件...")
    archive_dir = base_dir / "kb_archive"
    archive_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_file = archive_dir / f"knowledge_base_v1_{timestamp}.json.gz"
    
    with open(kb_file, 'rb') as f_in:
        with gzip.open(archive_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    original_size = kb_file.stat().st_size
    compressed_size = archive_file.stat().st_size
    print(f"   原文件：{original_size/1024/1024:.2f}MB")
    print(f"   压缩后：{compressed_size/1024/1024:.2f}MB (压缩率 {compressed_size/original_size*100:.1f}%)")
    print(f"   归档：{archive_file.name}")
    
    # 验证
    print("\n✅ 验证迁移结果...")
    verified = 0
    for round_num in round_list:
        round_dir = rounds_dir / f"round_{round_num:02d}"
        for category in categories:
            file = round_dir / f"{category}.json"
            if file.exists():
                with open(file, 'r') as f:
                    items = json.load(f)
                verified += len(items)
    
    print(f"   验证通过：{verified:,} 条")
    if verified == total_entries:
        print("   ✅ 数据完整性验证通过!")
    else:
        print(f"   ⚠️  数据不匹配：期望 {total_entries:,} 条")
    
    return True


def create_kb_summary(base_dir: Path):
    """创建知识库摘要报告"""
    
    index_file = base_dir / "kb_index.json"
    if not index_file.exists():
        return
    
    with open(index_file, 'r') as f:
        index = json.load(f)
    
    report = []
    report.append("# 📊 知识库摘要报告")
    report.append("")
    report.append(f"**迁移时间**: {index['migrated_at']}")
    report.append(f"**版本**: {index['version']}")
    report.append("")
    report.append("## 分类统计")
    report.append("")
    report.append("| 分类 | 总数 | 轮次分布 |")
    report.append("|------|------|----------|")
    
    for cat, info in index['categories'].items():
        total = info['total']
        rounds = ', '.join(f"R{r}({c})" for r, c in sorted(info['rounds'].items()))
        report.append(f"| {cat} | {total:,} | {rounds} |")
    
    report.append("")
    report.append("## 轮次分布")
    report.append("")
    report.append("| 轮次 | 分类 | 条目数 |")
    report.append("|------|------|--------|")
    
    for round_name, info in sorted(index['rounds'].items()):
        round_num = round_name.replace('round_', '')
        total = info['total_entries']
        cats = ', '.join(info['categories'])
        report.append(f"| {round_num} | {cats} | {total:,} |")
    
    report_file = base_dir / "KB_SUMMARY.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"📝 摘要报告：{report_file.name}")


if __name__ == "__main__":
    print("=" * 70)
    print("📦 灵顺知识库 - 迁移到分片格式")
    print("=" * 70)
    
    base_dir = Path(__file__).parent
    
    # 执行迁移
    success = migrate_to_shards(base_dir)
    
    if success:
        # 生成摘要
        create_kb_summary(base_dir)
        
        print("\n" + "=" * 70)
        print("✨ 迁移完成!")
        print("=" * 70)
        print("\n下一步:")
        print("  1. 验证分片数据：python3 knowledge_base_v3.py")
        print("  2. 集成到灵顺 V5")
        print("  3. 启动自动循环")
        print("=" * 70)
