# 🔄 规则沉淀机制 - 从研究到防护

## 整体流程

```
灵顺 V5 研究循环
      ↓
生成新规则/新样本
      ↓
rule_sync.py 自动同步
      ↓
agent-defender (Runtime 防护)
agent-dlp (入口/出口检测)
      ↓
实时防护生效
```

---

## 7 步完整闭环

| 步骤 | 模块 | 功能 | 输出 |
|------|------|------|------|
| 1 | 威胁情报采集 | 收集最新攻击手法 | 情报条目 |
| 2 | 样本探索 | 生成恶意样本 | 样本文件 |
| 3 | 规则研发 | 编写检测规则 | 规则草案 |
| 4 | 测试验证 | 运行测试套件 | 测试结果 |
| 5 | 质量评估 | 计算检测率/覆盖率 | 质量分数 |
| 6 | 反思迭代 | 优化规则 | 优化后规则 |
| **7** | **规则同步** | **沉淀到防护模块** | **实时防护** |

---

## 规则同步详解

### 同步时机

- **自动同步**: 守护进程每轮迭代后自动执行
- **手动同步**: 随时运行 `python3 rule_sync.py --sync`

### 同步内容

| 规则类型 | 同步目标 | 文件格式 |
|----------|----------|----------|
| Runtime 规则 | agent-defender/rules/ | JSON |
| DLP 检测规则 | agent-dlp/rules/ | JSON |
| 系统调用规则 | agent-defender/runtime/monitor.py | Python |
| 敏感数据规则 | agent-dlp/dlp/check.py | Python |

### 同步流程

```
1. 备份当前规则
   ↓
2. 读取新生成的规则
   ↓
3. 合并到 agent-defender
   ↓
4. 合并到 agent-dlp
   ↓
5. 验证规则有效性
   ↓
6. 生成变更报告
   ↓
7. 成功 ✅ / 失败回滚 🔄
```

---

## 文件结构

```
expert_mode/
├── lingshun_daemon.py          # 守护进程 (包含规则同步步骤)
├── rule_sync.py                # 规则同步模块
├── rules_backup/               # 规则备份目录
│   ├── backup_20260317_080000/
│   │   ├── defender_rules/
│   │   ├── dlp_rules/
│   │   ├── monitor.py
│   │   └── check.py
├── sync_reports/               # 同步报告
│   ├── sync_20260317_080000.json
├── rules_history.json          # 同步历史
├── agent-defender/             # 防护模块
│   ├── rules/                  # ← 同步到这里
│   │   ├── tool_poisoning_rules.json
│   │   ├── remote_load_rules.json
│   │   └── ...
│   └── runtime/monitor.py      # ← 更新这里
└── agent-dlp/                  # DLP 模块
    ├── rules/                  # ← 同步到这里
    │   └── custom_rules.json
    └── dlp/check.py            # ← 更新这里
```

---

## 使用方式

### 查看同步状态

```bash
cd /home/cdy/.openclaw/workspace/skills/agent-security-skill-scanner/expert_mode

# 查看同步状态
python3 rule_sync.py --status
```

输出示例:
```
============================================================
📊 规则同步状态
============================================================
最后同步：2026-03-17T08:30:00
总同步次数：15
总回滚次数：1

Defender 规则文件：8 个
DLP 规则文件：3 个

规则备份：5 个

最近同步报告:
  - sync_20260317_083000: 12 条规则
  - sync_20260317_080000: 8 条规则
```

### 手动同步

```bash
# 同步规则
python3 rule_sync.py --sync

# 强制同步 (跳过验证)
python3 rule_sync.py --sync --force
```

### 验证规则

```bash
# 验证当前规则有效性
python3 rule_sync.py --verify
```

### 回滚

```bash
# 回滚到指定备份
python3 rule_sync.py --rollback backup_20260317_080000

# 查看可用备份
ls rules_backup/
```

---

## 变更报告

每次同步生成详细报告：

```json
{
  "timestamp": "2026-03-17T08:30:00",
  "summary": {
    "total_new_rules": 12,
    "defender_updated": 8,
    "dlp_updated": 4
  },
  "defender_rules": [
    "RT-019",
    "RT-020",
    "RT-021"
  ],
  "dlp_rules": [
    "DLP-027",
    "DLP-028"
  ],
  "details": [
    {
      "id": "RT-019",
      "category": "syscall",
      "description": "检测 ptrace 调试器注入",
      "pattern": "ptrace\\(PTRACE_",
      "risk": "HIGH"
    }
  ]
}
```

---

## 安全机制

### 1. 备份机制

- 每次同步前自动备份
- 保留最近 5 个备份
- 支持一键回滚

### 2. 验证机制

- 语法检查 (JSON/Python)
- 运行测试套件
- 验证通过率 > 90% 才生效

### 3. 回滚机制

触发条件:
- 语法错误
- 测试失败
- 运行时异常

自动回滚到上一个可用版本

### 4. 审计日志

记录所有变更:
- 同步时间
- 规则数量
- 规则详情
- 操作者 (自动/手动)

---

## 实际效果

### 示例：发现新攻击手法

**第 1 步**: 灵顺 V5 发现新攻击
```
🔍 威胁情报采集: 发现新攻击手法 - ptrace 注入
🧬 样本设计：生成 ptrace_inject_sample.py
📝 规则研发：编写 RT-019 规则
🧪 测试验证：通过率 100%
📊 质量评估：检测率 95%
🔄 规则同步：同步到 agent-defender/rules/syscall_rules.json
```

**第 2 步**: 防护生效
```
用户运行恶意技能:
  技能尝试：ptrace(PTRACE_ATTACH, ...)
  
Runtime 防护实时检测:
  ✅ 匹配规则 RT-019
  🚫 立即阻断执行
  📝 记录审计日志
```

### 防护时间线

| 时间 | 事件 |
|------|------|
| 08:00 | 灵顺 V5 发现 ptrace 攻击 |
| 08:05 | 生成检测规则 RT-019 |
| 08:06 | 测试验证通过 |
| 08:07 | **同步到 agent-defender** |
| 08:10 | 用户遭遇 ptrace 攻击 |
| 08:10 | **实时阻断** ✅ |

从发现到防护：**10 分钟**

---

## 监控与告警

### 检查规则是否更新

```bash
# 查看最新同步报告
cat sync_reports/sync_latest.json | jq '.summary'

# 查看 Defender 规则数量
ls agent-defender/rules/*.json | wc -l

# 查看 DLP 规则数量
ls agent-dlp/rules/*.json | wc -l
```

### 验证防护是否生效

```bash
# 运行防护测试
python3 agent-defender/scanner/scan.py <test_skill>

# 运行 DLP 测试
python3 agent-dlp/dlp/check.py "test input"
```

### 监控同步失败

守护进程日志中搜索:
```bash
grep "规则同步" logs/lingshun_daemon.log | tail -20

# 查看失败原因
grep "同步失败" logs/lingshun_daemon.log
```

---

## 最佳实践

### 1. 定期审查同步报告

```bash
# 每周审查
cat sync_reports/sync_*.json | jq '.summary'
```

### 2. 保留关键备份

```bash
# 标记重要备份
cp -r rules_backup/backup_20260317_080000/ rules_backup/stable_v1.0/
```

### 3. 测试环境验证

在生产环境同步前，先在测试环境验证:
```bash
# 测试环境同步
python3 rule_sync.py --sync --test-env
```

### 4. 版本控制

```bash
# 提交规则变更
git add agent-defender/rules/ agent-dlp/rules/
git commit -m "🛡️ 同步灵顺 V5 第 15 轮规则 (12 条新增)"
git push
```

---

## 故障排查

### 问题 1: 同步失败

```bash
# 查看详细错误
python3 rule_sync.py --sync 2>&1 | tail -50

# 检查规则语法
python3 -m json.tool agent-defender/rules/*.json > /dev/null

# 查看备份是否完整
ls -la rules_backup/latest/
```

### 问题 2: 规则未生效

```bash
# 检查是否同步成功
python3 rule_sync.py --status

# 检查防护模块是否加载
python3 agent-defender/scanner/scan.py --list-rules

# 重启防护服务
systemctl restart agent-defender
```

### 问题 3: 回滚后仍异常

```bash
# 手动恢复备份
rm -rf agent-defender/rules/
cp -r rules_backup/stable_v1.0/defender_rules agent-defender/rules/

# 验证恢复
python3 agent-defender/scanner/scan.py <known_safe_skill>
```

---

## 性能优化

### 1. 增量同步

只同步变化的规则:
```python
# 比较哈希值
new_hash = generate_rule_hash(new_rule)
old_hash = get_stored_hash(rule_id)

if new_hash != old_hash:
    sync_rule(new_rule)
```

### 2. 批量同步

累积多轮规则后批量同步:
```bash
# 每 3 轮同步一次
if round_num % 3 == 0:
    sync_rules()
```

### 3. 异步同步

不阻塞主循环:
```python
# 后台同步
threading.Thread(target=sync_rules).start()
```

---

## 总结

✅ **已实现**:
- 自动同步 (每轮迭代后)
- 备份机制 (保留 5 个版本)
- 验证机制 (语法 + 测试)
- 回滚机制 (失败自动回滚)
- 审计日志 (详细变更报告)

✅ **防护生效**:
- agent-defender: Runtime 实时阻断
- agent-dlp: 入口/出口检测
- 从发现到防护：< 10 分钟

✅ **可追溯**:
- 同步历史可查
- 变更报告详细
- 备份可回滚

---

**规则已完全沉淀到防护模块！** 🎉
