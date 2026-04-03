# 📚 历史经验教训 - 安全扫描器研发

**创建时间**: 2026-04-03  
**目的**: 记录历史系统的有价值经验，避免重复犯错

---

## 🎯 核心教训

### 1. 不要轻信完美数据 ⚠️

**问题**: 检测率 99.8% 过于完美，可能存在：
- 数据泄露
- 过拟合
- 测试集同质化
- LLM 幻觉

**解决方案**:
- ✅ 质疑反思 Agent (critic_agent.py)
- ✅ 全量测试 (65,533 样本)
- ✅ 分层抽样
- ✅ 独立测试集验证

**教训**: **永远保持怀疑，数据不会说谎但会误导**

---

### 2. 多进程冲突是灾难 ⚠️

**问题**: 多个自动化系统同时修改规则目录
- enhanced_orchestrator.py
- progress_reporter.py
- ros_cycle.py
- hros_auto_start.sh

**后果**:
- 规则文件冲突
- 重复规则生成
- 测试数据不一致
- 无法追溯变更

**解决方案**:
- ✅ 单一写入源 (只有 auto_rd_scanner.py)
- ✅ 进程锁保护 (`/tmp/auto_rd_scanner.lock`)
- ✅ systemd 服务管理
- ✅ 规则目录锁定 (444 权限)

**教训**: **一套系统，一个入口，严格锁机制**

---

### 3. 规则目录需要严格保护 ⚠️

**问题**: 规则目录经常被自动修改

**解决方案**:
- ✅ protect_rules.sh (规则保护脚本)
- ✅ 变更流程：备份 → 解锁 → 修改 → 验证 → 锁定 → 记录
- ✅ CHANGELOG.md (变更日志)
- ✅ backup/ (备份目录)

**教训**: **规则目录神圣不可侵犯，变更必须记录和追溯**

---

### 4. 多层架构很重要 ⚠️

**历史系统有**:
- Layer 1: YARA 规则 ✅
- Layer 2: 意图识别 ❌ 缺失
- Layer 3: AST 分析 ✅ 可用
- Layer 4: 控制流 ❌ 缺失
- Layer 5: 语义分析 ❌ 缺失
- Layer 6: 行为分析 ✅ 可用
- Layer 7: ML 分类 ✅ 可用
- Layer 8: LLM 分析 ❌ 禁用

**教训**: **基础扫描 + 深度分析 = 完整检测能力**

---

### 5. 自动化需要监控 ⚠️

**问题**: 自动化进程运行后不知道状态

**解决方案**:
- ✅ manage_auto_rd.sh (统一 CLI)
- ✅ systemd 服务
- ✅ 实时日志
- ✅ 状态检查命令

**教训**: **自动化不等于放任，需要实时监控和干预能力**

---

### 6.  Cron 任务会捣乱 ⚠️

**问题**: Cron 每 5 分钟自动运行旧系统
```bash
*/5 * * * * hros_auto_start.sh
*/5 * * * * progress_reporter.py
```

**解决方案**:
- ✅ 禁用 Cron (`crontab -r`)
- ✅ 备份 Cron (`crontab -l > /tmp/crontab.backup`)

**教训**: **检查所有定时任务，确保没有冲突**

---

### 7.  systemd 服务配置要正确 ⚠️

**问题**: ProtectSystem=strict 导致 /tmp 只读

**解决方案**:
```ini
ProtectSystem=full  # 不是 strict
ReadWritePaths=/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master /tmp
```

**教训**: **systemd 安全设置要测试，不要盲目使用最严格配置**

---

### 8. 全量测试比抽样更可靠 ⚠️

**问题**: 抽样 1000 个样本可能掩盖问题

**解决方案**:
- ✅ 全量测试 65,533 样本
- ✅ 分层抽样 (按攻击类型)
- ✅ 独立验证集

**教训**: **抽样用于快速验证，全量用于最终确认**

---

## 🏆 最佳实践

### 启动流程
```bash
# 1. 检查状态
./manage_auto_rd.sh status

# 2. 查看日志
./manage_auto_rd.sh logs -f

# 3. 确认无冲突进程
ps aux | grep -E "auto_rd|orchestrat|progress" | grep -v grep

# 4. 启动服务
./manage_auto_rd.sh start
```

### 规则修改流程
```bash
# 1. 备份
./protect_rules.sh --clean

# 2. 解锁
./protect_rules.sh --unlock

# 3. 修改
# (复制或编辑规则文件)

# 4. 验证
python3 -c "import yara; yara.compile('rules/scanner_v3/yara/scanner_rules.yar')"

# 5. 锁定
./protect_rules.sh --lock

# 6. 记录
./protect_rules.sh --log "修改原因"
```

### 故障排查流程
```bash
# 1. 查看服务状态
sudo systemctl status auto_rd_scanner

# 2. 查看错误日志
sudo journalctl -u auto_rd_scanner -n 50

# 3. 检查进程
ps aux | grep "auto_rd_scanner"

# 4. 检查锁文件
ls -la /tmp/auto_rd_scanner.lock

# 5. 清理并重启
rm -f /tmp/auto_rd_scanner.lock
./manage_auto_rd.sh restart
```

---

## 📊 系统演进历史

### v1.0 - 基础版 (2026-03)
- ✅ YARA 规则扫描
- ✅ 简单自动化
- ❌ 多进程冲突
- ❌ 无规则保护

### v2.0 - 增强版 (2026-04-03)
- ✅ 进程锁保护
- ✅ 规则目录保护
- ✅ 质疑反思 Agent
- ✅ systemd 服务
- ✅ 统一 CLI

### v3.0 - 多层架构 (进行中)
- ✅ YARA 规则
- ✅ AST 分析
- ✅ 行为分析
- ✅ ML 分类
- ⏳ 意图识别
- ⏳ 控制流
- ⏳ 语义分析

---

## 💡 关键决策记录

### 决策 1: 停止 security-sample-generator 自治
**原因**: 分散精力，规则质量参差不齐  
**结果**: 专注 agent-security-skill-scanner-master

### 决策 2: 全量测试 65,533 样本
**原因**: 抽样可能掩盖问题  
**结果**: 发现真实检测率 99.6%

### 决策 3: 禁用 Cron 任务
**原因**: 每 5 分钟自动运行旧系统，导致冲突  
**结果**: 系统稳定，无冲突

### 决策 4: 规则目录只读锁定
**原因**: 经常被自动修改  
**结果**: 规则变更可追溯

### 决策 5: 集成质疑反思 Agent
**原因**: 防止自嗨和 LLM 欺骗  
**结果**: 置信度 85%，结果可信

---

## 🎓 给后来者的建议

1. **先读 PROJECT_ENTRY_POINT.md** - 了解项目入口
2. **再读 HISTORY_AND_LESSONS.md** - 避免重复犯错
3. **查看 TODO_AND_PROGRESS.md** - 了解当前任务
4. **使用 manage_auto_rd.sh** - 统一管理接口
5. **保护规则目录** - 严格变更流程
6. **保持怀疑** - 质疑所有完美数据
7. **记录变更** - 方便追溯和回滚
8. **定期检查** - 确保系统正常运行

---

**最后更新**: 2026-04-03 11:58  
**维护者**: 自治研发系统  
**更新方式**: 每次遇到问题并解决后更新此文档
