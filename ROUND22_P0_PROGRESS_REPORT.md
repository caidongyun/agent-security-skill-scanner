# Round 22 - P0 规则补充进度报告

**日期**: 2026-03-28  
**目标**: 补充缺失的攻击类型规则，提升检测率从 36.8% → 60%+  
**状态**: 🟡 进行中

---

## 📊 当前测试结果

### Benchmark 对比

| 测试 | 规则数 | 检测率 | 误报率 | F1 Score |
|------|--------|--------|--------|----------|
| **初始 (v2)** | 5 | 36.8% | 12.3% | 52.3% |
| **当前 (v3)** | 9 | 48.4% | 0.0% | 65.2% |
| **目标** | 100+ | ≥60% | <10% | ≥75% |

### 按攻击类型检测率

| 攻击类型 | 初始 | 当前 | 提升 | 目标 |
|---------|------|------|------|------|
| supply_chain | 33.3% | 100% | +66.7% | ✅ |
| network_call | 66.7% | 100% | +33.3% | ✅ |
| resource_exhaustion | - | 100% | - | ✅ |
| obfuscation | - | 100% | - | ✅ |
| code_execution | 41.7% | 50% | +8.3% | ⚠️ |
| privilege_escalation | 0% | 50% | +50% | ⚠️ |
| data_exfil | 33.3% | 40% | +6.7% | ⚠️ |
| persistence | 33.3% | 15% | -18.3% | 🔴 |
| credential_theft | 33.3% | 0% | -33.3% | 🔴 |

### 按语言检测率

| 语言 | 初始 | 当前 | 提升 | 目标 |
|------|------|------|------|------|
| Python | 59.3% | 84.4% | +25.1% | ✅ |
| JavaScript | 11.1% | 33.3% | +22.2% | ⚠️ |
| Bash | 8.3% | 15% | +6.7% | 🔴 |
| PowerShell | - | 0% | - | 🔴 |

---

## ✅ 已完成工作

### 1. 创建新规则文件 (4 个)

| 文件 | 规则数 | 状态 |
|------|--------|------|
| `privilege_escalation_rules.yaml` | 10 YARA + 5 Sigma | ✅ 已创建 |
| `impact_rules.yaml` | 15 YARA + 8 Sigma | ✅ 已创建 |
| `enhanced_shell_rules.yaml` | 40 YARA | ✅ 已创建 |
| `enhanced_js_rules.yaml` | 35 YARA | ✅ 已创建 |
| **总计** | **100+ 条规则** | |

### 2. 创建 Benchmark v3 测试工具

- **文件**: `benchmark/benchmark_v3.py`
- **功能**: 使用完整 YARA 规则目录进行扫描
- **优势**: 支持批量加载多个规则文件

### 3. 规则整合

- ✅ 创建了 scanner_v3_yar (9 条规则，纯 YARA 格式)
- ⚠️ 新规则文件需要清理 Sigma 规则和中文注释

---

## 🚨 遇到的问题

### 问题 1: YARA 不支持非 ASCII 字符

**现象**: YARA 编译失败，报错 "non-ascii character"  
**原因**: 规则文件包含中文注释  
**解决方案**: 
- 方案 A: 将所有规则转换为纯英文注释
- 方案 B: 分离 YARA 规则和 Sigma 规则到不同文件

### 问题 2: YARA 和 Sigma 格式混合

**现象**: YARA 编译失败，报错 "unterminated regular expression"  
**原因**: 规则文件同时包含 YARA 规则和 Sigma 规则 (YAML 格式)  
**解决方案**: 
- 创建纯 YARA 规则文件 (`*.yar`)
- 创建纯 Sigma 规则文件 (`*.yaml`)
- 修改扫描器分别加载

---

## 📋 待完成任务

### P0 - 紧急 (今日完成)

- [ ] 清理规则文件中的中文注释
- [ ] 分离 YARA 和 Sigma 规则
- [ ] 创建纯 YARA 规则整合文件 (`all_rules.yar`)
- [ ] 重新运行 benchmark 验证检测率 ≥60%

### P1 - 高优先级 (本周完成)

- [ ] 增强 Bash 检测规则 (当前 15% → 目标 50%)
- [ ] 增强 PowerShell 检测规则 (当前 0% → 目标 50%)
- [ ] 修复 credential_theft 检测 (当前 0% → 目标 80%)
- [ ] 修复 persistence 检测 (当前 15% → 目标 70%)

### P2 - 中优先级 (下周完成)

- [ ] 集成 Expert Mode 完整引擎
- [ ] 添加白名单机制
- [ ] 优化误报率 (<5%)

---

## 💡 优化建议

### 短期 (1-2 天)

1. **规则格式标准化**
   ```bash
   # 创建纯 YARA 规则文件
   cat rules/scanner_v3/yara/*.yar > rules/scanner_v3/all_rules.yar
   
   # 创建纯 Sigma 规则文件
   cat rules/scanner_v3/sigma/*.yaml > rules/scanner_v3/all_sigma.yaml
   ```

2. **快速验证**
   ```bash
   python3 benchmark/benchmark_v3.py --rules rules/scanner_v3/all_rules.yar
   ```

3. **规则调试**
   ```bash
   # 测试单个规则文件
   yara rules/scanner_v3/yara/privilege_escalation_rules.yar benchmark_samples/malicious/bash/*
   ```

### 中期 (3-5 天)

1. **增强 Bash 检测**
   - 添加更多 bash 特有模式 (eval, base64, 反向 shell)
   - 增加进程替换检测
   - 增强命令注入规则

2. **增强 PowerShell 检测**
   - 添加 PowerShell 特有 cmdlet 检测
   - 增加 Invoke-Expression 检测
   - 增强编码绕过检测

3. **集成 Runtime 检测**
   - 使用 expert_mode 的完整扫描器
   - 添加行为分析
   - 集成 DLP 规则

### 长期 (1-2 周)

1. **AST 静态分析**
   - Python AST 解析
   - JavaScript AST 解析
   - 检测混淆代码

2. **机器学习增强**
   - CodeBERT 特征提取
   - 训练二分类模型
   - 与传统规则融合

---

## 📈 预期效果

### 阶段目标

| 阶段 | 规则数 | 检测率 | 误报率 | F1 Score |
|------|--------|--------|--------|----------|
| **P0 完成后** | 100+ | 60% | <10% | 75% |
| **P1 完成后** | 150+ | 75% | <7% | 85% |
| **P2 完成后** | 200+ | 85% | <5% | 90% |
| **最终目标** | 300+ | ≥95% | <3% | ≥96% |

### 各攻击类型目标

| 攻击类型 | 当前 | P0 目标 | P1 目标 | 最终目标 |
|---------|------|--------|--------|---------|
| privilege_escalation | 50% | 70% | 85% | ≥95% |
| credential_theft | 0% | 50% | 80% | ≥95% |
| persistence | 15% | 50% | 75% | ≥95% |
| bash | 15% | 40% | 60% | ≥90% |
| powershell | 0% | 30% | 60% | ≥90% |

---

## 🔧 技术细节

### YARA 规则格式要求

```yara
rule Rule_Name {
    meta:
        description = "English description only"
        author = "Author Name"
        severity = "critical"
        mitre = "T1059"
    strings:
        $pattern1 = /regex_pattern/
        $pattern2 = "string literal"
        $pattern3 = { hex pattern }
    condition:
        $pattern1 and $pattern2
}
```

### Sigma 规则格式要求

```yaml
title: Rule Title
status: experimental
author: Author Name
logsource:
    category: process_creation
    product: linux
detection:
    selection:
        CommandLine|contains:
            - 'pattern1'
            - 'pattern2'
    condition: selection
level: critical
tags:
    - attack.t1059
```

### 规则编写最佳实践

1. **避免非 ASCII 字符** - YARA 只支持 ASCII
2. **使用有意义的规则名** - 遵循 `Category_Technique_Detail` 格式
3. **添加完整元数据** - MITRE ATT&CK ID, 严重程度，作者
4. **测试规则** - 使用 benchmark 验证检测率和误报率
5. **避免过度匹配** - 平衡特异性和敏感性

---

## 📚 参考资料

1. **YARA 文档**: https://yara.readthedocs.io/
2. **Sigma HQ**: https://github.com/SigmaHQ/sigma
3. **MITRE ATT&CK**: https://attack.mitre.org/
4. **GTFOBins**: https://gtfobins.github.io/ (提权技术参考)
5. **Round 11 优化报告**: `~/ai-work/OPTIMIZATION_PLAN.md`

---

**下一步行动**: 清理规则文件格式，重新运行 benchmark 验证

**预计完成时间**: 2026-03-28 晚间
