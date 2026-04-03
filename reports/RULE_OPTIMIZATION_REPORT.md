# 规则优化报告

**日期**: 2026-04-02  
**优化目标**: 降低误报率至 < 5%

---

## 📊 优化结果对比

| 指标 | 优化前 (4,779 条) | L1 规则 (28 条) | 改进 |
|------|------------------|----------------|------|
| **检测率** | 100.0% | 100.0% | ✅ 保持 |
| **误报率** | 53.65% | 26.7% | ⬇️ -50% |
| **误报数 (FP)** | 8,508 | 4,241 | ⬇️ -50% |
| **漏报数 (FN)** | 0 | 0 | ✅ 保持 |
| **规则数** | 4,779 | 28 | ⬇️ -99.4% |

---

## 📁 规则分级结果

| 级别 | 规则数 | FP 率范围 | 使用场景 |
|------|--------|----------|----------|
| **L1 (高置信度)** | 28 条 | < 10% | 生产环境告警 |
| **L2 (中置信度)** | 4,070 条 | 10-30% | 测试环境/审查 |
| **L3 (低置信度)** | 70 条 | > 30% | 研究/日志 |

---

## ⚠️ 高 FP 规则 (Top 10)

| 规则名称 | 估计 FP 率 | 级别 |
|----------|-----------|------|
| Agent_Curl_Remote_Exec | 60% | L3 |
| Agent_Credential_Theft | 55% | L3 |
| CRED_ShadowFileAccess | 50% | L3 |
| CRED_SSHKeyAccess | 50% | L3 |
| CRED_NetrcFile | 50% | L3 |
| CRED_EnvVarTheft | 50% | L3 |
| CRED_DatabaseCredential | 50% | L3 |
| CRED_ConfigFileParsing | 50% | L3 |
| CRED_BrowserPassword | 50% | L3 |
| CRED_MemoryDump | 50% | L3 |

---

## 🎯 L1 规则列表 (28 条)

```
Impact_Cloud_DeleteBuckets
Impact_Cloud_TerminateInstances
Impact_DataDestruction_DD
Impact_DataDestruction_RMRecursive
Impact_DataDestruction_Shred
Impact_Ransomware_FileEncryption
Impact_Ransomware_RansomNote
Impact_Ransomware_ShadowCopyDeletion
Impact_SystemDisruption_KillProcesses
Impact_SystemDisruption_StopServices
PrivEsc_Linux_Capabilities
PrivEsc_PKEXEC_LocalExploit
PrivEsc_SetUID_Binary
PrivEsc_Sudo_NOPASSWD
PrivEsc_Sudo_ShellEscape
PrivEsc_SudoersMod
PrivEsc_Systemctl_Service
Shell_PrivEsc_SUIDFind
Shell_PrivEsc_SudoFind
Shell_PrivEsc_SudoVim
Shell_Recon_InternalScan
Shell_Recon_PortScan
Shell_Recon_ServiceEnum
Shell_ReverseShell_BashTCP
Shell_ReverseShell_Netcat
Shell_ReverseShell_Perl
Shell_ReverseShell_Python
Malicious_Hidden_Instructions
```

---

## 📋 下一步优化计划

### P0: 进一步降低 FP (目标 < 5%)

1. **细化 L1 规则**
   - 当前 L1 规则 FP 估计 < 10%，实际可能更高
   - 需要针对良性样本集测试，精确测量每条规则的 FP 率
   - 移除 FP > 5% 的规则

2. **添加例外条件**
   - 对高频误报规则添加白名单路径
   - 例如：排除 `/usr/bin/`, `/opt/` 等系统目录

3. **多规则组合**
   - 单条规则触发 → L3 (日志)
   - 2 条相关规则触发 → L2 (审查)
   - 3+ 条规则触发 → L1 (告警)

### P1: Intent Detector 集成

4. **修复导入问题**
   - 错误：`No module named 'intent_detector_v2'`
   - 行动：查找模块位置或重新安装

5. **语义分析辅助**
   - 结合代码上下文判断意图
   - 区分合法运维脚本 vs 恶意攻击

### P2: 持续优化

6. **建立测试流水线**
   - 每次规则更新自动运行 benchmark
   - 监控 FP/FN 趋势

7. **规则版本管理**
   - 记录每次优化的变更
   - 支持回滚到历史版本

---

## 🔧 使用指南

### 生产环境 (低 FP)
```bash
python3 scanner-master/ros-scanner-v2.py <目标路径> \
  --rules rules/optimized/l1_high_confidence.yar
```

### 测试环境 (平衡)
```bash
python3 scanner-master/ros-scanner-v2.py <目标路径> \
  --rules rules/optimized/l1_high_confidence.yar,rules/optimized/l2_medium_confidence.yar
```

### 研究用途 (全量)
```bash
python3 scanner-master/ros-scanner-v2.py <目标路径> \
  --rules scanner-master/output/rules/scanner_master_rules.yar
```

---

**生成时间**: 2026-04-02 07:45  
**优化脚本**: `optimize_rules_v3.py`
