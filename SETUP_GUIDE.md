# 🛡️ 自治研发系统安装指南

**版本**: v2.0  
**创建时间**: 2026-04-03  
**状态**: ✅ 生产就绪

---

## 📋 概述

本系统提供**统一的自动化研究系统**，具备：
- ✅ 进程锁保护（防止重复运行）
- ✅ systemd 服务管理
- ✅ 规则目录保护
- ✅ 统一命令行接口

---

## 🚀 快速安装

### 1. 停止所有冲突进程

```bash
cd ~/.openclaw/workspace/agent-security-skill-scanner-master

# 停止所有冲突进程
pkill -f "auto_rd_scanner.py"
pkill -f "enhanced_orchestrator"
pkill -f "progress_reporter"
pkill -f "ros_"
pkill -f "monitor_test"
```

### 2. 清理环境

```bash
# 清理锁文件
rm -f /tmp/auto_rd_scanner.lock

# 清理规则目录
./protect_rules.sh --clean
./protect_rules.sh --lock
```

### 3. 安装 systemd 服务

```bash
# 需要 sudo 密码
sudo ./install_auto_rd_service.sh
```

### 4. 验证安装

```bash
./manage_auto_rd.sh status
```

---

## 🎮 使用方法

### 管理服务

```bash
# 查看状态
./manage_auto_rd.sh status

# 启动服务
./manage_auto_rd.sh start

# 停止服务
./manage_auto_rd.sh stop

# 重启服务
./manage_auto_rd.sh restart
```

### 查看日志

```bash
# 查看最近日志
./manage_auto_rd.sh logs

# 实时查看日志
./manage_auto_rd.sh logs -f
```

### 手动运行

```bash
# 单次运行（带进程锁保护）
python3 auto_rd_scanner.py

# 如果已有进程运行，会提示：
# ❌ 已有进程运行中 (PID: 12345)
```

---

## 🔒 进程锁保护

系统使用文件锁防止重复运行：

```bash
# 锁文件位置
/tmp/auto_rd_scanner.lock

# 手动清理锁文件（如果进程异常终止）
rm -f /tmp/auto_rd_scanner.lock
```

---

## 📊 规则目录保护

```bash
# 查看规则目录状态
./protect_rules.sh --status

# 清理规则目录
./protect_rules.sh --clean

# 解锁（修改前）
./protect_rules.sh --unlock

# 锁定（修改后）
./protect_rules.sh --lock

# 记录变更
./protect_rules.sh --log "修改原因"
```

---

## ⚙️ systemd 服务配置

服务文件：`auto_rd_scanner.service`

**特性**:
- 资源限制（CPU 50%, 内存 2GB）
- 安全设置（NoNewPrivileges, ProtectSystem）
- 自动日志记录
- 开机自启

**管理命令**:
```bash
# 系统级命令
sudo systemctl start auto_rd_scanner
sudo systemctl stop auto_rd_scanner
sudo systemctl status auto_rd_scanner
sudo journalctl -u auto_rd_scanner -f
```

---

## 🛑 禁用旧系统

**重要**: 禁用所有冲突的自动化系统

### 1. 禁用 cron 任务

```bash
# 备份当前 cron
crontab -l > /tmp/crontab.backup

# 禁用 cron
crontab -r
```

### 2. 停止旧进程

```bash
# 停止所有旧系统进程
pkill -f "enhanced_orchestrator.py"
pkill -f "progress_reporter.py"
pkill -f "ros_cycle.py"
pkill -f "ros_self_learner.py"
pkill -f "hros_auto_start.sh"
```

### 3. 禁用 systemd 服务（如果有）

```bash
# 查找相关服务
systemctl list-units | grep -i "auto\|ros\|ling"

# 禁用服务
sudo systemctl stop <service_name>
sudo systemctl disable <service_name>
```

---

## 📈 监控与日志

### 日志位置

```
~/.openclaw/workspace/agent-security-skill-scanner-master/logs/
├── auto_rd_scanner.log      # 主日志
├── full_test_*.log          # 全量测试日志
└── progress_reporter.log    # 进度报告（旧系统）
```

### 实时监控

```bash
# 使用管理脚本
./manage_auto_rd.sh logs -f

# 或直接查看
tail -f logs/auto_rd_scanner.log
```

---

## 🎯 最佳实践

### 1. 只运行一个实例

```bash
# ✅ 正确：使用管理脚本
./manage_auto_rd.sh start

# ❌ 错误：直接运行多个实例
python3 auto_rd_scanner.py &
python3 auto_rd_scanner.py &  # 会被进程锁阻止
```

### 2. 定期清理规则目录

```bash
# 每周清理一次
./protect_rules.sh --clean
```

### 3. 记录所有变更

```bash
# 每次修改规则后记录
./protect_rules.sh --log "优化 data_exfiltration 规则"
```

### 4. 监控资源使用

```bash
# 查看服务资源使用
systemctl status auto_rd_scanner

# 查看系统资源
top -p $(cat /tmp/auto_rd_scanner.lock)
```

---

## 🔧 故障排查

### 问题 1: 进程锁无法释放

**症状**: 无法启动，提示已有进程运行

**解决**:
```bash
# 检查进程是否存在
PID=$(cat /tmp/auto_rd_scanner.lock)
ps -p $PID

# 如果进程不存在，清理锁文件
rm -f /tmp/auto_rd_scanner.lock
```

### 问题 2: 规则目录被修改

**症状**: 规则文件数量变化

**解决**:
```bash
# 清理并锁定
./protect_rules.sh --clean
./protect_rules.sh --lock

# 检查是否有旧系统进程
ps aux | grep -E "orchestrat|progress|ros_"
```

### 问题 3: 服务无法启动

**症状**: `systemctl start` 失败

**解决**:
```bash
# 查看详细错误
sudo journalctl -u auto_rd_scanner -n 50

# 检查 Python 环境
python3 --version
which python3

# 重新安装服务
sudo ./install_auto_rd_service.sh
```

---

## 📞 支持

- **文档**: 查看本文件和 AUTO_RD_README.md
- **日志**: `logs/auto_rd_scanner.log`
- **状态**: `./manage_auto_rd.sh status`

---

**一套系统，统一管理！** 🎯
