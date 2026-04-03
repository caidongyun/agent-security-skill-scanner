# 🧠 上下文优化与知识管理最佳实践

## 一、问题诊断

### 1.1 常见症状
- 启动慢 (加载大文件)
- 内存占用高
- 上下文溢出
- 响应延迟

### 1.2 根因分析
| 根因 | 典型场景 | 影响 |
|------|----------|------|
| 全量加载 | `json.load(f)` 加载 3.7MB 文件 | 内存 + 时间 |
| 无增量更新 | 每次轮次重写整个知识库 | IO 阻塞 |
| 无缓存 | 重复查询每次读磁盘 | 性能差 |
| 无版本控制 | 无法回滚 | 风险高 |
| 无分层 | 所有数据混在一起 | 难管理 |

---

## 二、解决方案：五层架构

```
┌─────────────────────────────────────────────────────────┐
│  第5层: 归档层 (Archive)                                │
│  历史数据、冷数据 (>30天)                                │
├─────────────────────────────────────────────────────────┤
│  第4层: 版本层 (Version)                                │
│  快照、回滚点                                           │
├─────────────────────────────────────────────────────────┤
│  第3层: 增量层 (Delta)                                  │
│  变更记录 diff                                          │
├─────────────────────────────────────────────────────────┤
│  第2层: 缓存层 (Cache)                                  │
│  LRU 缓存、热数据                                       │
├─────────────────────────────────────────────────────────┤
│  第1层: 索引层 (Index)                                  │
│  元数据、指针 (常驻内存)                                 │
└─────────────────────────────────────────────────────────┘
```

---

## 三、核心实现：IncrementalKnowledgeBase

### 3.1 设计原则
1. **索引与数据分离** - 索引常驻内存
2. **按需加载 (Lazy Loading)** - 只加载需要的部分
3. **增量更新** - 只写变更部分
4. **LRU 缓存** - 热点数据缓存
5. **版本控制** - 支持回滚

### 3.2 目录结构
```
knowledge_base/
├── kb_index.json          # 索引 (几 KB)
├── kb_version.json        # 版本信息
├── kb_data/               # 数据分片
│   ├── shard_00.json      # 按哈希分片
│   ├── shard_01.json
│   └── ...
└── kb_archive/            # 历史归档
    └── v1_20260317.json
```

### 3.3 性能对比

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 启动加载 | 3.7MB | 几 KB | **99%↓** |
| 内存占用 | ~4MB | <100KB | **97%↓** |
| 加载时间 | ~2s | <50ms | **40x↑** |
| 单条查询 | 读整个文件 | 读单条 | **100x↑** |

---

## 四、代码示例

### 4.1 基础使用

```python
from knowledge_base_v2 import IncrementalKnowledgeBase, KBConfig

# 初始化
kb = IncrementalKnowledgeBase(KBConfig(base_dir=Path(".")))

# 插入数据
kb.put("rule_001", {"name": "规则1", "severity": "high"})
kb.put_batch({
    "rule_002": {...},
    "rule_003": {...}
})

# 查询数据 (按需加载)
rule = kb.get("rule_001")           # 单条
rules = kb.get_batch(["rule_001", "rule_002"])  # 批量

# 列出所有键
all_keys = kb.list_keys()           # 全部
rule_keys = kb.list_keys("rule_")   # 前缀过滤

# 统计
print(kb.stats())

# 保存
kb.save()

# 版本控制
version = kb.create_version("优化版本")
kb.rollback(version - 1)  # 回滚
```

### 4.2 集成到现有系统

```python
# 替换原来的 json.load()
class MySystem:
    def __init__(self):
        # 原来: self.knowledge = json.load(open("kb.json"))
        # 现在:
        self.kb = IncrementalKnowledgeBase(
            KBConfig(base_dir=Path("."), cache_size=1000)
        )
    
    def load(self):
        # 只加载索引
        stats = self.kb.stats()
        print(f"加载了 {stats['entries']} 条索引")
    
    def get_lesson(self, i):
        # 按需加载单条
        return self.kb.get(f"lesson_{i}")
    
    def save(self):
        # 增量保存
        self.kb.save()
```

---

## 五、其他优化技巧

### 5.1 日志轮转

```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    "app.log",
    maxBytes=10*1024*1024,  # 10MB
    backupCount=7            # 保留7天
)
```

### 5.2 大文件拆分

```python
# 原来: 1.9MB 的 resource_exhaustion.json
# 拆分为:
resource_exhaustion/
├── index.json              # 索引
├── cases/                  # 按类型分目录
│   ├── cpu_exhaustion.json
│   ├── memory_exhaustion.json
│   └── network_exhaustion.json
└── metadata.json           # 元数据
```

### 5.3 压缩归档

```python
import gzip
import shutil

def compress_old_data():
    with open('data.json', 'rb') as f_in:
        with gzip.open('data.json.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
```

---

## 六、灵顺系统集成

### 6.1 经验沉淀流程

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  每轮研发   │ → │  提取经验   │ → │  增量保存   │
└─────────────┘    └─────────────┘    └─────────────┘
                           ↓
                    ┌─────────────┐
                    │  更新索引   │
                    └─────────────┘
```

### 6.2 经验查询

```python
# 查询最近 N 条经验
recent_lessons = []
for i in range(100):
    lesson = kb.get(f"lesson_{i}")
    if lesson:
        recent_lessons.append(lesson)
```

---

## 七、清理清单

### 7.1 立即清理
```bash
# 删除空备份目录
rm -rf expert_mode/rules_backup/
rm -rf expert_mode/BACKUP_*/

# 压缩大文件
gzip expert_mode/tests/cases/resource_exhaustion.json
```

### 7.2 定期清理 (Cron)
```bash
# 每周清理日志
find . -name "*.log" -mtime +7 -delete

# 每月归档
tar -czvf archive_$(date +%Y%m).tar.gz data/
```

---

## 八、效果验证

```python
# 性能测试
import time

# 优化前
start = time.time()
data = json.load(open("kb.json"))  # 3.7MB
print(f"加载时间: {time.time()-start:.2f}s")
print(f"内存占用: {len(json.dumps(data))/1024/1024:.2f}MB")

# 优化后
kb = IncrementalKnowledgeBase(KBConfig(base_dir=Path(".")))
start = time.time()
stats = kb.stats()  # 只加载索引
print(f"加载时间: {time.time()-start:.4f}s")
print(f"内存占用: {stats['total_size_bytes']/1024:.2f}KB")
```

---

**总结**: 核心是 **索引与数据分离** + **按需加载** + **增量更新**，可将上下文占用降低 99%。
