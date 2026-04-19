# 优化方案通用性分析

**时间**: 2026-04-08 21:25  
**问题**: 基于 20 个样本的优化，通用性如何？

---

## ⚠️ 当前问题

### 测试样本不足

**当前测试**:
- 样本数：20 个 Skills
- 占比：20/17,000 = **0.12%**
- 抽样方式：随机

**风险**:
- 样本太少，可能存在**抽样偏差**
- 优化可能**过拟合**这 20 个样本
- 在全量数据上表现可能不同

---

## 📊 通用性验证方案

### 方案 1: 多批次验证（推荐）

**思路**: 多次抽样，验证稳定性

**步骤**:
```bash
# 第 1 批：随机 100 个
python3 benchmark_vs_official_v2.py /path/to/skills \
  --output logs/batch1.json --sample-size 100 --mode random

# 第 2 批：随机 100 个
python3 benchmark_vs_official_v2.py /path/to/skills \
  --output logs/batch2.json --sample-size 100 --mode random

# 第 3 批：分层 100 个
python3 benchmark_vs_official_v2.py /path/to/skills \
  --output logs/batch3.json --sample-size 100 --mode stratified

# 对比 3 批结果
echo "批次 1 一致率：" $(cat logs/batch1.json | jq '.analysis.agreement_rate')
echo "批次 2 一致率：" $(cat logs/batch2.json | jq '.analysis.agreement_rate')
echo "批次 3 一致率：" $(cat logs/batch3.json | jq '.analysis.agreement_rate')
```

**判断标准**:
- 3 批一致率差异 <5% → **通用性好** ✅
- 3 批一致率差异 >15% → **通用性差** ❌

**时间**: 30 分钟

---

### 方案 2: 渐进式验证（科学）

**思路**: 从小到大，验证收敛性

**步骤**:
```bash
# 10 个样本
python3 benchmark_vs_official_v2.py /path/to/skills \
  --output logs/n10.json --sample-size 10

# 50 个样本
python3 benchmark_vs_official_v2.py /path/to/skills \
  --output logs/n50.json --sample-size 50

# 100 个样本
python3 benchmark_vs_official_v2.py /path/to/skills \
  --output logs/n100.json --sample-size 100

# 500 个样本
python3 benchmark_vs_official_v2.py /path/to/skills \
  --output logs/n500.json --sample-size 500

# 观察一致率收敛
echo "n=10:  $(cat logs/n10.json | jq '.analysis.agreement_rate')"
echo "n=50:  $(cat logs/n50.json | jq '.analysis.agreement_rate')"
echo "n=100: $(cat logs/n100.json | jq '.analysis.agreement_rate')"
echo "n=500: $(cat logs/n500.json | jq '.analysis.agreement_rate')"
```

**判断标准**:
- n≥100 时一致率稳定（波动<3%）→ **样本充足** ✅
- n≥500 时一致率仍在波动 → **需要更多样本** ⚠️

**时间**: 1 小时

---

### 方案 3: 领域分层验证（最科学）

**思路**: 按领域分层，验证各领域表现

**步骤**:
```bash
# 1. 先按领域分类
python3 domain_aware_scanner.py /path/to/skills \
  --output logs/domain_classification.json

# 2. 每个领域抽样测试
# 安全审计类 (30 个)
python3 benchmark_vs_official_v2.py /path/to/skills/security-* \
  --output logs/domain_security.json --sample-size 30

# 开发工具类 (30 个)
python3 benchmark_vs_official_v2.py /path/to/skills/dev-* \
  --output logs/domain_dev.json --sample-size 30

# 自动化类 (30 个)
python3 benchmark_vs_official_v2.py /path/to/skills/auto-* \
  --output logs/domain_auto.json --sample-size 30

# 3. 对比各领域表现
echo "安全审计一致率：" $(cat logs/domain_security.json | jq '.analysis.agreement_rate')
echo "开发工具一致率：" $(cat logs/domain_dev.json | jq '.analysis.agreement_rate')
echo "自动化一致率：" $(cat logs/domain_auto.json | jq '.analysis.agreement_rate')
```

**判断标准**:
- 各领域一致率差异 <10% → **通用性好** ✅
- 某些领域一致率 <60% → **需要领域特定优化** ⚠️

**时间**: 1.5 小时

---

## 🎯 推荐验证流程

### 阶段 1: 快速验证（30 分钟）

```bash
# 3 批次验证
for i in 1 2 3; do
  python3 benchmark_vs_official_v2.py /path/to/skills \
    --output logs/verify_batch${i}.json \
    --sample-size 100 --mode random
done

# 对比结果
echo "=== 3 批次对比 ==="
for i in 1 2 3; do
  echo "批次$i: $(cat logs/verify_batch${i}.json | jq '.analysis.agreement_rate')%"
done
```

**目标**: 验证稳定性

---

### 阶段 2: 渐进验证（1 小时）

```bash
# 渐进样本验证
for n in 50 100 200 500; do
  python3 benchmark_vs_official_v2.py /path/to/skills \
    --output logs/verify_n${n}.json \
    --sample-size $n --mode stratified
done

# 观察收敛
echo "=== 样本数 vs 一致率 ==="
for n in 50 100 200 500; do
  echo "n=$n: $(cat logs/verify_n${n}.json | jq '.analysis.agreement_rate')%"
done
```

**目标**: 验证样本充足性

---

### 阶段 3: 领域验证（2 小时）

```bash
# 按领域验证
python3 domain_aware_scanner.py /path/to/skills --output logs/domains.json

# 提取各领域 Skills
# ...（需要脚本支持）

# 分别测试
```

**目标**: 验证领域通用性

---

## 📊 通用性评估标准

### 样本量要求

| 总 Skills 数 | 最小样本数 | 置信度 |
|------------|-----------|--------|
| <100 | 30 | 90% |
| 100-1000 | 100 | 95% |
| 1000-10000 | 300 | 95% |
| >10000 | 500 | 99% |

**当前**: 17,000 Skills → **需要至少 500 个样本**

---

### 一致性要求

| 指标 | 优秀 | 良好 | 可接受 |
|------|------|------|--------|
| **批次稳定性** | <3% | <5% | <10% |
| **样本收敛** | n≥100 | n≥200 | n≥500 |
| **领域差异** | <5% | <10% | <15% |

---

## ⚠️ 当前优化的通用性风险

### 风险 1: 样本过少

**当前**: 20 个样本  
**需要**: 500 个样本  
**风险**: **高** ❌

---

### 风险 2: 抽样偏差

**当前**: 随机抽样  
**问题**: 可能集中在某些领域  
**风险**: **中** ⚠️

---

### 风险 3: 过拟合

**当前**: 基于 20 个样本调整权重  
**风险**: 在这 20 个上表现好，在其他样本上差  
**风险**: **高** ❌

---

## ✅ 建议行动方案

### 立即执行（验证通用性）

```bash
# 1. 3 批次验证（30 分钟）
for i in 1 2 3; do
  python3 benchmark_vs_official_v2.py \
    /home/cdy/Desktop/security-benchmark/openclaw-skills-repo/skills \
    --output logs/generic_batch${i}.json \
    --sample-size 100 --mode random
done

# 2. 对比稳定性
echo "=== 通用性验证 ==="
for i in 1 2 3; do
  rate=$(cat logs/generic_batch${i}.json | jq '.analysis.agreement_rate')
  echo "批次$i: ${rate}%"
done

# 3. 判断
# 如果 3 个批次差异<5% → 通用性好
# 如果差异>15% → 通用性差，需要更多样本
```

---

### 明日执行（大样本验证）

```bash
# 500 个样本验证
python3 benchmark_vs_official_v2.py \
  /home/cdy/Desktop/security-benchmark/openclaw-skills-repo/skills \
  --output logs/generic_500.json \
  --sample-size 500 --mode stratified

# 查看结果
cat logs/generic_500.json | jq '.analysis.agreement_rate'
# 目标：>80%
```

---

## 📋 通用性报告模板

```markdown
# 通用性验证报告

## 测试配置
- 总 Skills 数：17,000
- 测试样本：500 (2.9%)
- 抽样方式：分层随机

## 批次稳定性
| 批次 | 样本数 | 一致率 |
|------|--------|--------|
| 批次 1 | 100 | 88.5% |
| 批次 2 | 100 | 87.2% |
| 批次 3 | 100 | 89.1% |
| **差异** | - | **1.9%** ✅ |

## 样本收敛
| 样本数 | 一致率 | 波动 |
|--------|--------|------|
| n=50 | 85.2% | - |
| n=100 | 87.8% | +2.6% |
| n=200 | 88.5% | +0.7% |
| n=500 | 88.9% | +0.4% ✅ |

## 领域差异
| 领域 | 样本数 | 一致率 |
|------|--------|--------|
| 安全审计 | 100 | 86.5% |
| 开发工具 | 150 | 89.2% |
| 自动化 | 120 | 88.7% |
| 其他 | 130 | 89.5% |
| **差异** | - | **3.0%** ✅ |

## 结论
✅ 通用性良好
- 批次稳定性：1.9% (<5%)
- 样本收敛：n≥200 稳定
- 领域差异：3.0% (<10%)

**优化方案可推广到全量 Skills**
```

---

**建议：立即执行 3 批次验证（30 分钟），确认通用性后再大规模优化！** 🎯
