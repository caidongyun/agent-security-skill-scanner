# 🧠 大文件缓冲层设计文档

## 问题现状

### 大文件列表
| 文件 | 大小 | 问题 |
|------|------|------|
| kb_index.json | 3.9MB | 全量加载慢 |
| knowledge_base.json | 3.8MB | 占用内存 |
| kb_index_shards.json | 3.2MB | 索引冗余 |
| all_rules_v*.yar | ~50KB each | 规则文件 |
| 各 shard 文件 | 400KB-1.4MB | 知识库分片 |

### LLM 上下文问题
- ❌ 加载无关文件内容
- ❌ 上下文超过 token 限制
- ❌ 关键信息被稀释
- ❌ 响应质量下降

---

## 解决方案

### 1. 缓冲层架构

```
应用层
   │
   ▼
┌─────────────────┐
│  ContextCache   │ ← LRU 缓存 (50MB)
│  (智能缓存层)    │
└─────────────────┘
   │
   ▼
┌─────────────────┐
│  SmartContext   │ ← 按需构建
│  Builder        │
└─────────────────┘
   │
   ▼
┌─────────────────┐
│  文件系统        │
│  (按需加载)     │
└─────────────────┘
```

### 2. 缓存策略

**LRU 淘汰**:
- 最大缓存：50MB
- 淘汰策略：最少使用 (LRU)
- 哈希校验：文件变化自动失效
- 持久化：索引保存到磁盘

**按需加载**:
- 文件摘要：只加载前 20 行
- 搜索匹配：只加载匹配行
- 分片加载：大文件分块读取
- 延迟加载：使用时才读取

### 3. LLM 上下文优化

**精准构建**:
```python
# ❌ 旧方式：加载整个文件
context = file.read_text()

# ✅ 新方式：只加载关键信息
builder.add_file_summary(file, max_lines=20)
builder.add_file_search(file, pattern='rule ', max_matches=10)
builder.add_metrics(metrics)
builder.add_weaknesses(top_3)
context = builder.build(compress=True)
```

**上下文组成**:
- 📄 文件摘要：~200 tokens
- 🔍 关键搜索：~100 tokens
- 📊 核心指标：~50 tokens
- ⚠️ Top3 短板：~100 tokens
- **总计**: ~450 tokens (远低于 4000 限制)

---

## 实施效果

### 性能提升

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 上下文加载 | 全量 (MB 级) | 精准 (KB 级) | 100x+ |
| LLM Token 使用 | 3000-4000 | 400-500 | 8x |
| 响应质量 | 信息稀释 | 聚焦关键 | 显著提升 |
| 内存占用 | 高 | 低 (缓存控制) | 显著降低 |

### 内存优化

**优化前**:
```
启动时加载:
- kb_index.json: 3.9MB
- knowledge_base.json: 3.8MB
- all_rules_v7.yar: 50KB
- 其他：~5MB
总计：~13MB 常驻内存
```

**优化后**:
```
缓存层管理:
- 最大缓存：50MB (可配置)
- 实际占用：按需 (通常<10MB)
- LRU 淘汰：自动清理
- 文件索引：<1KB
```

---

## 使用指南

### 自进化引擎集成

```python
# self_evolving_engine.py 已自动集成

from smart_context_manager import ContextCache, SmartContextBuilder

# 初始化缓存
cache = ContextCache(max_size_mb=50)

# 构建精准上下文
builder = SmartContextBuilder(cache)
builder.add_file_summary('rules/scanner_v3/yara/bash_rules.yar')
builder.add_metrics({'detection_rate': 95.8, ...})
builder.add_weaknesses([...])

# 获取优化后的上下文
context = builder.build(compress=True)
# ~500 tokens，包含所有关键信息
```

### 手动使用

```bash
# 查看缓存状态
python3 smart_context_manager.py

# 查看缓存统计
python3 -c "
from smart_context_manager import ContextCache
cache = ContextCache()
print(cache.stats())
"
```

---

## 最佳实践

### ✅ 推荐做法

1. **大文件使用摘要**
   ```python
   builder.add_file_summary(large_file, max_lines=20)
   ```

2. **搜索代替全量**
   ```python
   builder.add_file_search(file, pattern='rule ', max_matches=10)
   ```

3. **只保留 Top N**
   ```python
   builder.add_weaknesses(weaknesses[:3])  # 只保留前 3
   ```

4. **启用压缩**
   ```python
   context = builder.build(compress=True)
   ```

### ❌ 避免做法

1. **不要全量加载大文件**
   ```python
   # ❌ 错误
   context = Path('kb_index.json').read_text()
   
   # ✅ 正确
   builder.add_file_summary('kb_index.json', max_lines=20)
   ```

2. **不要包含所有指标**
   ```python
   # ❌ 错误
   builder.add_metrics(all_metrics)  # 50+ 个指标
   
   # ✅ 正确
   builder.add_metrics({
       'detection_rate': rate,
       'false_positive': fp,
       'f1_score': f1
   })  # 只保留核心 3 个
   ```

3. **不要加载无关文件**
   ```python
   # ❌ 错误
   for f in Path('.').glob('**/*'):
       builder.add_file_summary(str(f))
   
   # ✅ 正确
   for f in top_3_weaknesses:
       builder.add_file_summary(f)
   ```

---

## 监控与维护

### 缓存监控

```bash
# 查看缓存使用
python3 -c "
from smart_context_manager import ContextCache
cache = ContextCache()
stats = cache.stats()
print(f\"缓存条目：{stats['entries']}\")
print(f\"使用：{stats['size_mb']}/{stats['max_size_mb']} MB\")
"
```

### 性能日志

自进化引擎会自动记录：
- 上下文构建时间
- Token 使用量
- 缓存命中率

日志位置：`logs/evolution_*.log`

---

**版本**: v1.0  
**最后更新**: 2026-03-28 22:20  
**维护者**: 自进化系统
