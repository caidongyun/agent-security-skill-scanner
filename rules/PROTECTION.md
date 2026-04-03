# 🛡️ 规则目录保护机制

**版本**: v1.0  
**创建时间**: 2026-04-03  
**状态**: ✅ 强制执行

---

## ⚠️ 问题

规则目录 `rules/scanner_v3/yara/` 经常被**多个自动化进程**同时修改，导致：
- 规则文件冲突
- 重复规则生成
- 测试数据不一致
- 无法追溯变更

---

## 🎯 解决方案

### 1. 单一写入源

**只有**以下脚本可以修改规则目录：
- ✅ `auto_rd_scanner.py` (自治研发系统)
- ✅ `manual_rule_update.sh` (手动更新脚本)

**禁止**以下进程修改规则目录：
- ❌ `enhanced_orchestrator.py`
- ❌ `progress_reporter.py`
- ❌ `hros_auto_start.sh`
- ❌ 其他任何自动化脚本

---

### 2. 规则目录锁定

```bash
# 规则目录权限设置
rules/scanner_v3/yara/
└── scanner_rules.yar  # 只读 (444)

# 修改前必须：
chmod 644 scanner_rules.yar

# 修改后必须：
chmod 444 scanner_rules.yar
```

---

### 3. 变更管理流程

```
修改规则流程:
1. 备份当前规则
   cp scanner_rules.yar scanner_rules.yar.backup_$(date +%Y%m%d_%H%M%S)

2. 解除只读锁定
   chmod 644 scanner_rules.yar

3. 修改规则
   (复制或编辑规则文件)

4. 验证规则
   python3 -c "import yara; yara.compile('scanner_rules.yar')"

5. 重新锁定
   chmod 444 scanner_rules.yar

6. 记录变更
   echo "$(date): 更新规则 - 原因" >> CHANGELOG.md
```

---

### 4. 进程管理

**启动前检查**:
```bash
# 检查是否有冲突进程
ps aux | grep -E "auto_rd|orchestrat|progress" | grep -v grep

# 如果有多个 auto_rd_scanner.py 进程，只保留一个
```

**停止冲突进程**:
```bash
# 停止所有冲突进程
pkill -f "enhanced_orchestrator.py"
pkill -f "progress_reporter.py"
pkill -f "hros_auto_start.sh"

# 只保留 auto_rd_scanner.py (最多 1 个进程)
```

---

### 5. 监控与告警

**规则目录监控脚本** (`watch_rules.sh`):
```bash
#!/bin/bash
# 监控规则目录变化

RULES_DIR="/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/rules/scanner_v3/yara"
LAST_CHECK=$(stat -c %Y "$RULES_DIR")

while true; do
    CURRENT=$(stat -c %Y "$RULES_DIR")
    if [ "$CURRENT" != "$LAST_CHECK" ]; then
        echo "[$(date)] ⚠️  规则目录发生变化!"
        ls -la "$RULES_DIR"
        LAST_CHECK=$CURRENT
    fi
    sleep 60
done
```

---

## 📋 变更日志模板

```markdown
# 规则目录变更日志

## 2026-04-03

| 时间 | 操作 | 操作人 | 原因 | 规则数 |
|------|------|--------|------|--------|
| 11:00 | 更新 | auto_rd | 自治研发 | 544 条 |
| 10:00 | 清理 | admin | 清理垃圾文件 | 544 条 |

## 变更流程

1. 备份 → 2. 解锁 → 3. 修改 → 4. 验证 → 5. 锁定 → 6. 记录
```

---

## 🚨 违规处理

**发现未经授权的修改**:
1. 立即恢复备份
2. 查找修改进程
3. 停止冲突进程
4. 记录事件
5. 修复流程

---

## 📞 负责人

- **主要维护**: auto_rd_scanner.py
- **监督**: 系统管理员
- **审计**: 每周检查 CHANGELOG.md

---

**规则目录神圣不可侵犯！** 🛡️
