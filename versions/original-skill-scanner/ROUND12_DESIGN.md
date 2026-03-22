# 🚨 Round 12 - 实时检测与告警系统集成

**日期**: 2026-03-22  
**目标**: 实时文件监控 + 告警通知 + Web 仪表板 + 规则热更新

---

## 🎯 目标

| 功能模块 | 目标 | 状态 |
|----------|------|------|
| **实时文件监控** | inotify/fsevents 监控，<100ms 响应 | 🔴 待完成 |
| **告警通知** | 邮件/钉钉/飞书，支持多渠道 | 🔴 待完成 |
| **Web 仪表板** | 实时检测展示、统计图表 | 🔴 待完成 |
| **规则热更新** | 无需重启加载新规则 | 🔴 待完成 |

---

## 📋 任务清单

### 1. 实时文件监控 (File Watcher)

**技术选型**:
- Linux: `inotify` (pyinotify)
- macOS: `FSEvents` (watchdog)
- Windows: `ReadDirectoryChangesW` (watchdog)

**监控目标**:
| 目录 | 监控事件 | 响应时间 |
|------|----------|----------|
| `~/Downloads/` | 文件创建、修改 | <100ms |
| `~/Desktop/` | 文件创建、修改 | <100ms |
| `/tmp/` | 可疑文件创建 | <50ms |
| `~/.ssh/` | 文件修改、删除 | <50ms |

**检测流程**:
```
文件事件 → 文件扫描 → 规则匹配 → 告警生成 → 通知发送
   ↓
事件日志 → 数据库存储 → 仪表板展示
```

---

### 2. 告警通知系统 (Alert Notifier)

**通知渠道**:

| 渠道 | 优先级 | 延迟 | 状态 |
|------|--------|------|------|
| **飞书 webhook** | P0 | <1s | 🔴 待配置 |
| **钉钉 webhook** | P0 | <1s | 🔴 待配置 |
| **邮件 SMTP** | P1 | <5s | 🔴 待配置 |
| **系统通知** | P2 | 即时 | 🔴 待实现 |

**告警级别**:
| 级别 | 名称 | 触发条件 | 通知渠道 |
|------|------|----------|----------|
| **P0** | 严重 | critical 规则触发 | 飞书 + 钉钉 + 邮件 |
| **P1** | 高危 | high 规则触发 | 飞书 + 邮件 |
| **P2** | 中危 | medium 规则触发 | 邮件 |
| **P3** | 低危 | low 规则触发 | 日志记录 |

**告警模板**:
```markdown
🚨 安全告警 - {级别}

**时间**: {timestamp}
**文件**: {file_path}
**威胁类型**: {attack_type}
**触发规则**: {rule_name}
**严重程度**: {severity}
**风险评分**: {risk_score}

**建议操作**:
1. 隔离文件
2. 扫描关联文件
3. 检查系统日志
```

---

### 3. Web 仪表板 (Dashboard)

**技术栈**:
- 后端：FastAPI (轻量、异步)
- 前端：Vue3 + ECharts (响应式图表)
- 数据库：SQLite (轻量) / PostgreSQL (生产)

**功能模块**:

| 模块 | 功能 | 状态 |
|------|------|------|
| **概览** | 今日检测数、告警统计、趋势图 | 🔴 |
| **实时监控** | 文件事件流、检测日志 | 🔴 |
| **告警中心** | 告警列表、处理状态、筛选 | 🔴 |
| **规则管理** | 规则列表、启用/禁用、版本 | 🔴 |
| **统计分析** | 攻击类型分布、时间趋势 | 🔴 |
| **系统设置** | 监控目录、通知配置、阈值 | 🔴 |

**页面设计**:
```
/dashboard
├── /overview          # 概览页
├── /realtime          # 实时监控
├── /alerts            # 告警中心
├── /rules             # 规则管理
├── /analytics         # 统计分析
└── /settings          # 系统设置
```

---

### 4. 规则热更新 (Hot Reload)

**功能需求**:
- 检测规则文件变化 (inotify)
- 自动重新加载规则
- 规则版本控制
- 回滚机制

**实现方案**:
```python
class RuleManager:
    def __init__(self):
        self.rules = []
        self.version = "1.0"
        self.watcher = RuleFileWatcher()
    
    def reload_rules(self):
        """热加载规则"""
        new_rules = self._load_rules()
        old_version = self.version
        self.rules = new_rules
        self.version = self._calculate_version()
        
        # 记录变更
        self._log_change(old_version, self.version)
        
        # 通知仪表板
        self._notify_dashboard()
    
    def rollback(self, target_version):
        """回滚到指定版本"""
        backup = self._get_backup(target_version)
        self.rules = backup['rules']
        self.version = target_version
```

**版本管理**:
```
rules/
├── current/           # 当前规则
├── versions/          # 历史版本
│   ├── v10.0/
│   ├── v11.0/
│   └── v12.0/
└── backups/           # 自动备份
```

---

## 📁 文件结构

```
expert_mode/
├── ROUND12_DESIGN.md
├── round12/
│   ├── file_watcher.py        # 文件监控
│   ├── alert_notifier.py      # 告警通知
│   ├── rule_manager.py        # 规则管理 (热更新)
│   ├── dashboard/
│   │   ├── main.py            # FastAPI 后端
│   │   ├── models.py          # 数据模型
│   │   ├── api/
│   │   │   ├── alerts.py      # 告警 API
│   │   │   ├── rules.py       # 规则 API
│   │   │   └── stats.py       # 统计 API
│   │   ├── static/            # 前端静态文件
│   │   └── templates/         # HTML 模板
│   ├── database.py            # 数据库操作
│   └── config.yaml            # 配置文件
├── database/
│   └── security.db            # SQLite 数据库
└── logs/
    └── detector.log           # 检测日志
```

---

## 🚀 执行步骤

### Step 1: 创建数据库模型
```bash
cd ~/.openclaw/workspace/skills/agent-security-skill-scanner/expert_mode
python3 round12/database.py --init
```

### Step 2: 配置文件监控
```bash
python3 round12/file_watcher.py --watch ~/Downloads --watch ~/Desktop
```

### Step 3: 配置告警通知
```bash
python3 round12/alert_notifier.py --test-feishu --test-email
```

### Step 4: 启动 Web 仪表板
```bash
python3 round12/dashboard/main.py --host 0.0.0.0 --port 8080
```

### Step 5: 测试热更新
```bash
python3 round12/rule_manager.py --hot-reload --test
```

---

## 📊 质量指标

| 指标 | 目标 | 测量方法 |
|------|------|----------|
| **监控响应** | <100ms | 文件创建到检测完成 |
| **告警延迟** | <1s | 规则触发到通知发送 |
| **仪表板加载** | <2s | 页面打开到完全渲染 |
| **热更新时间** | <500ms | 规则文件变化到加载完成 |
| **系统资源** | CPU<5%, 内存<200MB | 空闲状态监控 |

---

## ✅ 完成标准

- [ ] 文件监控正常运行 (inotify/watchdog)
- [ ] 告警通知可用 (飞书/钉钉/邮件至少 1 个)
- [ ] Web 仪表板可访问 (概览 + 告警列表)
- [ ] 规则热更新功能正常
- [ ] 完成 Round 12 报告

---

## 🔧 配置示例

### 配置文件 (round12/config.yaml)

```yaml
# 监控配置
watcher:
  directories:
    - ~/Downloads
    - ~/Desktop
    - /tmp
  exclude_patterns:
    - "*.tmp"
    - "*.log"
    - ".git/*"

# 告警配置
alerts:
  feishu:
    enabled: true
    webhook: "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
  dingtalk:
    enabled: false
    webhook: "https://oapi.dingtalk.com/robot/send?access_token=xxx"
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "your@email.com"
    password: "your_password"

# 仪表板配置
dashboard:
  host: "0.0.0.0"
  port: 8080
  auth:
    enabled: false
    username: "admin"
    password: "admin123"

# 数据库配置
database:
  type: "sqlite"
  path: "./database/security.db"
```

---

**位置**: `~/.openclaw/workspace/skills/agent-security-skill-scanner/expert_mode/`  
**下一轮**: Round 13 - AI 驱动的威胁狩猎与自动化响应
