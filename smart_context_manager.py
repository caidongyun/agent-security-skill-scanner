#!/usr/bin/env python3
"""
🧠 智能上下文管理器
- 大文件缓冲层
- 按需加载
- LLM 上下文精准优化
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

@dataclass
class CacheEntry:
    path: str
    hash: str
    size: int
    loaded_at: str
    last_accessed: str
    access_count: int

class ContextCache:
    """LRU 缓存管理器"""
    
    def __init__(self, max_size_mb: int = 50):
        self.max_size = max_size_mb * 1024 * 1024
        self.cache: Dict[str, CacheEntry] = {}
        self.current_size = 0
        self.cache_file = Path('/tmp/context_cache.json')
        self.load_cache()
    
    def load_cache(self):
        """从磁盘加载缓存索引"""
        if self.cache_file.exists():
            try:
                data = json.loads(self.cache_file.read_text())
                self.cache = {k: CacheEntry(**v) for k, v in data.items()}
            except:
                self.cache = {}
    
    def save_cache(self):
        """保存缓存索引"""
        data = {k: asdict(v) for k, v in self.cache.items()}
        self.cache_file.write_text(json.dumps(data, indent=2))
    
    def get(self, path: str) -> Optional[str]:
        """从缓存获取内容"""
        if path not in self.cache:
            return None
        
        entry = self.cache[path]
        p = Path(path)
        if not p.exists():
            self.remove(path)
            return None
        
        # 检查文件是否变化
        current_hash = self._hash_file(p)
        if current_hash != entry.hash:
            self.remove(path)
            return None
        
        # 更新访问信息
        entry.last_accessed = datetime.now().isoformat()
        entry.access_count += 1
        self.save_cache()
        
        # 从磁盘读取（缓存只存索引，内容从磁盘读）
        return p.read_text()
    
    def set(self, path: str, content: str):
        """添加到缓存"""
        p = Path(path)
        size = p.stat().st_size if p.exists() else len(content.encode())
        
        # 如果缓存已满，清理最不常用的
        while self.current_size + size > self.max_size and self.cache:
            self._evict_lru()
        
        # 计算哈希
        file_hash = hashlib.md5(content.encode()).hexdigest()
        
        # 创建缓存条目
        now = datetime.now().isoformat()
        self.cache[path] = CacheEntry(
            path=path,
            hash=file_hash,
            size=size,
            loaded_at=now,
            last_accessed=now,
            access_count=1
        )
        self.current_size += size
        self.save_cache()
    
    def remove(self, path: str):
        """从缓存移除"""
        if path in self.cache:
            self.current_size -= self.cache[path].size
            del self.cache[path]
            self.save_cache()
    
    def _evict_lru(self):
        """淘汰最少使用的条目"""
        if not self.cache:
            return
        
        # 找到最久未访问的
        lru_path = min(self.cache.keys(), 
                      key=lambda k: self.cache[k].last_accessed)
        self.remove(lru_path)
    
    def _hash_file(self, path: Path) -> str:
        """计算文件哈希"""
        return hashlib.md5(path.read_bytes()).hexdigest()
    
    def stats(self) -> Dict:
        """缓存统计"""
        return {
            'entries': len(self.cache),
            'size_mb': round(self.current_size / 1024 / 1024, 2),
            'max_size_mb': self.max_size // 1024 // 1024
        }

class SmartContextBuilder:
    """智能上下文构建器 - 为 LLM 提供精准上下文"""
    
    def __init__(self, cache: ContextCache):
        self.cache = cache
        self.context_items = []
        self.max_tokens = 4000  # LLM 上下文限制
    
    def add_file_summary(self, path: str, max_lines: int = 20):
        """添加文件摘要（而非全文）"""
        p = Path(path)
        if not p.exists():
            return
        
        content = self.cache.get(path) or p.read_text()
        lines = content.split('\n')
        
        # 只取关键部分
        summary = {
            'file': str(p),
            'lines': len(lines),
            'size_kb': round(len(content) / 1024, 1),
            'preview': '\n'.join(lines[:max_lines])
        }
        
        self.context_items.append(('summary', summary))
    
    def add_file_search(self, path: str, pattern: str, max_matches: int = 10):
        """搜索文件并添加匹配行"""
        p = Path(path)
        if not p.exists():
            return
        
        content = self.cache.get(path) or p.read_text()
        matches = []
        
        for i, line in enumerate(content.split('\n'), 1):
            if pattern.lower() in line.lower():
                matches.append(f"  Line {i}: {line.strip()}")
                if len(matches) >= max_matches:
                    break
        
        if matches:
            self.context_items.append(('search', {
                'file': str(p),
                'pattern': pattern,
                'matches': matches
            }))
    
    def add_metrics(self, metrics: Dict):
        """添加关键指标"""
        self.context_items.append(('metrics', {
            'detection_rate': metrics.get('detection_rate', 0),
            'false_positive': metrics.get('false_positive', 0),
            'f1_score': metrics.get('f1_score', 0),
            'total_rules': metrics.get('total_rules', 0)
        }))
    
    def add_weaknesses(self, weaknesses: List[Dict]):
        """添加短板分析（精准）"""
        # 只保留 top 3
        top_weaknesses = sorted(weaknesses, key=lambda x: x.get('current', 0))[:3]
        self.context_items.append(('weaknesses', top_weaknesses))
    
    def build(self, compress: bool = True) -> str:
        """构建最终上下文"""
        output = []
        
        for item_type, data in self.context_items:
            if item_type == 'summary':
                output.append(f"📄 File: {data['file']}")
                output.append(f"   Lines: {data['lines']}, Size: {data['size_kb']}KB")
                output.append(f"   Preview:\n{data['preview']}\n")
            
            elif item_type == 'search':
                output.append(f"🔍 Search '{data['pattern']}' in {data['file']}:")
                for match in data['matches']:
                    output.append(match)
                output.append("")
            
            elif item_type == 'metrics':
                output.append("📊 Current Metrics:")
                output.append(f"   Detection: {data['detection_rate']:.1f}%")
                output.append(f"   FP Rate: {data['false_positive']:.1f}%")
                output.append(f"   F1 Score: {data['f1_score']:.1f}")
                output.append("")
            
            elif item_type == 'weaknesses':
                output.append("⚠️  Weaknesses (Top 3):")
                for w in data:
                    output.append(f"   - {w.get('name', 'unknown')}: {w.get('current', 0):.1f}% (target: {w.get('target', 95)}%)")
                output.append("")
        
        result = '\n'.join(output)
        
        # 如果超过 token 限制，压缩
        if compress and len(result) > self.max_tokens * 4:  # ~4 chars per token
            result = self._compress(result)
        
        return result
    
    def _compress(self, text: str) -> str:
        """压缩上下文"""
        lines = text.split('\n')
        # 保留关键信息
        compressed = []
        for line in lines:
            if any(x in line for x in ['📊', '⚠️', '🔍', 'Detection', 'F1']):
                compressed.append(line)
            elif line.startswith('   - '):  # 弱点列表
                compressed.append(line)
        
        return '\n'.join(compressed) if compressed else text[:self.max_tokens * 4]

# === 使用示例 ===
if __name__ == '__main__':
    # 初始化缓存
    cache = ContextCache(max_size_mb=50)
    
    # 构建精准上下文
    builder = SmartContextBuilder(cache)
    
    # 添加规则文件摘要
    rules_dir = Path('/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/rules/scanner_v3/yara')
    for f in sorted(rules_dir.glob('*.yar'))[:3]:  # 只加载前 3 个
        builder.add_file_summary(str(f), max_lines=10)
    
    # 搜索关键模式
    builder.add_file_search(str(rules_dir / 'all_rules_v7.yar'), 'rule ', max_matches=5)
    
    # 添加指标
    builder.add_metrics({
        'detection_rate': 95.8,
        'false_positive': 0.0,
        'f1_score': 97.8,
        'total_rules': 257
    })
    
    # 添加短板
    builder.add_weaknesses([
        {'name': 'persistence', 'current': 90.0, 'target': 95},
        {'name': 'data_exfil', 'current': 90.0, 'target': 95}
    ])
    
    # 构建最终上下文
    context = builder.build()
    
    print("="*70)
    print("🧠 智能上下文 (LLM-Optimized)")
    print("="*70)
    print(context)
    print("="*70)
    print(f"\n缓存统计：{cache.stats()}")
    print(f"上下文长度：{len(context)} 字符 (~{len(context)//4} tokens)")
