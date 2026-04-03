# 🚪 项目入口 - 安全扫描器自治研发系统

**最后更新**: 2026-04-03 11:58  
**项目状态**: 🟢 运行中  
**当前任务**: 全量测试 (65,533 样本)

---

## 🎯 快速导航

### 我是新来的，如何开始？

```bash
# 1. 查看项目状态
cd ~/.openclaw/workspace/agent-security-skill-scanner-master
./manage_auto_rd.sh status

# 2. 查看历史进展
cat HISTORY_AND_LESSONS.md

# 3. 查看当前待办
cat TODO_AND_PROGRESS.md

# 4. 查看多层架构
cat MULTI_LAYER_INTEGRATION_STATUS.md

# 5. 启动/查看自治研发系统
./manage_auto_rd.sh start
./manage_auto_rd.sh logs -f
```

---

## 📊 当前系统状态

### 运行中进程
- **PID**: 1644175
- **服务**: `auto_rd_scanner.service`
- **任务**: 全量测试 (65,533 样本)
- **进度**: ~0.4% (250/65,533)
- **检测率**: 99.6% (249/250)

### 规则库
- **规则数**: 544 条 (YARA)
- **来源**: security-sample-generator
- **状态**: ✅ 已锁定 (只读)

### 多层架构
- **进度**: 4/8 层 (50%)
- **已集成**: YARA, AST, 行为分析，ML 分类
- **待集成**: 意图识别，控制流，语义分析

---

## 📋 核心文件清单

```
agent-security-skill-scanner-master/
├── 📖 文档入口
│   ├── PROJECT_ENTRY_POINT.md      # ⭐ 本文件 - 项目入口
│   ├── HISTORY_AND_LESSONS.md      # ⭐ 历史经验教训
│   ├── TODO_AND_PROGRESS.md        # ⭐ 当前待办和进展
│   └── MULTI_LAYER_INTEGRATION_STATUS.md  # 多层架构状态
│
├── 🤖 自动化系统
│   ├── auto_rd_scanner.py          # ⭐ 自治研发主程序
│   ├── critic_agent.py             # ⭐ 质疑反思 Agent
│   ├── multi_layer_scanner.py      # ⭐ 多层扫描器
│   ├── manage_auto_rd.sh           # ⭐ 统一管理脚本
│   └── protect_rules.sh            # ⭐ 规则保护脚本
│
├── ⚙️ 系统配置
│   ├── auto_rd_scanner.service     # systemd 服务
│   └── SETUP_GUIDE.md              # 安装指南
│
└── 📂 规则目录
    └── scanner_v3/yara/
        └── scanner_rules.yar       # 544 条规则 (只读)
```

---

## 🔍 如何查看...

### 查看系统状态
```bash
./manage_auto_rd.sh status
```

### 查看实时日志
```bash
./manage_auto_rd.sh logs -f
```

### 查看全量测试进度
```bash
tail -f logs/auto_rd_scanner.log
```

### 查看规则目录
```bash
./protect_rules.sh --status
```

### 查看 systemd 服务
```bash
sudo systemctl status auto_rd_scanner
sudo journalctl -u auto_rd_scanner -f
```

---

## 📞 常用命令速查

| 操作 | 命令 |
|------|------|
| **启动服务** | `./manage_auto_rd.sh start` |
| **停止服务** | `./manage_auto_rd.sh stop` |
| **查看状态** | `./manage_auto_rd.sh status` |
| **查看日志** | `./manage_auto_rd.sh logs -f` |
| **规则保护** | `./protect_rules.sh --status` |
| **系统服务** | `sudo systemctl status auto_rd_scanner` |

---

## 🎓 新手必读

1. **只有一套系统**: `auto_rd_scanner.py` 是唯一指定的自动化系统
2. **规则目录神圣不可侵犯**: 必须通过 `protect_rules.sh` 修改
3. **进程锁保护**: 防止重复运行 (`/tmp/auto_rd_scanner.lock`)
4. **质疑反思**: 所有结果都要经过 Critic Agent 验证
5. **多层架构**: 正在恢复历史系统的 8 层检测架构

---

## 📚 重要文档

| 文档 | 说明 | 优先级 |
|------|------|--------|
| `PROJECT_ENTRY_POINT.md` | 项目入口 (本文件) | ⭐⭐⭐ |
| `HISTORY_AND_LESSONS.md` | 历史经验教训 | ⭐⭐⭐ |
| `TODO_AND_PROGRESS.md` | 当前待办和进展 | ⭐⭐⭐ |
| `SETUP_GUIDE.md` | 安装和使用指南 | ⭐⭐ |
| `MULTI_LAYER_INTEGRATION_STATUS.md` | 多层架构状态 | ⭐⭐ |
| `ENHANCED_AUTO_RD.md` | 增强版文档 | ⭐ |
| `CRITIC_AGENT_README.md` | 质疑反思 Agent | ⭐ |

---

## 🆘 遇到问题？

### 常见问题

**Q: 服务启动失败？**
```bash
# 查看错误日志
sudo journalctl -u auto_rd_scanner -n 50

# 检查规则目录
./protect_rules.sh --status

# 清理锁文件
rm -f /tmp/auto_rd_scanner.lock
```

**Q: 规则目录被修改？**
```bash
# 恢复规则
./protect_rules.sh --clean
./protect_rules.sh --lock
```

**Q: 有多个进程运行？**
```bash
# 停止所有进程
pkill -f "auto_rd_scanner.py"

# 启动单个进程
./manage_auto_rd.sh start
```

---

## 📊 项目关键指标

| 指标 | 当前值 | 目标 | 状态 |
|------|--------|------|------|
| **检测率** | 99.6% | ≥98% | ✅ |
| **误报率** | 0.0% | ≤2% | ✅ |
| **规则数** | 544 条 | - | ✅ |
| **测试样本** | 65,533 个 | - | ✅ |
| **多层架构** | 4/8 层 | 8/8 | 🟡 |

---

**最后更新**: 2026-04-03 11:58  
**维护者**: 自治研发系统  
**联系方式**: `./manage_auto_rd.sh status`
