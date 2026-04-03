# 🎯 系统命名和版本说明

**创建时间**: 2026-04-03 12:12  
**目的**: 明确系统命名，避免与老系统混淆

---

## 📛 系统名称

### 正式名称：**灵顺融合版 (Lingshun-Fused)**

**版本号**: v3.0  
**代号**: Sentinel (哨兵)  
**状态**: 🟢 唯一指定

---

## 📚 版本历史

| 版本 | 名称 | 状态 | 说明 |
|------|------|------|------|
| **v1.0** | 灵顺系统 | ❌ 已废弃 | 老系统，已停止维护 |
| **v2.0** | 灵顺自治版 | ❌ 已废弃 | 过渡版本，已停止维护 |
| **v3.0** | 灵顺融合版 | ✅ **当前** | 融合历史系统能力，唯一指定 |

---

## ⚠️ 重要提醒

### ❌ 不要启动的老系统

**这些系统已废弃，启动会导致冲突**:

```bash
# ❌ 错误：启动老灵顺系统
python3 skills/agent-security-skill-scanner/expert_mode/lingshun_v5.py
python3 skills/agent-security-skill-scanner/expert_mode/lingshun_daemon.py

# ❌ 错误：启动 ROS 系统
python3 skills/research-orchestrator/research_cycle.py

# ❌ 错误：启动旧编排器
python3 agent-security-skill-scanner-master/auto-rd-daemon/enhanced_orchestrator.py
python3 agent-security-skill-scanner-master/auto-rd-daemon/fused_orchestrator.py
```

**后果**:
- 多进程冲突
- 规则目录混乱
- 数据不一致
- 无法追溯变更

---

### ✅ 唯一正确的启动方式

```bash
# ✅ 正确：使用唯一入口
cd ~/.openclaw/workspace/agent-security-skill-scanner-master
./START_HERE.sh

# ✅ 正确：使用管理脚本
./manage_auto_rd.sh status
./manage_auto_rd.sh start
./manage_auto_rd.sh logs -f

# ✅ 正确：使用 systemd 服务
sudo systemctl status auto_rd_scanner
sudo systemctl start auto_rd_scanner
```

---

## 🎯 如何识别当前系统

### 检查进程

```bash
# ✅ 正确的进程
ps aux | grep "auto_rd_scanner.py"
ps aux | grep "fused_scanner_auto_rd.py"

# ❌ 错误的进程 (如果看到，立即停止)
ps aux | grep "lingshun_daemon.py"
ps aux | grep "enhanced_orchestrator.py"
ps aux | grep "ros_"
```

### 检查服务

```bash
# ✅ 正确的服务
sudo systemctl status auto_rd_scanner

# ❌ 错误的服务 (如果存在，禁用)
sudo systemctl status lingshun
sudo systemctl status ros
```

### 检查 Cron

```bash
# ✅ 应该为空
crontab -l

# ❌ 如果有这些，立即删除
*/5 * * * * hros_auto_start.sh
*/5 * * * * progress_reporter.py
```

---

## 📞 快速参考

| 问题 | 答案 |
|------|------|
| **系统叫什么？** | 灵顺融合版 (Lingshun-Fused) v3.0 |
| **如何启动？** | `./START_HERE.sh` |
| **如何查看状态？** | `./manage_auto_rd.sh status` |
| **老系统能用吗？** | ❌ 不能，已废弃 |
| **如何避免混淆？** | 只使用 `START_HERE.sh` 入口 |
| **版本號是多少？** | v3.0 (融合版) |

---

## 🔒 安全启动检查清单

启动前请确认：

- [ ] 已停止所有老系统进程
- [ ] Cron 任务已禁用
- [ ] 规则目录已锁定
- [ ] 使用 `START_HERE.sh` 启动
- [ ] 确认进程名为 `auto_rd_scanner.py` 或 `fused_scanner_auto_rd.py`

---

## 📊 系统能力对比

| 功能 | 灵顺 v1 | 灵顺 v2 | **灵顺 v3** |
|------|--------|--------|-----------|
| YARA 规则 | ✅ | ✅ | ✅ |
| 进程锁保护 | ❌ | ❌ | ✅ |
| 规则目录保护 | ❌ | ❌ | ✅ |
| 质疑反思 Agent | ❌ | ❌ | ✅ |
| 多层架构 | ❌ | 部分 | ✅ (融合) |
| 优先级队列 | ❌ | ❌ | ✅ (融合) |
| 故障处理 | ❌ | ❌ | ✅ (融合) |
| Skill 服务池 | ❌ | ❌ | ✅ (融合) |
| systemd 服务 | ❌ | ❌ | ✅ |
| 统一 CLI | ❌ | ❌ | ✅ |

---

## 🎓 记忆口诀

```
灵顺系统要记牢，
v3 融合是唯一。
老系统们已废弃，
START_HERE 是入口。
多进程会冲突，
规则目录要保护。
哨兵守护 7x24，
安全扫描最可靠！
```

---

**最后更新**: 2026-04-03 12:12  
**维护者**: 灵顺融合版 v3.0  
**唯一入口**: `./START_HERE.sh`
