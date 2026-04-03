#!/usr/bin/env python3
"""
🧠 灵顺知识库 V3 - 内存缓存 + 按需加载
========================================
特性:
1. 启动时不加载数据，只加载索引
2. 按分类/轮次按需加载到内存
3. LRU 缓存管理内存使用
4. 版本结束时增量持久化
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import OrderedDict


class MemoryCache:
    """LRU 内存缓存"""
    
    def __init__(self, max_size: int = 1000):
        self.cache: OrderedDict = OrderedDict()
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def put(self, key: str, value: Any):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)
    
    def clear(self):
        self.cache.clear()
    
    def stats(self) -> Dict:
        total = self.hits + self.misses
        hit_rate = self.hits / total * 100 if total > 0 else 0
        return {
            "entries": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%"
        }


class LazyKnowledgeBase:
    """
    懒加载知识库 - 内存优化版
    
    使用方式:
        kb = LazyKnowledgeBase(base_dir)
        
        # 按需加载特定分类
        risks = kb.load_category("risks", round=7)
        
        # 查询数据
        for risk in risks:
            ...
        
        # 版本结束时保存增量
        kb.save_incremental(round=7)
    """
    
    def __init__(self, base_dir: Path, cache_size: int = 500):
        self.base_dir = Path(base_dir)
        self.index_file = self.base_dir / "kb_index.json"
        self.data_file = self.base_dir / "knowledge_base.json"
        self.cache = MemoryCache(cache_size)
        self.index: Dict = {}
        self.loaded_categories: set = set()
        self.dirty_data: Dict[str, List] = {}
        
        self._load_index()
    
    def _load_index(self):
        """加载索引 (轻量，<100KB)"""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                self.index = json.load(f)
        else:
            # 构建索引
            self._build_index()
    
    def _build_index(self):
        """从原始数据构建索引"""
        if not self.data_file.exists():
            return
        
        print("📇 构建索引...")
        start = time.time()
        
        with open(self.data_file, 'r') as f:
            data = json.load(f)
        
        self.index = {
            "categories": {},
            "rounds": {},
            "built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        for category, items in data.items():
            if isinstance(items, list):
                self.index["categories"][category] = {
                    "count": len(items),
                    "loaded": False
                }
                
                # 按 round 统计
                round_counts = {}
                for item in items:
                    r = item.get("round", 0)
                    round_counts[r] = round_counts.get(r, 0) + 1
                
                self.index["rounds"][category] = round_counts
        
        self._save_index()
        print(f"   索引构建完成 ({time.time()-start:.2f}s)")
    
    def _save_index(self):
        """保存索引"""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def load_category(self, category: str, round: Optional[int] = None) -> List:
        """
        按需加载分类数据
        
        Args:
            category: 分类名 (risks/patterns/lessons/fixes/test_cases)
            round: 可选，只加载特定轮次的数据
        
        Returns:
            数据列表
        """
        cache_key = f"{category}_r{round}" if round else category
        
        # 1. 查缓存
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        # 2. 加载数据
        if not self.data_file.exists():
            return []
        
        print(f"📥 加载 {category}" + (f" (round={round})" if round else ""))
        start = time.time()
        
        with open(self.data_file, 'r') as f:
            data = json.load(f)
        
        items = data.get(category, [])
        
        # 过滤轮次
        if round is not None:
            items = [i for i in items if i.get("round") == round]
        
        # 加入缓存
        self.cache.put(cache_key, items)
        self.loaded_categories.add(category)
        
        print(f"   加载 {len(items)} 条 ({time.time()-start:.2f}s)")
        return items
    
    def add_data(self, category: str, items: List, round: int):
        """
        添加新数据 (内存中，版本结束时持久化)
        
        Args:
            category: 分类名
            items: 数据列表
            round: 轮次
        """
        key = f"{category}_r{round}"
        self.dirty_data[key] = {
            "category": category,
            "round": round,
            "items": items
        }
        
        # 同时更新缓存
        cache_key = f"{category}_r{round}"
        existing = self.cache.get(cache_key) or []
        self.cache.put(cache_key, existing + items)
    
    def save_incremental(self, round: int):
        """
        增量保存 - 只写变更数据
        
        Args:
            round: 当前轮次
        """
        if not self.dirty_data:
            print("ℹ️  无变更数据，跳过保存")
            return
        
        print(f"💾 增量保存 round {round}...")
        
        # 按轮次分片存储
        round_dir = self.base_dir / "rounds" / f"round_{round:02d}"
        round_dir.mkdir(parents=True, exist_ok=True)
        
        saved_count = 0
        for key, data in self.dirty_data.items():
            if data["round"] != round:
                continue
            
            file = round_dir / f"{data['category']}.json"
            with open(file, 'w') as f:
                json.dump(data["items"], f, indent=2)
            
            saved_count += len(data["items"])
            print(f"   ✅ {data['category']}: {len(data['items'])} 条")
        
        self.dirty_data.clear()
        print(f"   总计保存 {saved_count} 条")
    
    def load_round(self, round: int) -> Dict[str, List]:
        """
        加载指定轮次的完整数据
        
        Returns:
            {category: items}
        """
        round_dir = self.base_dir / "rounds" / f"round_{round:02d}"
        
        if not round_dir.exists():
            return {}
        
        result = {}
        for file in round_dir.glob("*.json"):
            category = file.stem
            with open(file, 'r') as f:
                result[category] = json.load(f)
        
        return result
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "index": self.index.get("categories", {}),
            "cache": self.cache.stats(),
            "loaded_categories": list(self.loaded_categories),
            "dirty_entries": sum(len(d["items"]) for d in self.dirty_data.values())
        }
    
    def summary(self) -> str:
        """打印摘要"""
        lines = ["📊 知识库状态"]
        lines.append("=" * 50)
        
        for cat, info in self.index.get("categories", {}).items():
            status = "🟢" if cat in self.loaded_categories else "⚪"
            lines.append(f"{status} {cat}: {info['count']} 条")
        
        lines.append("")
        cache_stats = self.cache.stats()
        lines.append(f"💾 缓存：{cache_stats['entries']} 条目，命中率 {cache_stats['hit_rate']}")
        lines.append(f"📝 待保存：{cache_stats['entries']} 条")
        
        return "\n".join(lines)


# ==================== 使用示例 ====================

if __name__ == "__main__":
    base_dir = Path(__file__).parent
    
    print("=" * 60)
    print("🧠 灵顺知识库 V3 - 演示")
    print("=" * 60)
    
    # 初始化 (只加载索引)
    kb = LazyKnowledgeBase(base_dir)
    print("\n✅ 初始化完成 (仅加载索引)")
    
    # 按需加载
    print("\n--- 按需加载示例 ---")
    risks_r7 = kb.load_category("risks", round=7)
    fixes_r7 = kb.load_category("fixes", round=7)
    
    # 添加新数据
    print("\n--- 添加新数据 ---")
    kb.add_data("risks", [{"round": 8, "risk": "新风险", "severity": "HIGH"}], round=8)
    
    # 查看状态
    print("\n" + kb.summary())
    
    # 增量保存
    print("\n--- 增量保存 ---")
    kb.save_incremental(round=8)
    
    print("\n✅ 演示完成")
