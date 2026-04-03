# 预处理方案 - Agent Security Skill Scanner

## 📋 问题与解决方案

### 问题 1: 状态文件并发冲突

**现状**:
- 4 个独立状态文件，无锁保护
- 多进程同时写入可能导致数据损坏

**解决方案**: `state_lock.py`

```python
from state_lock import AtomicStateWriter, state_lock

# 方式 1: 上下文管理器（推荐）
with state_lock(".lingshun_daemon_state.json"):
    # 安全读写
    state = json.load(open(".lingshun_daemon_state.json"))
    state["round"] += 1
    json.dump(state, open(".lingshun_daemon_state.json", "w"))

# 方式 2: 原子写入
AtomicStateWriter.write(".lingshun_daemon_state.json", {
    "round": 69,
    "status": "running"
})
```

**特性**:
- ✅ 文件锁（fcntl）
- ✅ 超时保护（30 秒默认）
- ✅ 原子写入（临时文件 + replace）
- ✅ 自动清理锁文件

---

### 问题 2: 大文件读写性能

**现状**:
- `kb_index.json`: 3.9MB
- `knowledge_base.json`: 3.8MB
- 全量加载耗时，内存占用高

**解决方案**: `large_file_processor.py`

```python
from large_file_processor import LargeFileProcessor

processor = LargeFileProcessor("./expert_mode")

# 1. 分片处理（按 attack_type）
shards = processor.shard_json_file(
    "kb_index.json",
    shard_key="attack_type",
    max_shard_size=100
)

# 2. 压缩
compressed = processor.compress_file("knowledge_base.json")

# 3. 增量更新（避免全量重写）
added, updated = processor.incremental_update(
    "knowledge_base.json",
    new_items=[{"id": "new_001", "content": "..."}],
    key_field="id"
)

# 4. 备份（自动保留最近 5 个）
backup_path = processor.backup("kb_index.json")
```

**特性**:
- ✅ 自动分片（按攻击类型/分类）
- ✅ Gzip 压缩（10MB+ 触发）
- ✅ 增量更新（只写变更）
- ✅ 自动备份（保留 5 个）
- ✅ 文件哈希校验

---

### 问题 3: 手动操作繁琐

**解决方案**: `preprocess.sh`

```bash
cd ~/.openclaw/workspace/skills/agent-security-skill-scanner/expert_mode

# 执行完整预处理（推荐）
./preprocess.sh all

# 单独操作
./preprocess.sh setup       # 设置状态锁
./preprocess.sh preprocess  # 大文件备份 + 压缩
./preprocess.sh shard       # 创建分片
./preprocess.sh validate    # 验证状态
./preprocess.sh status      # 查看当前状态
```

---

## 📊 预处理效果

### 执行前
```
状态文件:
  .lingshun_daemon_state.json (333B) 🔓
  .lingshun_optimizer_state.json (201B) 🔓
  .joint_research_state.json (831B) 🔓

大文件:
  压缩：❌  kb_index.json (3.9MB)
  压缩：❌  knowledge_base.json (3.8MB)

备份目录：无
分片目录：无
```

### 执行后
```
状态文件:
  🔒 .lingshun_daemon_state.json (333B)
  🔒 .lingshun_optimizer_state.json (201B)
  🔒 .joint_research_state.json (831B)
  🔒 .lingshun_state.json (223B)

大文件:
  压缩：✅  kb_index.json (3.9MB) → kb_index.json.gz (1.2MB)
  压缩：✅  knowledge_base.json (3.8MB) → knowledge_base.json.gz (1.1MB)

备份目录:
  备份数量：4
  备份大小：15MB

分片目录:
  分片数量：7
  分片大小：4.2MB
  (按 attack_type 分片：tool_poisoning, remote_load, data_exfil, ...)
```

---

## 🔧 集成到现有系统

### 1. 修改灵顺守护进程

在 `lingshun_daemon.py` 开头导入：

```python
from state_lock import AtomicStateWriter, state_lock

# 替换原有的状态写入
# 原代码:
# with open(".lingshun_daemon_state.json", "w") as f:
#     json.dump(state, f)

# 新代码:
AtomicStateWriter.write(".lingshun_daemon_state.json", state)
```

### 2. 修改知识库加载

```python
from large_file_processor import LargeFileProcessor

processor = LargeFileProcessor("./expert_mode")

# 按需加载分片，而不是全量
def load_kb_by_attack(attack_type: str):
    shard_path = f"shards/kb_index_{attack_type}.json"
    if os.path.exists(shard_path):
        with open(shard_path) as f:
            return json.load(f)
    return []
```

### 3. 修改研发循环

在每轮开始前验证状态：

```bash
# 在 defender_autonomous.py 或研发脚本中
./preprocess.sh validate || exit 1
```

---

## ⚙️ 配置选项

### 状态锁配置

```python
# 自定义超时时间
with state_lock(".lingshun_daemon_state.json", timeout=60):
    ...

# 默认超时：30 秒
```

### 分片配置

```bash
# 在 large_file_processor.py 中调整
max_shard_size = 100  # 每个分片最大条目数
shard_key = "attack_type"  # 分片键
```

### 备份配置

```bash
# 在 preprocess.sh 中调整
max_backups=5  # 保留最近 5 个备份
compression_threshold=10485760  # 10MB 触发压缩
```

---

## 📈 性能提升预期

| 指标 | 优化前 | 优化后 |
|------|--------|--------|
| 状态冲突风险 | 高 | ✅ 无 |
| 知识库加载 | 全量 3.9MB | 按需 ~500KB |
| 备份恢复 | 手动 | ✅ 自动 |
| 增量更新 | 全量重写 | ✅ 只写变更 |
| 压缩率 | 无 | ✅ 60-70% |

---

## 🚨 故障恢复

### 状态文件损坏

```bash
# 1. 检查备份
ls -lt file_backups/

# 2. 恢复
cp file_backups/.lingshun_daemon_state_20260318_170000.json \
   .lingshun_daemon_state.json

# 3. 验证
./preprocess.sh validate
```

### 锁文件残留

```bash
# 清理所有锁文件（确保没有进程在运行）
rm -f .*.json.lock

# 或手动检查
lsof .*.json.lock
```

---

## 📝 日常维护

```bash
# 每日检查
./preprocess.sh status

# 每周清理旧备份
find file_backups -mtime +7 -delete

# 每月重新分片（如果数据增长）
./preprocess.sh shard
```

---

## 下一步

1. ✅ 运行 `./preprocess.sh all` 执行首次预处理
2. 🔄 修改灵顺守护进程使用状态锁
3. 🔄 修改知识库加载使用分片
4. 📊 监控性能提升效果
