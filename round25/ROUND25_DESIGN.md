# Round 25: 实时监测与自动响应 - 设计文档

**状态**: 🔄 规划中  
**启动时间**: 2026-03-24 22:25  
**预计完成**: 1-2 小时

---

## 🎯 目标

从**被动扫描**升级为**主动监测**，实现文件系统实时监控 + 自动响应。

---

## 📋 核心需求

### 功能需求

| 需求 | 说明 | 优先级 |
|------|------|--------|
| **文件监听** | 监控指定目录的文件变化 | 🔴 高 |
| **实时扫描** | 文件变化时自动扫描 | 🔴 高 |
| **告警通知** | 发现威胁时立即告警 | 🔴 高 |
| **自动响应** | 隔离/删除/记录恶意文件 | 🟡 中 |
| **日志审计** | 完整操作日志 | 🔴 高 |

### 质量要求

- **响应延迟**: <100ms (文件变化到扫描完成)
- **资源占用**: CPU <5%, 内存 <100MB
- **扫描速度**: <50ms/文件
- **误报处理**: 白名单机制
- **持久化**: 配置/日志/状态持久化

---

## 🏗️ 技术架构

### 系统架构

```
[文件系统] 
    ↓ (inotify/fsevents 事件)
[File Watcher]
    ↓ (事件队列)
[Event Processor]
    ↓ (扫描请求)
[Scanner V3 (ML 增强)]
    ↓ (检测结果)
[Response Engine]
    ↓ (告警/隔离/日志)
[Dashboard + 通知]
```

### 核心组件

#### 1. File Watcher (文件监听器)

```python
# 使用 watchdog 库
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MalwareFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        # 文件创建 → 扫描
    def on_modified(self, event):
        # 文件修改 → 扫描
    def on_moved(self, event):
        # 文件移动 → 扫描
```

#### 2. Event Processor (事件处理器)

```python
# 事件队列 + 去重 + 批处理
class EventProcessor:
    def __init__(self):
        self.event_queue = Queue()
        self.scanned_files = LRUCache(maxsize=1000)
    
    def process_event(self, event):
        # 去重 (避免重复扫描)
        # 批处理 (批量扫描)
        # 优先级 (可执行文件优先)
```

#### 3. Response Engine (响应引擎)

```python
# 分级响应
class ResponseEngine:
    def respond(self, scan_result):
        if result.risk_score >= 80:  # Critical
            self.isolate_file()
            self.send_alert()
        elif result.risk_score >= 60:  # High
            self.log_threat()
            self.send_alert()
        elif result.risk_score >= 40:  # Medium
            self.log_threat()
```

#### 4. Alert System (告警系统)

```python
# 多通道告警
class AlertSystem:
    def send_alert(self, threat_info):
        self.log_alert(threat_info)      # 日志
        self.send_email(threat_info)     # 邮件
        self.send_webhook(threat_info)   # Webhook
        self.update_dashboard(threat_info)  # 仪表板
```

---

## 📁 文件结构

```
round25/
├── ROUND25_DESIGN.md              # 设计文档 (本文件)
├── watcher/
│   ├── file_watcher.py            # 文件监听器
│   ├── event_processor.py         # 事件处理器
│   └── config.yaml                # 配置文件
├── response/
│   ├── response_engine.py         # 响应引擎
│   ├── alert_system.py            # 告警系统
│   └── quarantine.py              # 隔离区管理
├── integration/
│   └── realtime_scanner.py        # 实时扫描器 (主入口)
├── test/
│   ├── test_watcher.py            # 监听器测试
│   └── test_response.py           # 响应测试
├── reports/
│   └── ROUND25_REPORT.md          # 完成报告
└── README.md                      # 使用文档
```

---

## 🚀 实施步骤

### Step 1: 文件监听器 (30 分钟)

```bash
# 安装依赖
pip install watchdog

# 创建监听器
python3 round25/watcher/file_watcher.py
```

### Step 2: 事件处理器 (20 分钟)

```python
# 实现事件队列
# 实现去重逻辑
# 实现批处理
```

### Step 3: 响应引擎 (30 分钟)

```python
# 实现分级响应
# 实现隔离功能
# 实现告警通知
```

### Step 4: 集成测试 (30 分钟)

```python
# 创建测试样本
# 触发文件事件
# 验证响应行为
```

---

## 🎯 使用场景

### 场景 1: 开发环境监控

```bash
# 监控项目目录
python3 round25/integration/realtime_scanner.py \
  --watch ~/projects/my-app \
  --alert-email security@company.com
```

### 场景 2: 下载目录监控

```bash
# 监控下载目录
python3 round25/integration/realtime_scanner.py \
  --watch ~/Downloads \
  --auto-quarantine \
  --alert-webhook https://hooks.slack.com/xxx
```

### 场景 3: 服务器监控

```bash
# 监控关键目录
python3 round25/integration/realtime_scanner.py \
  --watch /etc /usr/bin /opt \
  --config /etc/scanner-v3/config.yaml \
  --daemon
```

---

## 📊 预期效果

### 性能指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 响应延迟 | <100ms | 文件变化到扫描完成 |
| 扫描速度 | <50ms/文件 | 单文件扫描时间 |
| 资源占用 | CPU<5%, Mem<100MB | 空闲状态 |
| 并发处理 | 100 事件/秒 | 峰值处理能力 |

### 检测效果

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 检出率 | ≥98% | 恶意文件检出 |
| 误报率 | <1% | 安全文件误判 |
| 响应时间 | <1s | 发现到告警 |
| 隔离成功率 | 100% | 恶意文件隔离 |

---

## ⚠️ 风险与挑战

### 挑战 1: 性能影响

**问题**: 持续监听可能影响系统性能

**解决方案**:
- 低优先级线程
- 批处理事件
- 跳过大文件 (>100MB)
- 跳过已知安全目录

### 挑战 2: 误报处理

**问题**: 误报影响用户体验

**解决方案**:
- 白名单机制
- 分级响应 (Critical 才隔离)
- 人工审核选项
- 快速恢复功能

### 挑战 3: 对抗规避

**问题**: 恶意软件可能尝试绕过监听

**解决方案**:
- 多目录监控
- 随机扫描间隔
- 完整性校验
- 系统级监控 (auditd)

---

## 🎓 创新点

### 1. 智能优先级

```python
# 根据文件类型/位置/行为分配优先级
priority = calculate_priority(file_path, event_type)

# 可执行文件 > 脚本 > 文档
# 系统目录 > 用户目录 > 临时目录
# 创建事件 > 修改事件 > 删除事件
```

### 2. 行为学习

```python
# 学习用户行为模式
# 正常写入 → 低优先级
# 异常写入 → 高优先级
# 夜间活动 → 提高警觉
```

### 3. 协同防御

```python
# 多机共享威胁情报
# A 机器发现 → B 机器预警
# 云端规则更新 → 本地即时应用
```

---

## ✅ 验收清单

- [ ] 文件监听器实现
- [ ] 事件处理器实现
- [ ] 响应引擎实现
- [ ] 告警系统实现
- [ ] 隔离区管理
- [ ] 配置管理
- [ ] 日志审计
- [ ] 集成测试
- [ ] 性能测试
- [ ] 使用文档

---

**准备启动 Round 25！** 🚀

下一步：实现文件监听器 → 事件处理器 → 响应引擎 → 集成测试
