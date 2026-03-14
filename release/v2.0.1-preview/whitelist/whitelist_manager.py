#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
白名单管理器 - 本地加白方案
支持文件、模式、哈希、规则四种白名单类型
"""

import os
import sys
import json
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum


class WhitelistType(Enum):
    """白名单类型"""
    FILE = "file"
    PATTERN = "pattern"
    HASH = "hash"
    RULE = "rule"


@dataclass
class WhitelistEntry:
    """白名单条目"""
    id: str
    type: str
    value: str
    reason: str
    added_by: str
    added_at: str
    expires_at: Optional[str] = None
    scope: Optional[List[str]] = None
    enabled: bool = True
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WhitelistEntry':
        return cls(**data)
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if not self.expires_at:
            return False
        
        expiry = datetime.fromisoformat(self.expires_at)
        return datetime.now() > expiry


class WhitelistManager:
    """白名单管理器"""
    
    def __init__(self, whitelist_file: Optional[str] = None):
        if whitelist_file:
            self.whitelist_file = Path(whitelist_file)
        else:
            # 默认路径
            self.whitelist_file = Path(
                "/home/cdy/.openclaw/workspace/skills/agent-security-skill-scanner/data/whitelist/local.json"
            )
        
        self.whitelist_file.parent.mkdir(parents=True, exist_ok=True)
        self.entries: Dict[str, WhitelistEntry] = {}
        self.load()
    
    def load(self):
        """加载白名单"""
        if self.whitelist_file.exists():
            with open(self.whitelist_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for entry_data in data.get('rules', []):
                entry = WhitelistEntry.from_dict(entry_data)
                if not entry.is_expired() and entry.enabled:
                    self.entries[entry.id] = entry
            
            print(f"[OK] 已加载 {len(self.entries)} 条白名单规则")
        else:
            print(f"[INFO] 白名单文件不存在，创建新的：{self.whitelist_file}")
            self.save()
    
    def save(self):
        """保存白名单"""
        data = {
            'version': '1.0.0',
            'updated_at': datetime.now().isoformat(),
            'rules': [entry.to_dict() for entry in self.entries.values()]
        }
        
        with open(self.whitelist_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"[OK] 已保存 {len(self.entries)} 条白名单规则")
    
    def generate_id(self) -> str:
        """生成唯一 ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        import random
        return f"wl-{timestamp}-{random.randint(1000, 9999)}"
    
    def add_file_whitelist(self, file_path: str, reason: str, 
                           added_by: str = "admin",
                           expires_days: Optional[int] = None) -> WhitelistEntry:
        """添加文件白名单"""
        entry = WhitelistEntry(
            id=self.generate_id(),
            type=WhitelistType.FILE.value,
            value=file_path,
            reason=reason,
            added_by=added_by,
            added_at=datetime.now().isoformat(),
            expires_at=(datetime.now() + timedelta(days=expires_days)).isoformat() if expires_days else None
        )
        
        self.entries[entry.id] = entry
        self.save()
        
        print(f"[OK] 已添加文件白名单：{file_path}")
        return entry
    
    def add_pattern_whitelist(self, pattern: str, reason: str,
                              scope: Optional[List[str]] = None,
                              added_by: str = "admin",
                              expires_days: Optional[int] = None) -> WhitelistEntry:
        """添加模式白名单（正则）"""
        # 验证正则
        try:
            re.compile(pattern)
        except re.error as e:
            raise ValueError(f"无效的正则表达式：{e}")
        
        entry = WhitelistEntry(
            id=self.generate_id(),
            type=WhitelistType.PATTERN.value,
            value=pattern,
            reason=reason,
            added_by=added_by,
            added_at=datetime.now().isoformat(),
            scope=scope,
            expires_at=(datetime.now() + timedelta(days=expires_days)).isoformat() if expires_days else None
        )
        
        self.entries[entry.id] = entry
        self.save()
        
        print(f"[OK] 已添加模式白名单：{pattern}")
        return entry
    
    def add_hash_whitelist(self, file_path: str, reason: str,
                          added_by: str = "admin",
                          expires_days: Optional[int] = None) -> WhitelistEntry:
        """添加哈希白名单（自动计算 SHA256）"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在：{file_path}")
        
        hash_value = self.compute_file_hash(file_path)
        
        entry = WhitelistEntry(
            id=self.generate_id(),
            type=WhitelistType.HASH.value,
            value=hash_value,
            reason=reason,
            added_by=added_by,
            added_at=datetime.now().isoformat(),
            expires_at=(datetime.now() + timedelta(days=expires_days)).isoformat() if expires_days else None
        )
        
        self.entries[entry.id] = entry
        self.save()
        
        print(f"[OK] 已添加哈希白名单：{hash_value[:16]}...")
        return entry
    
    def add_rule_whitelist(self, rule_id: str, scope: List[str], reason: str,
                          added_by: str = "admin",
                          expires_days: Optional[int] = None) -> WhitelistEntry:
        """添加规则白名单"""
        entry = WhitelistEntry(
            id=self.generate_id(),
            type=WhitelistType.RULE.value,
            value=rule_id,
            reason=reason,
            added_by=added_by,
            added_at=datetime.now().isoformat(),
            scope=scope,
            expires_at=(datetime.now() + timedelta(days=expires_days)).isoformat() if expires_days else None
        )
        
        self.entries[entry.id] = entry
        self.save()
        
        print(f"[OK] 已添加规则白名单：{rule_id}")
        return entry
    
    def compute_file_hash(self, file_path: str) -> str:
        """计算文件 SHA256 哈希"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def remove(self, entry_id: str) -> bool:
        """删除白名单条目"""
        if entry_id in self.entries:
            del self.entries[entry_id]
            self.save()
            print(f"[OK] 已删除白名单：{entry_id}")
            return True
        
        print(f"[WARN] 未找到白名单：{entry_id}")
        return False
    
    def disable(self, entry_id: str) -> bool:
        """禁用白名单条目"""
        if entry_id in self.entries:
            self.entries[entry_id].enabled = False
            self.save()
            print(f"[OK] 已禁用白名单：{entry_id}")
            return True
        
        print(f"[WARN] 未找到白名单：{entry_id}")
        return False
    
    def enable(self, entry_id: str) -> bool:
        """启用白名单条目"""
        if entry_id in self.entries:
            self.entries[entry_id].enabled = True
            self.save()
            print(f"[OK] 已启用白名单：{entry_id}")
            return True
        
        print(f"[WARN] 未找到白名单：{entry_id}")
        return False
    
    def list_entries(self, entry_type: Optional[str] = None) -> List[WhitelistEntry]:
        """列出白名单条目"""
        entries = list(self.entries.values())
        
        if entry_type:
            entries = [e for e in entries if e.type == entry_type]
        
        return entries
    
    def check_file(self, file_path: str) -> Optional[WhitelistEntry]:
        """检查文件是否在白名单中"""
        # 1. 检查文件路径匹配
        for entry in self.entries.values():
            if entry.type == WhitelistType.FILE.value:
                if self._match_path(file_path, entry.value):
                    return entry
        
        # 2. 检查哈希匹配
        if os.path.exists(file_path):
            file_hash = self.compute_file_hash(file_path)
            for entry in self.entries.values():
                if entry.type == WhitelistType.HASH.value:
                    if entry.value == file_hash:
                        return entry
        
        return None
    
    def check_pattern(self, code_line: str, file_path: Optional[str] = None) -> Optional[WhitelistEntry]:
        """检查代码模式是否匹配白名单"""
        for entry in self.entries.values():
            if entry.type == WhitelistType.PATTERN.value:
                # 检查作用域
                if entry.scope and file_path:
                    if not any(self._match_path(file_path, s) for s in entry.scope):
                        continue
                
                # 匹配正则
                if re.search(entry.value, code_line):
                    return entry
        
        return None
    
    def check_rule(self, rule_id: str, file_path: Optional[str] = None) -> Optional[WhitelistEntry]:
        """检查规则是否被白名单覆盖"""
        for entry in self.entries.values():
            if entry.type == WhitelistType.RULE.value:
                if entry.value != rule_id:
                    continue
                
                # 检查作用域
                if entry.scope and file_path:
                    if any(self._match_path(file_path, s) for s in entry.scope):
                        return entry
                elif not entry.scope:
                    return entry
        
        return None
    
    def _match_path(self, file_path: str, pattern: str) -> bool:
        """匹配文件路径（支持通配符）"""
        import fnmatch
        return fnmatch.fnmatch(file_path, pattern)
    
    def export(self, output_file: str):
        """导出白名单"""
        data = {
            'version': '1.0.0',
            'exported_at': datetime.now().isoformat(),
            'rules': [entry.to_dict() for entry in self.entries.values()]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"[OK] 已导出白名单到：{output_file}")
    
    def import_from_file(self, input_file: str, merge: bool = True):
        """从文件导入白名单"""
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        imported = 0
        for entry_data in data.get('rules', []):
            entry = WhitelistEntry.from_dict(entry_data)
            
            # 生成新 ID 避免冲突
            entry.id = self.generate_id()
            
            if merge or entry.id not in self.entries:
                self.entries[entry.id] = entry
                imported += 1
        
        self.save()
        print(f"[OK] 已导入 {imported} 条白名单规则")
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        stats = {
            'total': len(self.entries),
            'by_type': {},
            'expiring_soon': 0,
            'expired': 0
        }
        
        now = datetime.now()
        
        for entry in self.entries.values():
            # 按类型统计
            stats['by_type'][entry.type] = stats['by_type'].get(entry.type, 0) + 1
            
            # 检查过期
            if entry.is_expired():
                stats['expired'] += 1
            elif entry.expires_at:
                expiry = datetime.fromisoformat(entry.expires_at)
                if (expiry - now).days <= 7:
                    stats['expiring_soon'] += 1
        
        return stats


def main():
    """CLI 入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='白名单管理器')
    parser.add_argument('--file', '-f', type=str, help='白名单文件路径')
    parser.add_argument('--action', '-a', type=str, 
                       choices=['add', 'remove', 'list', 'check', 'export', 'import', 'stats'],
                       help='操作类型')
    parser.add_argument('--type', '-t', type=str,
                       choices=['file', 'pattern', 'hash', 'rule'],
                       help='白名单类型')
    parser.add_argument('--value', '-v', type=str, help='白名单值')
    parser.add_argument('--reason', '-r', type=str, help='添加原因')
    parser.add_argument('--scope', '-s', type=str, nargs='*', help='作用域')
    parser.add_argument('--expires', '-e', type=int, help='过期天数')
    parser.add_argument('--output', '-o', type=str, help='输出文件')
    parser.add_argument('--input', '-i', type=str, help='输入文件')
    
    args = parser.parse_args()
    
    manager = WhitelistManager(args.file)
    
    if args.action == 'add':
        if args.type == 'file':
            manager.add_file_whitelist(args.value, args.reason, expires_days=args.expires)
        elif args.type == 'pattern':
            manager.add_pattern_whitelist(args.value, args.reason, scope=args.scope, expires_days=args.expires)
        elif args.type == 'hash':
            manager.add_hash_whitelist(args.value, args.reason, expires_days=args.expires)
        elif args.type == 'rule':
            manager.add_rule_whitelist(args.value, args.scope or [], args.reason, expires_days=args.expires)
    
    elif args.action == 'remove':
        manager.remove(args.value)
    
    elif args.action == 'list':
        entries = manager.list_entries(args.type)
        for entry in entries:
            status = "⚠️ 即将过期" if not entry.is_expired() and entry.expires_at else "✅"
            print(f"{entry.id} [{entry.type}] {entry.value} - {entry.reason} {status}")
    
    elif args.action == 'check':
        if args.type == 'file':
            result = manager.check_file(args.value)
        elif args.type == 'pattern':
            result = manager.check_pattern(args.value)
        elif args.type == 'rule':
            result = manager.check_rule(args.value)
        else:
            print("[ERROR] 指定 --type (file/pattern/rule)")
            sys.exit(1)
        
        if result:
            print(f"[MATCH] 匹配白名单：{result.id} - {result.reason}")
        else:
            print(f"[NO_MATCH] 未匹配白名单")
    
    elif args.action == 'export':
        manager.export(args.output)
    
    elif args.action == 'import':
        manager.import_from_file(args.input)
    
    elif args.action == 'stats':
        stats = manager.get_statistics()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
