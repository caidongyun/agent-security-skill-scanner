#!/usr/bin/env python3
"""
大文件预处理模块 - 分片、压缩、增量更新
"""

import json
import gzip
import hashlib
import shutil
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class LargeFileProcessor:
    """大文件处理器"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.backup_dir = self.base_dir / "file_backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    # ============ 分片管理 ============
    
    def shard_json_file(self, file_path: str, shard_key: str = "attack_type", 
                        max_shard_size: int = 100) -> Dict[str, str]:
        """
        将大 JSON 文件按指定键分片
        
        Args:
            file_path: 原文件路径
            shard_key: 分片键（如 attack_type, category）
            max_shard_size: 每个分片最大条目数
        
        Returns:
            分片文件路径映射
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # 按 shard_key 分组
        shards: Dict[str, List] = {}
        for item in data if isinstance(data, list) else data.values():
            if isinstance(item, dict):
                key = item.get(shard_key, "unknown")
                if key not in shards:
                    shards[key] = []
                shards[key].append(item)
        
        # 写入分片文件
        shard_paths = {}
        for key, items in shards.items():
            # 如果分片太大，继续拆分
            for i in range(0, len(items), max_shard_size):
                chunk = items[i:i + max_shard_size]
                shard_name = f"{key}_{i//max_shard_size}"
                shard_path = self.base_dir / f"shards/{shard_key}/{shard_name}.json"
                shard_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(shard_path, 'w') as f:
                    json.dump(chunk, f, ensure_ascii=False, indent=2)
                
                shard_paths[shard_name] = str(shard_path)
        
        # 保存分片索引
        index_path = self.base_dir / f"shards/{shard_key}_index.json"
        with open(index_path, 'w') as f:
            json.dump({
                "shard_key": shard_key,
                "created_at": datetime.now().isoformat(),
                "total_items": sum(len(items) for items in shards.values()),
                "shards": shard_paths
            }, f, ensure_ascii=False, indent=2)
        
        return shard_paths
    
    # ============ 压缩管理 ============
    
    def compress_file(self, file_path: str, keep_original: bool = False) -> str:
        """压缩 JSON 文件为 gzip"""
        src_path = Path(file_path)
        dst_path = src_path.with_suffix(src_path.suffix + '.gz')
        
        with open(src_path, 'rb') as f_in:
            with gzip.open(dst_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        if not keep_original:
            self.backup(src_path)
            src_path.unlink()
        
        return str(dst_path)
    
    def decompress_file(self, gz_path: str, keep_compressed: bool = False) -> str:
        """解压 gzip 文件"""
        src_path = Path(gz_path)
        dst_path = src_path.with_suffix('')
        
        with gzip.open(src_path, 'rb') as f_in:
            with open(dst_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        if not keep_compressed:
            src_path.unlink()
        
        return str(dst_path)
    
    # ============ 备份管理 ============
    
    def backup(self, file_path: str, max_backups: int = 5) -> str:
        """创建备份"""
        src_path = Path(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{src_path.stem}_{timestamp}{src_path.suffix}"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(src_path, backup_path)
        
        # 清理旧备份
        self._cleanup_backups(src_path.name, max_backups)
        
        return str(backup_path)
    
    def _cleanup_backups(self, original_name: str, max_backups: int):
        """清理旧备份"""
        backups = sorted(
            self.backup_dir.glob(f"{Path(original_name).stem}_*{Path(original_name).suffix}"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        for old_backup in backups[max_backups:]:
            old_backup.unlink()
    
    # ============ 增量更新 ============
    
    def incremental_update(self, file_path: str, new_items: List[Dict], 
                          key_field: str = "id") -> Tuple[int, int]:
        """
        增量更新 JSON 文件（避免全量重写）
        
        Returns:
            (新增数量，更新数量)
        """
        # 读取现有数据
        try:
            with open(file_path, 'r') as f:
                existing_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = {}
        
        # 构建索引
        if isinstance(existing_data, list):
            existing_map = {item.get(key_field, str(i)): item 
                          for i, item in enumerate(existing_data)}
        else:
            existing_map = existing_data
        
        added = 0
        updated = 0
        
        # 增量更新
        for item in new_items:
            key = item.get(key_field)
            if key in existing_map:
                existing_map[key].update(item)
                updated += 1
            else:
                existing_map[key] = item
                added += 1
        
        # 写回
        with open(file_path, 'w') as f:
            if isinstance(existing_data, list):
                json.dump(list(existing_map.values()), f, ensure_ascii=False, indent=2)
            else:
                json.dump(existing_map, f, ensure_ascii=False, indent=2)
        
        return added, updated
    
    # ============ 文件校验 ============
    
    def get_file_hash(self, file_path: str) -> str:
        """计算文件哈希（用于检测变更）"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def has_changed(self, file_path: str, last_hash: str) -> bool:
        """检查文件是否变更"""
        return self.get_file_hash(file_path) != last_hash
    
    # ============ 预处理流程 ============
    
    def preprocess(self, file_path: str, 
                   enable_sharding: bool = True,
                   enable_compression: bool = True,
                   enable_backup: bool = True) -> Dict[str, Any]:
        """
        完整预处理流程
        
        Returns:
            预处理报告
        """
        report = {
            "file": file_path,
            "timestamp": datetime.now().isoformat(),
            "steps": []
        }
        
        src_path = Path(file_path)
        original_size = src_path.stat().st_size
        report["original_size"] = original_size
        
        # Step 1: 备份
        if enable_backup and original_size > 1024 * 1024:  # >1MB
            backup_path = self.backup(file_path)
            report["steps"].append({
                "step": "backup",
                "result": backup_path,
                "status": "success"
            })
        
        # Step 2: 分片（如果是列表型 JSON）
        if enable_sharding and original_size > 5 * 1024 * 1024:  # >5MB
            try:
                with open(file_path, 'r') as f:
                    sample = json.load(f)
                
                if isinstance(sample, list) and len(sample) > 0 and isinstance(sample[0], dict):
                    # 自动检测分片键
                    shard_key = self._detect_shard_key(sample)
                    shard_paths = self.shard_json_file(file_path, shard_key)
                    report["steps"].append({
                        "step": "sharding",
                        "shard_key": shard_key,
                        "shard_count": len(shard_paths),
                        "status": "success"
                    })
            except Exception as e:
                report["steps"].append({
                    "step": "sharding",
                    "error": str(e),
                    "status": "skipped"
                })
        
        # Step 3: 压缩
        if enable_compression and original_size > 10 * 1024 * 1024:  # >10MB
            try:
                compressed_path = self.compress_file(file_path, keep_original=True)
                compression_ratio = original_size / Path(compressed_path).stat().st_size
                report["steps"].append({
                    "step": "compression",
                    "result": compressed_path,
                    "ratio": round(compression_ratio, 2),
                    "status": "success"
                })
            except Exception as e:
                report["steps"].append({
                    "step": "compression",
                    "error": str(e),
                    "status": "skipped"
                })
        
        return report
    
    def _detect_shard_key(self, sample_data: List[Dict]) -> str:
        """自动检测最佳分片键"""
        priority_keys = ["attack_type", "category", "type", "source", "severity"]
        
        for key in priority_keys:
            if key in sample_data[0]:
                return key
        
        # 返回第一个字符串类型的键
        for key, value in sample_data[0].items():
            if isinstance(value, str):
                return key
        
        return "unknown"


# ============ 使用示例 ============
if __name__ == "__main__":
    processor = LargeFileProcessor(".")
    
    # 预处理大文件
    report = processor.preprocess("kb_index.json")
    print(json.dumps(report, indent=2))
    
    # 增量更新
    added, updated = processor.incremental_update(
        "knowledge_base.json",
        [{"id": "new_001", "content": "新条目"}],
        key_field="id"
    )
    print(f"新增：{added}, 更新：{updated}")
