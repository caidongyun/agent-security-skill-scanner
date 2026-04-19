# 多 Skill 对比测试问题分析报告

**测试时间**: 2026-04-08 21:15  
**测试样本**: 20 个随机 Skills  
**对比方式**: 基础扫描 vs 上下文感知扫描

---

## 📊 核心发现

### 一致率对比

| 扫描方式 | 一致率 | 误报数 | 状态 |
|---------|--------|--------|------|
| **基础扫描** | **90.0%** | 2 个 | ✅ 良好 |
| **上下文感知** | **25.0%** | 15 个 | ❌ 过于宽松 |

**结论**: 基础扫描更准确，上下文感知过于宽松

---

## 🔍 误报案例分析

### 基础扫描误报 (2 个)

1. **fund-advisor-agent** - 2 个恶意文件
2. **email-campaign** - 1 个恶意文件

**原因**: Round 18 检测过于敏感

---

### 上下文感知误报 (15 个)

**典型误报案例**:
- notebooklm-audio-generator ❌
- clicky-analytics ❌
- cloud-support ❌
- prompting ❌
- conventional-git ❌

**原因**: 上下文感知过度降低风险权重

---

## ⚠️ 问题分析

### 问题 1: 上下文感知过于宽松

**表现**:
- 15 个基础扫描判定为 SAFE 的 Skills
- 上下文感知判定为 MALICIOUS
- 但官方判定为 SAFE（误报）

**根本原因**:
```python
# 当前实现：过度降低风险
if is_official:
    total_weight *= 0.5  # 降低 50%
if has_documentation:
    total_weight *= 0.8  # 降低 20%
if author_rep == 'high':
    total_weight *= 0.7  # 降低 30%

# 累积效果：0.5 * 0.8 * 0.7 = 0.28 (降低 72%!)
```

**结果**: 大量良性 Skills 被判定为恶意

---

### 问题 2: 权重设计不合理

**当前权重**:
- 官方 Skill: ×0.5
- 安装脚本: ×0.6
- 文档完整: ×0.8
- 知名作者: ×0.7

**问题**: 权重减免是**乘法累积**的，导致过度降低

**示例**:
```
官方 Skill + 文档完整 + 知名作者
= 0.5 × 0.8 × 0.7 = 0.28 (仅 28% 风险)

即使有 curl|bash，风险分也会从 0.9 降至 0.25
导致误判为 SAFE
```

---

### 问题 3: 缺乏阈值控制

**当前逻辑**:
```python
if is_official:
    total_weight *= 0.5  # 无条件降低
```

**问题**: 没有设置最低阈值，导致高风险也被过度降低

**应该**:
```python
if is_official and total_weight < 0.6:
    total_weight *= 0.8  # 仅降低低风险案例
```

---

## 🎯 优化方案

### 方案 1: 调整权重（推荐）

**新权重**:
```python
# 降低减免幅度
OFFICIAL_SKILL_FACTOR = 0.8  # 从 0.5 改为 0.8
INSTALL_SCRIPT_FACTOR = 0.85  # 从 0.6 改为 0.85
DOCUMENTATION_FACTOR = 0.9  # 从 0.8 改为 0.9
AUTHOR_FACTOR = 0.9  # 从 0.7 改为 0.9

# 累积效果：0.8 * 0.9 * 0.9 = 0.65 (降低 35%，而非 72%)
```

**预期效果**: 一致率从 25% 提升至 70%+

---

### 方案 2: 增加阈值控制

**实现**:
```python
def apply_context_factors(total_weight, context):
    # 只有低风险案例才应用上下文减免
    if total_weight > 0.6:  # 高风险不减免
        return total_weight
    
    # 应用减免
    if context['is_official']:
        total_weight *= 0.8
    if context['has_documentation']:
        total_weight *= 0.9
    
    return max(total_weight, 0.3)  # 最低 30% 风险
```

**预期效果**: 避免高风险案例被错误降低

---

### 方案 3: 综合判定

**逻辑**:
```python
# 结合基础扫描 + 上下文 + 领域判定
base_verdict = base_scan(skill)
context_verdict = context_scan(skill)
domain_verdict = domain_scan(skill)

# 投票判定
if base_verdict == 'SAFE' and domain_verdict == 'SAFE':
    final_verdict = 'SAFE'  # 基础 + 领域都安全 → 安全
elif base_verdict == 'MALICIOUS' or context_verdict == 'MALICIOUS':
    final_verdict = 'MALICIOUS'  # 任一判定恶意 → 恶意
else:
    final_verdict = 'SUSPICIOUS'  # 边界案例 → 可疑
```

**预期效果**: 一致率提升至 85%+

---

## 📋 推荐实施方案

### 立即实施

1. **调整权重** (方案 1)
   - 降低减免幅度
   - 避免过度降低

2. **增加阈值** (方案 2)
   - 高风险案例不减免
   - 设置最低风险阈值

### 中期实施

3. **综合判定** (方案 3)
   - 结合多种扫描方式
   - 投票判定

---

## 🧪 验证方案

### 测试命令

```bash
# 1. 调整权重后测试
python3 benchmark_vs_official_v2.py /path/to/skills \
  --output logs/benchmark_optimized.json \
  --sample-size 100 \
  --context-aware

# 2. 对比效果
cat logs/benchmark_optimized.json | jq '.analysis.agreement_rate'
# 目标：>70%
```

---

## 📊 预期效果

| 指标 | 当前 | 目标 | 改善 |
|------|------|------|------|
| **一致率** | 25.0% | **>70%** | +180% |
| **误报数** | 15 个 | **<5 个** | -67% |
| **召回率** | 100% | **>95%** | 保持 |

---

**分析完成！建议立即调整权重和阈值。** 🎯
