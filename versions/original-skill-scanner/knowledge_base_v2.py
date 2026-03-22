#!/usr/bin/env python3
"""
知识库增量更新系统 - 通用方案

核心思路:
1. 索引与数据分离 - 索引常驻内存，数据按需加载
2. 增量更新 - 只加载变更部分
3. 版本控制 - 支持回滚和 diff
4. 缓存层 - LRU 缓存热点数据

适用于: 规则库、知识库、配置库等大规模 JSON 数据
"""

import json
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import OrderedDict
from dataclasses import dataclass, field
import sqlite3

# ==================== 配置 ====================

@dataclass
class KBConfig:
    """知识库配置"""
    base_dir: Path
    index_file: str = "kb_index.json"      # 索引文件 (轻量)
    data_dir: str = "kb_data"              # 数据分片目录
    cache_size: int = 1000                 # LRU 缓存大小
    version_file: str = "kb_version.json"  # 版本信息
    archive_dir: str = "kb_archive"        # 归档目录


# ==================== 索引结构 ====================

@dataclass
class KBIndex:
    """
    索引结构 - 只保存元数据，不保存实际内容
    
    示例:
    {
        "version": 42,
        "updated_at": "2026-03-17T23:00:00Z",
        "entries": {
            "rule_001": {
                "hash": "abc123...",
                "size": 1024,
                "shard": "shard_00.json",
                "offset": 0,
                "updated_at": "2026-03-17T22:00:00Z"
            },
            "rule_002": {...}
        }
    }
    """
    version: int = 0
    updated_at: str = ""
    entries: Dict[str, Dict] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "updated_at": self.updated_at,
            "entries": self.entries
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'KBIndex':
        return cls(
            version=data.get("version", 0),
            updated_at=data.get("updated_at", ""),
            entries=data.get("entries", {})
        )


# ==================== LRU 缓存 ====================

class LRUCache:
    """LRU 缓存 - 缓存热点数据"""
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()
    
    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key: str, value: Any):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
    
    def clear(self):
        self.cache.clear()


# ==================== 知识库核心类 ====================

class IncrementalKnowledgeBase:
    """
    增量知识库 - 通用实现
    
    特性:
    - 索引与数据分离
    - 按需加载 (lazy loading)
    - LRU 缓存
    - 增量更新
    - 版本控制
    """
    
    def __init__(self, config: KBConfig):
        self.config = config
        self.base_dir = Path(config.base_dir)
        self.index_file = self.base_dir / config.index_file
        self.data_dir = self.base_dir / config.data_dir
        self.version_file = self.base_dir / config.version_file
        self.archive_dir = self.base_dir / config.archive_dir
        
        # 内存中的索引
        self.index: KBIndex = KBIndex()
        
        # LRU 缓存
        self.cache = LRUCache(config.cache_size)
        
        # 变更跟踪
        self.dirty_keys: set = set()
        
        # 初始化
        self._init_dirs()
        self._load_index()
    
    def _init_dirs(self):
        """初始化目录结构"""
        self.data_dir.mkdir(exist_ok=True)
        self.archive_dir.mkdir(exist_ok=True)
    
    def _load_index(self):
        """加载索引 (轻量操作)"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.index = KBIndex.from_dict(data)
        else:
            self.index = KBIndex()
    
    def _save_index(self):
        """保存索引"""
        self.index.updated_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index.to_dict(), f, indent=2, ensure_ascii=False)
    
    def _compute_hash(self, data: Any) -> str:
        """计算数据哈希"""
        content = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _get_shard_file(self, shard_name: str) -> Path:
        """获取分片文件路径"""
        return self.data_dir / shard_name
    
    def _load_shard(self, shard_name: str) -> Dict:
        """加载分片数据"""
        shard_file = self._get_shard_file(shard_name)
        if shard_file.exists():
            with open(shard_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_shard(self, shard_name: str, data: Dict):
        """保存分片数据"""
        shard_file = self._get_shard_file(shard_name)
        with open(shard_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # ==================== 公共 API ====================
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取单个条目 - 按需加载
        
        1. 先查缓存
        2. 缓存未命中则从磁盘加载
        3. 加入缓存
        """
        # 1. 查缓存
        cached = self.cache.get(key)
        if cached is not None:
            return cached
        
        # 2. 查索引
        if key not in self.index.entries:
            return None
        
        entry = self.index.entries[key]
        shard_name = entry["shard"]
        
        # 3. 加载分片
        shard_data = self._load_shard(shard_name)
        value = shard_data.get(key)
        
        # 4. 加入缓存
        if value is not None:
            self.cache.put(key, value)
        
        return value
    
    def get_batch(self, keys: List[str]) -> Dict[str, Any]:
        """批量获取 - 按分片批量加载"""
        result = {}
        missing_keys = []
        
        # 先从缓存获取
        for key in keys:
            cached = self.cache.get(key)
            if cached is not None:
                result[key] = cached
            else:
                missing_keys.append(key)
        
        # 按分片分组加载
        shards_to_load: Dict[str, List[str]] = {}
        for key in missing_keys:
            if key in self.index.entries:
                shard = self.index.entries[key]["shard"]
                shards_to_load.setdefault(shard, []).append(key)
        
        # 批量加载每个分片
        for shard_name, shard_keys in shards_to_load.items():
            shard_data = self._load_shard(shard_name)
            for key in shard_keys:
                value = shard_data.get(key)
                if value is not None:
                    result[key] = value
                    self.cache.put(key, value)
        
        return result
    
    def put(self, key: str, value: Any):
        """
        更新/插入单个条目 - 增量更新
        
        1. 计算哈希
        2. 如果哈希未变，跳过
        3. 否则更新分片
        4. 更新索引
        """
        new_hash = self._compute_hash(value)
        
        # 检查是否已存在且未变更
        if key in self.index.entries:
            old_hash = self.index.entries[key]["hash"]
            if old_hash == new_hash:
                return  # 无变更，跳过
        
        # 分配到分片 (简单哈希分片)
        shard_name = f"shard_{hash(key) % 10:02d}.json"
        
        # 加载分片
        shard_data = self._load_shard(shard_name)
        
        # 更新数据
        shard_data[key] = value
        self._save_shard(shard_name, shard_data)
        
        # 更新索引
        self.index.entries[key] = {
            "hash": new_hash,
            "size": len(json.dumps(value, ensure_ascii=False)),
            "shard": shard_name,
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        
        # 标记为脏数据
        self.dirty_keys.add(key)
    
    def put_batch(self, items: Dict[str, Any]):
        """批量更新"""
        for key, value in items.items():
            self.put(key, value)
    
    def delete(self, key: str):
        """删除条目"""
        if key not in self.index.entries:
            return
        
        entry = self.index.entries[key]
        shard_name = entry["shard"]
        
        # 从分片删除
        shard_data = self._load_shard(shard_name)
        if key in shard_data:
            del shard_data[key]
            self._save_shard(shard_name, shard_data)
        
        # 从索引删除
        del self.index.entries[key]
        self.dirty_keys.add(key)
    
    def save(self):
        """保存索引 (调用 save() 才持久化索引)"""
        self._save_index()
        self.dirty_keys.clear()
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """列出所有键 (支持前缀过滤)"""
        if prefix:
            return [k for k in self.index.entries.keys() if k.startswith(prefix)]
        return list(self.index.entries.keys())
    
    def count(self) -> int:
        """返回条目数"""
        return len(self.index.entries)
    
    def stats(self) -> dict:
        """返回统计信息"""
        total_size = sum(
            e.get("size", 0) for e in self.index.entries.values()
        )
        return {
            "entries": len(self.index.entries),
            "version": self.index.version,
            "updated_at": self.index.updated_at,
            "total_size_bytes": total_size,
            "cache_size": len(self.cache.cache),
            "dirty_keys": len(self.dirty_keys)
        }
    
    # ==================== 版本控制 ====================
    
    def create_version(self, message: str = "") -> int:
        """创建版本快照"""
        self.save()
        
        version_num = self.index.version + 1
        timestamp = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
        
        # 归档当前索引
        archive_file = self.archive_dir / f"index_v{version_num}_{timestamp}.json"
        with open(archive_file, 'w', encoding='utf-8') as f:
            json.dump(self.index.to_dict(), f, indent=2, ensure_ascii=False)
        
        # 更新版本号
        self.index.version = version_num
        self._save_index()
        
        # 保存版本信息
        version_info = {
            "version": version_num,
            "timestamp": timestamp,
            "message": message,
            "entries": len(self.index.entries)
        }
        
        with open(self.version_file, 'w', encoding='utf-8') as f:
            json.dump(version_info, f, indent=2, ensure_ascii=False)
        
        return version_num
    
    def rollback(self, version: int) -> bool:
        """回滚到指定版本"""
        # 查找归档文件
        archive_files = list(self.archive_dir.glob(f"index_v{version}_*.json"))
        if not archive_files:
            return False
        
        # 恢复索引
        with open(archive_files[0], 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.index = KBIndex.from_dict(data)
        
        self._save_index()
        self.cache.clear()
        
        return True


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 示例用法
    config = KBConfig(base_dir=Path("."))
    kb = IncrementalKnowledgeBase(config)
    
    # 插入数据
    kb.put("rule_001", {"name": "规则 1", "severity": "high"})
    kb.put("rule_002", {"name": "规则 2", "severity": "medium"})
    
    # 获取数据 (按需加载)
    rule = kb.get("rule_001")
    print(f"获取规则：{rule}")
    
    # 批量获取
    rules = kb.get_batch(["rule_001", "rule_002"])
    print(f"批量获取：{rules}")
    
    # 统计
    print(f"统计：{kb.stats()}")
    
    # 保存
    kb.save()
    
    # 创建版本
    version = kb.create_version("初始版本")
    print(f"创建版本：{version}")
