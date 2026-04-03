# 🛡️ 分布式扫描架构 v4.1 - 设计文档

## 📋 架构概览

```
┌────────────────────────────────────────────────────────┐
│              分布式扫描架构 v4.1                        │
│  单机优化 · 原子写入 · 粗粒度分片 · 易扩展              │
└────────────────────────────────────────────────────────┘

┌─────────────────┐
│   Coordinator   │ ← 主协调器
│  (scanner.py)   │    - 样本收集
│                 │    - 任务分片
│                 │    - 结果汇总
└────────┬────────┘
         │
         │ 分发任务
         ↓
┌────────────────────────────────────────────────────────┐
│              ThreadPoolExecutor (并发池)                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ Worker 1 │ │ Worker 2 │ │ Worker 3 │ │ Worker N │  │
│  │          │ │          │ │          │ │          │  │
│  │ 扫描分片 │ │ 扫描分片 │ │ 扫描分片 │ │ 扫描分片 │  │
│  │ JSON 原子 │ │ JSON 原子 │ │ JSON 原子 │ │ JSON 原子 │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└────────────────────────────────────────────────────────┘
         │
         │ 结果汇总
         ↓
┌─────────────────┐
│  Final Report   │ ← 最终报告
│  (汇总所有      │    - 检测率/误报率
│   Worker 结果)   │    - 性能指标
└─────────────────┘
```

---

## 🎯 核心特性

### 1. JSON 原子写入 ✅

**问题**: 并发写入 JSON 文件不安全，可能导致数据损坏

**解决**: 
```python
def atomic_write_json(filepath, data):
    # 1. 写入临时文件
    fd, temp_path = tempfile.mkstemp()
    with os.fdopen(fd, 'w') as f:
        json.dump(data, f)
    
    # 2. 原子重命名
    Path(temp_path).rename(filepath)
```

**优势**:
- ✅ 写操作要么完全成功，要么完全失败
- ✅ 不会出现半写入状态
- ✅ 支持并发写入

---

### 2. 粗粒度分片 ✅

**问题**: 分片太细（5K）导致管理复杂，Worker 数量过多

**解决**: 每片 **10,000 样本**

**对比**:
| 分片大小 | 分片数 | 管理复杂度 | 推荐 |
|---------|--------|-----------|------|
| 5,000   | ~13 片 | 高 | ❌ |
| 10,000  | ~7 片  | 低 | ✅ |

---

### 3. Worker 完全独立 ✅

**设计理念**: 每个 Worker 独立运行，不依赖共享状态

```python
def worker_task(task_id, sample_paths, rules_dir, output_dir):
    # 1. 独立加载规则
    rules = load_rules(rules_dir)
    
    # 2. 独立扫描
    results = scan_batch(rules, detector, sample_paths)
    
    # 3. 独立统计
    stats = calculate_stats(results)
    
    # 4. 原子写入结果
    atomic_write_json(output_dir / f"{task_id}.json", {
        'task_id': task_id,
        'results': results,
        'stats': stats
    })
```

**优势**:
- ✅ 易于扩展到分布式（多机）
- ✅ 故障隔离（一个失败不影响其他）
- ✅ 易于调试（每个 Worker 有独立日志）

---

### 4. 易于横向扩展 ✅

**当前**: 单机多线程（ThreadPoolExecutor）

**未来扩展**:
```
单机 → 多机（Celery/Ray）
  ↓
本地文件 → 对象存储（S3/OSS）
  ↓
JSON 文件 → 数据库（PostgreSQL/MongoDB）
```

---

## 📊 性能基准

### 测试结果 (65,728 样本)

| 版本 | 样本数 | 检测率 | 误报率 | 速度 | 耗时 |
|------|--------|--------|--------|------|------|
| V3 Lite | 65,728 | 91.8% | 0.0% | 957/s | 68.7s |
| **V4.1** | 65,728 | **待测** | **待测** | **预计 1200+/s** | **预计 <55s** |

**性能提升来源**:
1. 减少分片开销（7 片 vs 13 片）
2. 优化并发调度
3. 原子写入避免锁竞争

---

## 🗂️ 文件结构

```
agent-security-skill-scanner-master/
├── scanner_distributed_v4_1.py    # 分布式扫描器
├── intent_detector_v2.py           # 意图识别器
├── benchmark/
│   └── v4_distributed/             # V4.1 输出目录
│       ├── tasks.json              # 任务列表
│       ├── workers/                # Worker 结果
│       │   ├── chunk_000.json
│       │   ├── chunk_001.json
│       │   └── ...
│       └── FINAL_REPORT_*.json     # 最终汇总报告
└── docs/
    └── DISTRIBUTED_ARCHITECTURE.md # 本文档
```

---

## 🔧 使用指南

### 本地并行扫描

```bash
cd agent-security-skill-scanner-master

# 基础用法
python3 scanner_distributed_v4_1.py

# 自定义并发度
python3 scanner_distributed_v4_1.py --workers 16

# 自定义分片大小
python3 scanner_distributed_v4_1.py --chunk-size 15000

# 自定义输出目录
python3 scanner_distributed_v4_1.py --output ./my_benchmark
```

### 输出说明

**tasks.json** - 任务列表:
```json
[
  {
    "task_id": "chunk_000",
    "samples": ["/path/to/sample1", "/path/to/sample2", ...]
  },
  ...
]
```

**workers/chunk_000.json** - Worker 结果:
```json
{
  "task_id": "chunk_000",
  "samples_scanned": 10000,
  "detection_rate": 92.5,
  "false_positive_rate": 0.0,
  "f1_score": 96.1,
  "scan_time_sec": 8.5,
  "speed": 1176,
  "results": [...]
}
```

**FINAL_REPORT_*.json** - 最终报告:
```json
{
  "total_samples": 65728,
  "detection_rate": 91.8,
  "false_positive_rate": 0.0,
  "f1_score": 95.7,
  "performance": {
    "total_time_sec": 55.2,
    "speed": 1190
  },
  "by_attack_type": {...}
}
```

---

## 🚀 未来扩展

### Phase 1: 多机分布式

```python
# 使用 Celery 分发任务
@app.task
def celery_worker_task(task_id, sample_paths):
    return worker_task(task_id, sample_paths)

# 多 Worker 节点
celery -A scanner worker --loglevel=info
```

### Phase 2: 结果存储

```python
# 使用 PostgreSQL 存储结果
import psycopg2

def save_to_db(results):
    conn = psycopg2.connect("dbname=scanner")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO scan_results ...")
    conn.commit()
```

### Phase 3: 实时监控

```python
# WebSocket 实时推送进度
@websocket.route('/progress')
def progress():
    while scanning:
        ws.send(json.dumps({
            'completed': completed,
            'total': total,
            'speed': speed
        }))
```

---

## 💡 最佳实践

1. **并发度选择**
   - 4 核 CPU: 8 线程
   - 8 核 CPU: 16 线程
   - 16 核 +: 32 线程

2. **分片大小**
   - 小样本 (<10K): 5,000/片
   - 中样本 (10K-100K): 10,000/片
   - 大样本 (>100K): 20,000/片

3. **结果清理**
   ```bash
   # 保留最近 10 次报告
   ls -t FINAL_REPORT_*.json | tail -n +11 | xargs rm
   ```

---

**版本**: v4.1  
**创建时间**: 2026-03-30  
**维护者**: Security Scanner Team
