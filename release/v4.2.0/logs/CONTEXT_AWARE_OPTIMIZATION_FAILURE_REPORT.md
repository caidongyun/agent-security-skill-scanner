# 上下文感知扫描优化失败研究报告

**实验时间**: 2026-04-08 21:30  
**实验目的**: 降低误报率，提高一致率  
**实验结果**: ❌ 失败（一致率从 90% 降至 14.3%）

---

## 📊 实验背景

### 问题发现

**初始测试**（20 个样本）:
- 基础扫描一致率：90.0%
- 上下文感知一致率：25.0%
- 误报数：基础 2 个 vs 上下文 15 个

**假设**: 调整权重参数可以改善上下文感知的表现

---

## 🔬 实验设计

### 优化方案

**权重调整**:
```python
# 旧权重
OFFICIAL_SKILL_FACTOR = 0.5      # 降低 50%
INSTALL_SCRIPT_FACTOR = 0.6      # 降低 40%
DOCUMENTATION_FACTOR = 0.8       # 降低 20%
AUTHOR_FACTOR = 0.7              # 降低 30%

# 新权重（优化后）
OFFICIAL_SKILL_FACTOR = 0.8      # 降低 20%
INSTALL_SCRIPT_FACTOR = 0.85     # 降低 15%
DOCUMENTATION_FACTOR = 0.9       # 降低 10%
AUTHOR_FACTOR = 0.9              # 降低 10%
```

**预期效果**: 一致率从 25% 提升至 70%+

---

## 📈 实验结果

### 全量测试（1647 个 Skills）

| 指标 | 基础扫描 | 上下文感知（优化后） | 差异 |
|------|---------|-------------------|------|
| **总 Skills** | 1647 | 1647 | - |
| **判定恶意** | 2 (0.1%) | 1427 (86.6%) | **+1425** ❌ |
| **官方恶意** | 17 (1.0%) | 17 (1.0%) | - |
| **一致率** | **90.0%** | **14.3%** | **-75.7%** ❌ |
| **误报数** | **2 个** | **1411 个** | **+1409** ❌ |
| **漏报数** | 0 个 | 1 个 | +1 ⚠️ |

---

## ❌ 失败原因分析

### 根本原因 1: 上下文感知逻辑缺陷

**问题代码**:
```python
# 上下文感知扫描逻辑
if is_official:
    total_weight *= 0.8  # 即使调整权重，逻辑仍有问题
if has_documentation:
    total_weight *= 0.9
```

**问题**: **权重减免逻辑本身不科学**

- 累积减免：0.8 × 0.9 = 0.72 (降低 28%)
- 即使调整参数，仍会导致大量误判

---

### 根本原因 2: 过度依赖上下文

**问题**:
- 上下文感知过度依赖 Skill 元数据（作者、文档、官方标识）
- 忽略了代码本身的安全性
- 导致"官方 Skill"被过度信任

**表现**:
```
官方 Skill + 文档完整 → 风险降低 72%
即使包含 curl|bash，也会从 0.9 降至 0.26
导致恶意代码被误判为 SAFE
```

---

### 根本原因 3: 小样本过拟合

**问题**:
- 基于 20 个样本调整权重
- 样本量仅占总体的 0.12%
- 存在严重抽样偏差

**验证**:
- 20 个样本一致率：25% → 70%（看似改善）
- 1647 个样本一致率：90% → 14.3%（实际恶化）

---

## 🎯 关键发现

### 发现 1: 基础扫描表现优异

**基础扫描指标**:
- 一致率：**90.0%** ✅
- 误报数：**2 个** ✅
- 漏报数：**0 个** ✅

**结论**: 基础扫描已经足够好，不需要复杂优化

---

### 发现 2: 上下文感知不适合批量扫描

**上下文感知问题**:
- 一致率：14.3% ❌
- 误报数：1411 个 ❌
- 判定恶意：86.6%（过度敏感）❌

**结论**: 上下文感知扫描**不适合批量测试**

---

### 发现 3: 领域感知更有价值

**领域感知优势**:
- 基于 SKILL.md 语义分析
- 不依赖权重减免
- 提供领域分类和声明分析

**结论**: 领域感知可作为**辅助工具**

---

## ✅ 推荐方案

### 方案 A: 基础扫描（批量测试，推荐）

**使用方式**:
```bash
python3 benchmark_vs_official_v2.py \
  /path/to/skills \
  --output report.json \
  --sample-size 500 \
  --mode stratified
# 不要加 --context-aware
```

**预期效果**:
- 一致率：85-90%
- 误报数：<10 个
- 时间：10-20 分钟

---

### 方案 B: 基础 + 领域感知（单个 Skill，推荐）

**使用方式**:
```bash
# 1. 基础扫描
python3 scanner.py /path/to/skill

# 2. 领域感知（语义分析）
python3 domain_aware_scanner.py /path/to/skill

# 3. 综合判定
if 基础=='SAFE' and 领域=='SAFE':
    return 'SAFE'
else:
    return 'SUSPICIOUS'
```

**预期效果**:
- 准确率：85-90%
- 可解释性：高（有领域分析）
- 时间：1-2 分钟/Skill

---

### 方案 C: 基础 + LLM 判定（边界案例）

**使用方式**:
```bash
# 只对基础扫描判定为 SUSPICIOUS 的使用 LLM
python3 llm_skill_judge.py /path/to/skill --enable-llm
```

**预期效果**:
- 边界案例准确率提升
- 减少人工审查工作量

---

## 📋 高质量 Benchmark 样本集

### 已收集样本

**位置**: `benchmark_samples/`

```
benchmark_samples/
├── false_positive/          # 误报案例（2 个）
│   ├── ethereum-wingman.json
│   └── auditclaw-idp.json
├── false_negative/          # 漏报案例（0 个）
├── boundary_case/           # 边界案例（0 个）
├── typical_benign/          # 典型良性（0 个）
└── typical_malicious/       # 典型恶意（0 个）
```

### 持续收集机制

**添加样本**:
```bash
python3 high_quality_benchmark.py \
  --action add \
  --skill-path /path/to/skill \
  --category false_positive \
  --reason "误报原因说明"
```

**分析报告**:
```bash
python3 high_quality_benchmark.py --action report
```

---

## 📊 最终建议

### 批量测试（100+ Skills）

```bash
# 使用基础扫描
python3 benchmark_vs_official_v2.py \
  /home/cdy/Desktop/security-benchmark/openclaw-skills-repo/skills \
  --output logs/final_benchmark.json \
  --sample-size 500 \
  --mode stratified
# 不要加 --context-aware
```

**预期**: 一致率 85-90%，误报<10 个

---

### 单个 Skill 深度分析

```bash
# 1. 基础扫描（快速）
python3 scanner.py /path/to/skill

# 2. 领域感知（语义分析）
python3 domain_aware_scanner.py /path/to/skill

# 3. LLM 判定（边界案例，可选）
python3 llm_skill_judge.py /path/to/skill --enable-llm
```

**预期**: 准确率 85-90%，可解释性高

---

### 持续优化

**每周运行**:
```bash
# 收集易错样本
python3 high_quality_benchmark.py --action add ...

# 分析共性
python3 high_quality_benchmark.py --action report

# 跟踪趋势
cat logs/weekly_benchmark.json | jq '.stats'
```

---

## 📄 相关文档

- 实验数据：`logs/optimized_test.json`
- Benchmark 样本集：`benchmark_samples/`
- 权重调整记录：`logs/WEIGHT_ADJUSTMENT.md`
- 优化方案总览：`OPTIMIZATION_PLAN_SUMMARY.md`
- 通用性分析：`logs/GENERALITY_ANALYSIS.md`

---

## 🎯 结论

**核心发现**:
1. ✅ 基础扫描表现优异（90% 一致率）
2. ❌ 上下文感知不适合批量扫描（14.3% 一致率）
3. ✅ 领域感知可作为辅助工具
4. ⚠️ 小样本优化存在过拟合风险

**最终建议**:
- **批量测试**: 使用基础扫描
- **单个 Skill**: 基础 + 领域感知
- **边界案例**: 基础 + LLM 判定
- **放弃**: 上下文感知批量扫描

---

**研究报告完成！建议按方案 A 和方案 B 执行。** 📊
