# 🔬 Round 10 - 样本扩展与自动化测试

**日期**: 2026-03-22  
**目标**: 扩展样本库 + 自动化测试框架

---

## 🎯 目标

| 指标 | 当前值 | 目标值 | 状态 |
|------|--------|--------|------|
| 样本总数 | 13 | ≥40 | 🔴 待完成 |
| 恶意样本 | 10 | ≥30 | 🔴 待完成 |
| 白样本 | 3 | ≥10 | 🔴 待完成 |
| 每类变体 | 1 | 3-4 | 🔴 待完成 |
| 自动化测试 | ❌ | ✅ | 🔴 待完成 |

---

## 📋 任务清单

### 1. 样本扩展 (Variant Generator)

**目标**: 每类威胁类型生成 3-4 个变体样本

| 威胁类型 | 当前 | 目标 | 新增 |
|----------|------|------|------|
| tool_poisoning | 1 | 4 | +3 |
| remote_load | 1 | 4 | +3 |
| data_exfil | 1 | 4 | +3 |
| prompt_injection | 1 | 4 | +3 |
| resource_exhaustion | 1 | 4 | +3 |
| memory_pollution | 1 | 4 | +3 |
| supply_chain | 1 | 3 | +2 |
| credential_theft | 1 | 3 | +2 |
| persistence | 1 | 3 | +2 |
| evasion | 1 | 3 | +2 |
| **恶意小计** | **10** | **36** | **+26** |

| 白样本类型 | 当前 | 目标 | 新增 |
|------------|------|------|------|
| normal_script | 1 | 4 | +3 |
| common_pattern | 1 | 4 | +3 |
| false_prone | 1 | 4 | +3 |
| **白样本小计** | **3** | **12** | **+9** |

**总计**: 13 → 48 个样本 (+35)

---

### 2. 变体生成策略

#### 恶意样本变体维度

| 维度 | 变体方法 | 示例 |
|------|----------|------|
| **变量名** | 随机化/混淆 | `cmd` → `command` → `exec_str` |
| **路径** | 改变文件路径 | `/tmp/x.sh` → `/var/tmp/y.sh` |
| **编码** | Base64/Hex/Rot13 | `curl | bash` → `echo XXX \| base64 -d \| bash` |
| **协议** | HTTP/HTTPS/DNS | `http://` → `https://` → `dns://` |
| **触发方式** | 不同 Hook | `postinstall` → `preinstall` → `prepare` |
| **执行方式** | 不同 API | `exec()` → `spawn()` → `execFile()` |

#### 白样本变体维度

| 维度 | 变体方法 | 示例 |
|------|----------|------|
| **功能** | 不同场景 | CSV 转 JSON → JSON 转 YAML |
| **库** | 不同依赖 | `requests` → `urllib` → `httpx` |
| **风格** | 不同写法 | 同步 → 异步 → 函数式 |

---

### 3. 自动化测试框架

**文件**: `round10/auto_test.py`

#### 功能

```python
# 1. 批量测试所有样本
python3 auto_test.py --all

# 2. 测试指定类型
python3 auto_test.py --attack-type tool_poisoning

# 3. 测试白样本 (误报率)
python3 auto_test.py --benign

# 4. 生成对比报告
python3 auto_test.py --compare-with-round8
```

#### 输出

| 文件 | 内容 |
|------|------|
| `round10/results/test_results.json` | 原始测试结果 |
| `round10/results/detection_stats.json` | 检测率统计 |
| `round10/reports/ROUND10_REPORT.md` | Markdown 报告 |
| `round10/reports/ROUND10_CHARTS.json` | 图表数据 |

---

### 4. 质量指标

| 指标 | 目标 | 验证方法 |
|------|------|----------|
| 检测率 | ≥95% | 恶意样本触发规则 |
| 误报率 | <5% | 白样本不触发规则 |
| 变体多样性 | ≥3 维度 | 检查 metadata |
| 测试覆盖率 | 100% | 所有样本都有 test_cases |

---

## 📁 文件结构

```
expert_mode/
├── ROUND10_DESIGN.md              # 本设计文档
├── round10/
│   ├── variant_generator.py       # 变体生成器
│   ├── auto_test.py               # 自动化测试
│   ├── results/                   # 测试结果
│   │   ├── test_results.json
│   │   └── detection_stats.json
│   └── reports/                   # 报告
│       ├── ROUND10_REPORT.md
│       └── ROUND10_CHARTS.json
└── samples/
    ├── malicious/                 # 36 个恶意样本
    │   ├── MAL-TOO-*/ (4 个)
    │   ├── MAL-RLO-*/ (4 个)
    │   └── ...
    └── benign/                    # 12 个白样本
        ├── BEN-NOR-*/ (4 个)
        └── ...
```

---

## 🚀 执行步骤

### Step 1: 创建变体生成器
```bash
cd ~/.openclaw/workspace/skills/agent-security-skill-scanner/expert_mode
python3 round10/variant_generator.py --all --summary
```

### Step 2: 验证样本质量
```bash
# 检查样本完整性
python3 round10/validate_samples.py
```

### Step 3: 执行自动化测试
```bash
python3 round10/auto_test.py --all --output-results
```

### Step 4: 生成报告
```bash
python3 round10/generate_report.py --compare-round8
```

---

## 📊 预期成果

| 成果 | 交付物 |
|------|--------|
| **样本库** | 48 个样本 (36 恶意 +12 白样本) |
| **变体生成器** | `variant_generator.py` |
| **自动化测试** | `auto_test.py` |
| **测试报告** | `ROUND10_REPORT.md` |
| **对比分析** | Round 8 vs Round 10 指标对比 |

---

## ✅ 完成标准

- [ ] 48 个样本全部生成并验证
- [ ] 每个样本有完整 metadata.json
- [ ] samples_index.json 更新
- [ ] 自动化测试通过率 ≥95%
- [ ] 误报率 <5%
- [ ] 报告生成完成

---

**位置**: `~/.openclaw/workspace/skills/agent-security-skill-scanner/expert_mode/`  
**下一轮**: Round 11 - 检测规则优化 (基于 Round 10 测试结果)
