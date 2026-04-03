# ✅ Round 22 P0 - 规则清理完成报告

**日期**: 2026-03-28 20:50  
**状态**: ✅ 文件分离完成，⚠️ 新规则需修复语法错误

---

## 📊 当前状态

### 文件分离结果

| 文件类型 | 文件数 | 状态 | 用途 |
|---------|--------|------|------|
| **原始文件 (.yaml.orig)** | 4 | ✅ 已备份 | 人类可读，保留中文注释 |
| **纯 YARA 规则 (.yar)** | 4 | ⚠️ 需修复 | 用于 benchmark/扫描 |
| **Sigma 规则 (.yaml)** | 2 | ✅ 已分离 | 日志分析工具使用 |
| **工作规则 (scanner_v3_yar)** | 1 | ✅ 正常 | 当前可用规则 |

### 目录结构

```
rules/scanner_v3/yara/
├── scanner_v3_yar                    ✅ 5 条规则，可正常工作
├── privilege_escalation_rules.yaml.orig   ✅ 原始文件 (含中文+Sigma)
├── privilege_escalation_rules.yar         ⚠️ 10 条规则，需修复语法
├── impact_rules.yaml.orig                 ✅ 原始文件
├── impact_rules.yar                       ⚠️ 14 条规则，需修复语法
├── enhanced_shell_rules.yaml.orig         ✅ 原始文件
├── enhanced_shell_rules.yar               ⚠️ 38 条规则，需修复语法
├── enhanced_js_rules.yaml.orig            ✅ 原始文件
├── enhanced_js_rules.yar                  ⚠️ 33 条规则，需修复语法
├── all_rules_combined.yar                 ⚠️ 合并文件，需修复语法
└── sigma/
    ├── sigma_privilege_escalation.yaml    ✅ Sigma 规则
    └── sigma_impact.yaml                  ✅ Sigma 规则
```

---

## 📈 Benchmark 测试结果

### 当前可用规则 (scanner_v3_yar - 5 条)

| 指标 | 值 | 对比初始 |
|------|------|----------|
| **检测率** | 48.4% | +11.6% ✅ |
| **误报率** | 0.0% | -12.3% ✅ |
| **F1 Score** | 65.2% | +12.9% ✅ |

### 按攻击类型

| 攻击类型 | 检测率 | 状态 |
|---------|--------|------|
| obfuscation | 100% | ✅ |
| supply_chain | 100% | ✅ |
| network_call | 100% | ✅ |
| resource_exhaustion | 100% | ✅ |
| code_execution | 50% | ⚠️ |
| privilege_escalation | 50% | ⚠️ (从 0% 提升) |
| data_exfil | 40% | ⚠️ |
| persistence | 15% | 🔴 |
| credential_theft | 0% | 🔴 |

### 按语言

| 语言 | 检测率 | 状态 |
|------|--------|------|
| Python | 84.4% | ✅ |
| JavaScript | 33.3% | ⚠️ |
| Bash | 15% | 🔴 |
| PowerShell | 0% | 🔴 |

---

## ⚠️ 待修复问题

### YARA 语法错误

新创建的 .yar 文件有以下问题：

1. **privilege_escalation_rules.yar** (line 139)
   - 错误：`unterminated regular expression`
   - 原因：正则表达式 `/` 未正确闭合

2. **impact_rules.yar** (line 251)
   - 错误：`unterminated regular expression`
   - 原因：正则表达式格式问题

3. **enhanced_shell_rules.yar** (line 567)
   - 错误：`syntax error, unexpected string count`
   - 原因：字符串引用格式错误

4. **enhanced_js_rules.yar** (line 535)
   - 错误：`syntax error, unexpected string count`
   - 原因：字符串引用格式错误

### 根本原因

原始 YAML 文件中，YARA 规则和 Sigma 规则混在一起，提取过程中：
- 某些正则表达式的 `/` 被误删除
- 某些字符串的引号未正确保留
- 规则块未完整提取

---

## 💡 解决方案

### 方案 A: 手动修复 YARA 规则 (推荐)

逐条检查新规则，修复语法错误：

```bash
# 测试单条规则
yara rules/scanner_v3/yara/privilege_escalation_rules.yar /dev/null

# 定位错误行号
# 手动编辑修复
```

**优点**: 保留所有规则逻辑  
**缺点**: 耗时，需要逐条验证

### 方案 B: 重新编写核心规则

基于原始文件的逻辑，重新编写精简版 YARA 规则：

```yara
// 示例：权限提升核心规则
rule PrivEsc_Sudo_NOPASSWD {
    meta:
        description = "Detects sudo NOPASSWD configuration"
        severity = "critical"
        mitre = "T1548.001"
    strings:
        $s1 = "NOPASSWD"
        $s2 = "/etc/sudoers"
    condition:
        $s1 and $s2
}
```

**优点**: 规则简洁，易于维护  
**缺点**: 需要重新编写

### 方案 C: 使用现有规则逐步扩展

当前 scanner_v3_yar 工作正常，基于此逐步添加新规则：

```bash
# 1. 从原始文件复制 1-2 条规则
# 2. 测试编译
# 3. 运行 benchmark 验证
# 4. 重复直到覆盖所有攻击类型
```

**优点**: 稳定可靠，每次只改动少量  
**缺点**: 进度较慢

---

## 📋 下一步行动

### 今日完成 (P0)

- [x] 备份原始文件 (.yaml.orig)
- [x] 分离 Sigma 规则到 sigma/ 目录
- [x] 提取纯 YARA 规则 (.yar)
- [ ] **修复 .yar 文件语法错误** ← 当前任务
- [ ] 运行 benchmark 验证检测率 ≥60%

### 本周完成 (P1)

- [ ] 增强 Bash 检测 (15% → 50%)
- [ ] 增强 PowerShell 检测 (0% → 50%)
- [ ] 修复 credential_theft (0% → 80%)
- [ ] 整合所有规则到 all_rules.yar

---

## 📚 规则统计

### 原始文件 (保留)

| 文件 | 行数 | 内容 |
|------|------|------|
| privilege_escalation_rules.yaml.orig | 272 行 | 10 YARA + 5 Sigma |
| impact_rules.yaml.orig | 370 行 | 15 YARA + 8 Sigma |
| enhanced_shell_rules.yaml.orig | 462 行 | 40 YARA |
| enhanced_js_rules.yaml.orig | 436 行 | 35 YARA |
| **总计** | **1540 行** | **100+ 规则** |

### 清理后文件

| 文件 | 行数 | 规则数 | 状态 |
|------|------|--------|------|
| scanner_v3_yar | 53 行 | 5 | ✅ 可用 |
| privilege_escalation_rules.yar | 145 行 | 10 | ⚠️ 待修复 |
| impact_rules.yar | 175 行 | 14 | ⚠️ 待修复 |
| enhanced_shell_rules.yar | 405 行 | 38 | ⚠️ 待修复 |
| enhanced_js_rules.yar | 384 行 | 33 | ⚠️ 待修复 |
| **总计** | **1162 行** | **100+** | |

---

## ✅ 成果总结

### 已完成

1. ✅ 保留所有原始文件（中文注释 + Sigma 规则）
2. ✅ 分离 Sigma 规则到独立目录
3. ✅ 提取纯 YARA 规则框架
4. ✅ 检测率从 36.8% 提升到 48.4% (+11.6%)
5. ✅ 误报率从 12.3% 降低到 0%

### 待完成

1. ⚠️ 修复 4 个 .yar 文件的语法错误
2. ⚠️ 整合所有规则并验证
3. ⚠️ 达到检测率 ≥60% 目标

---

**预计完成时间**: 修复语法错误后 1-2 小时  
**建议采用**: 方案 C (逐步扩展)，确保稳定性
