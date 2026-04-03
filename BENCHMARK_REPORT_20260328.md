# Benchmark 测试报告与优化提升方案

**测试时间**: 2026-03-28 17:45  
**测试目录**: `~/.openclaw/workspace/agent-security-skill-scanner-master`  
**测试工具**: `benchmark/benchmark_v2.py`

---

## 📊 测试结果概览

### 核心指标

| 指标 | 当前值 | 目标值 | 差距 |
|------|--------|--------|------|
| **检测率 (Recall)** | 36.8% | ≥95% | ⚠️ -58.2% |
| **误报率 (FPR)** | 12.3% | <3% | ⚠️ +9.3% |
| **精确率 (Precision)** | 90.0% | ≥97% | ⚠️ -7% |
| **F1 Score** | 52.3% | ≥96% | ⚠️ -43.7% |

**结论**: 🔴 **系统性能严重不达标**, 需紧急优化

---

## 🔍 详细分析

### 1. 按攻击类型分析

| 攻击类型 | 检测率 | 状态 |
|---------|--------|------|
| defense_evasion (防御规避) | 66.7% | ⚠️ 待优化 |
| lateral_movement (横向移动) | 66.7% | ⚠️ 待优化 |
| network_call (网络通信) | 66.7% | ⚠️ 待优化 |
| code_execution (代码执行) | 41.7% | 🔴 严重不足 |
| credential_access (凭证访问) | 33.3% | 🔴 严重不足 |
| supply_chain (供应链攻击) | 33.3% | 🔴 严重不足 |
| persistence (持久化) | 33.3% | 🔴 严重不足 |
| data_exfil (数据外传) | 33.3% | 🔴 严重不足 |
| **privilege_escalation (权限提升)** | **0.0%** | 🔴 **完全失效** |
| **impact (影响破坏)** | **0.0%** | 🔴 **完全失效** |

### 2. 按难度分级分析

| 难度 | 检测率 | 样本数 | 分析 |
|------|--------|--------|------|
| Easy | 63.2% | 57 | ⚠️ 简单样本检测率不足 |
| Medium | 36.8% | 57 | 🔴 中等样本漏报严重 |
| Hard | 10.5% | 57 | 🔴 困难样本几乎全部漏报 |

### 3. 按编程语言分析

| 语言 | 恶意样本检出 | 白样本误报 |
|------|-------------|-----------|
| Python | 48/81 (59.3%) | 5/20 (25.0%) |
| PowerShell | 9/27 (33.3%) | 0/0 (0.0%) |
| JavaScript | 3/27 (11.1%) | 0/20 (0.0%) |
| **Bash** | **3/36 (8.3%)** | 2/17 (11.8%) |

---

## 🚨 核心问题诊断

### 问题 1: 规则覆盖率严重不足
**现象**: 权限提升 (0%)、影响破坏 (0%) 完全未检出  
**原因**: 
- 缺少针对 `sudo`、`pkexec`、`systemctl` 等提权命令的 YARA/Sigma 规则
- 缺少针对 `rm -rf`、`:(){:|:&};:` 等破坏性命令的检测规则

### 问题 2: Bash 脚本检测能力极弱
**现象**: Bash 检出率仅 8.3%  
**原因**:
- shell_yara_rules.yaml 仅 6KB, 规则数量不足
- 缺少对 bash 特性 (eval, base64 解码，进程替换) 的检测

### 问题 3: JavaScript 检测几乎空白
**现象**: JS 检出率仅 11.1%  
**原因**:
- js_yara_rules.yaml 规则过于简单
- 未覆盖 Node.js 特有 API (child_process, fs, http)

### 问题 4: 误报率偏高
**现象**: 白样本误报率 12.3%  
**原因**:
- 规则过于宽泛 (如匹配 `eval` 但忽略上下文)
- 缺少白名单机制
- 未使用多级规则体系 (L1/L2/L3)

### 问题 5: 扫描器集成问题
**现象**: benchmark 使用的是 scanner/integration_scanner.py  
**原因**:
- 未使用 expert_mode 的完整检测引擎
- 未启用 Runtime 行为分析
- 未使用 DLP 规则和数据流分析

---

## 💡 优化提升方案

### 阶段一：紧急修复 (P0 - 1-2 天)

#### 1.1 补充缺失的攻击类型规则
```bash
# 创建权限提升规则
mkdir -p rules/scanner_v3/privilege_escalation
# 创建影响破坏规则
mkdir -p rules/scanner_v3/impact
```

**规则示例** (privilege_escalation_001.yaml):
```yaml
rule_id: PRIVESC-001
name: Sudo NOPASSWD Detection
severity: critical
patterns:
  - regex: 'sudo\s+(-S|--stdin)\s+.*NOPASSWD'
  - keyword: ['visudo', '/etc/sudoers', 'setuid', 'setgid']
mitre: T1548.001
```

#### 1.2 增强 Bash 检测规则
**目标**: 8.3% → 60%+

新增检测点:
- `eval $(...)` / `$(...)` 命令替换
- `base64 -d` / `openssl` 解码
- `bash -c` / `sh -c` 动态执行
- 进程替换 `<(...)`
- 反向 Shell 特征 (`/dev/tcp/`, `nc -e`)

#### 1.3 增强 JavaScript 检测规则
**目标**: 11.1% → 60%+

新增检测点:
- `child_process.exec/spawn`
- `fs.writeFileSync` + 敏感路径
- `http/https` 外传请求
- `vm.runInContext` 代码执行
- `Buffer.from()` Base64 解码

---

### 阶段二：架构优化 (P1 - 3-5 天)

#### 2.1 引入三级规则体系
参考 Round 11 优化方案:

| 级别 | 规则数 | 检测内容 | 延迟目标 |
|------|--------|---------|---------|
| **L1** | 50 | IOC 快速匹配 (哈希/域名/IP) | <1ms |
| **L2** | 100 | 行为模式 (API 调用/命令组合) | <10ms |
| **L3** | 50 | 深度语义分析 (AST/数据流) | <100ms |

#### 2.2 集成 Expert Mode 完整引擎
当前 benchmark 仅使用 YARA 规则，需集成:
- ✅ Runtime 行为分析器
- ✅ DLP 数据流检测
- ✅ Sigma 日志规则
- ✅ IOC 威胁情报

**实施方案**:
```python
# 修改 benchmark_v2.py 调用 expert_mode scanner
from expert_mode.scanner import SecurityScanner

scanner = SecurityScanner(
    enable_yara=True,
    enable_runtime=True,
    enable_dlp=True,
    enable_sigma=True
)
```

#### 2.3 添加白名单机制
```yaml
# config/whitelist.yaml
whitelist:
  paths:
    - /usr/bin/*
    - /bin/*
    - node_modules/**
  hashes:
    - sha256:abc123...  # 已知良性脚本
  patterns:
    - '#!/bin/bash\necho "Hello"'  # 简单 Hello World
```

---

### 阶段三：高级优化 (P2 - 1-2 周)

#### 3.1 AST 静态分析引擎
**目标**: 检测混淆代码 (Round 16)

**功能**:
- Python AST 解析 → 识别 `eval(exec(base64))` 模式
- Bash AST 解析 → 识别动态命令构建
- JavaScript AST 解析 → 识别混淆器输出

**工具集成**:
```bash
pip install astor black js2py bashparse
```

#### 3.2 机器学习增强
**方案**:
- 使用 CodeBERT 提取代码语义特征
- 训练二分类模型 (恶意/良性)
- 与传统规则引擎融合 (加权投票)

#### 3.3 持续学习闭环
```
样本生成 → 扫描检测 → 失败分析 → 规则优化 → 验证测试
    ↑                                          │
    └──────────────────────────────────────────┘
```

**自动化脚本**:
```bash
#!/bin/bash
# auto_optimize.sh
python3 benchmark_v2.py --run --output results.json
python3 analyze_failures.py results.json
python3 generate_rules.py failures.json
python3 validate_rules.py new_rules.yaml
```

---

## 📈 预期效果

### 优化后指标预测

| 阶段 | 检测率 | 误报率 | F1 Score |
|------|--------|--------|----------|
| **当前** | 36.8% | 12.3% | 52.3% |
| 阶段一后 | 65% | 10% | 73% |
| 阶段二后 | 85% | 5% | 89% |
| 阶段三后 | ≥95% | <3% | ≥96% |

### 各攻击类型目标

| 攻击类型 | 当前 | 阶段一目标 | 最终目标 |
|---------|------|-----------|---------|
| privilege_escalation | 0% | 50% | ≥95% |
| impact | 0% | 50% | ≥95% |
| bash | 8.3% | 50% | ≥90% |
| javascript | 11.1% | 50% | ≥90% |
| code_execution | 41.7% | 70% | ≥95% |
| 其他 | 33-67% | 70% | ≥95% |

---

## 🎯 立即执行任务清单

### 今日任务 (P0)
- [ ] 创建 `rules/scanner_v3/privilege_escalation/` 目录
- [ ] 创建 `rules/scanner_v3/impact/` 目录
- [ ] 编写 10 条提权检测规则
- [ ] 编写 10 条破坏命令检测规则
- [ ] 增强 shell_yara_rules.yaml (新增 30 条规则)
- [ ] 增强 js_yara_rules.yaml (新增 20 条规则)
- [ ] 重新运行 benchmark 验证

### 本周任务 (P1)
- [ ] 实现三级规则体系
- [ ] 集成 expert_mode 完整引擎到 benchmark
- [ ] 添加白名单机制
- [ ] 误报率降至 <8%
- [ ] 检测率提升至 >65%

### 下周任务 (P2)
- [ ] AST 静态分析引擎原型
- [ ] 持续学习自动化脚本
- [ ] 检测率 >85%, 误报率 <5%

---

## 📚 参考资料

1. **MITRE ATT&CK**: https://attack.mitre.org/
2. **Sigma HQ 规则库**: https://github.com/SigmaHQ/sigma
3. **YARA 规则编写指南**: https://yara.readthedocs.io/
4. **Round 11 优化报告**: `~/ai-work/OPTIMIZATION_PLAN.md`
5. **灵顺 V5 框架**: `~/skills/agent-security-skill-scanner/expert_mode/README.md`

---

**生成时间**: 2026-03-28 17:46  
**下次测试**: 完成 P0 任务后重新运行 `python3 benchmark/benchmark_v2.py --run`
