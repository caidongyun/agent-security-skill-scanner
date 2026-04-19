# 权重参数调整记录

**时间**: 2026-04-08 21:30  
**目的**: 降低误报率，提高一致率

## 调整内容

### 上下文感知权重

**旧权重**（过于宽松）:
```python
OFFICIAL_SKILL_FACTOR = 0.5      # 降低 50%
INSTALL_SCRIPT_FACTOR = 0.6      # 降低 40%
DOCUMENTATION_FACTOR = 0.8       # 降低 20%
AUTHOR_FACTOR = 0.7              # 降低 30%

# 累积：0.5 × 0.8 × 0.7 = 0.28 (降低 72%)
```

**新权重**（更合理）:
```python
OFFICIAL_SKILL_FACTOR = 0.8      # 降低 20%
INSTALL_SCRIPT_FACTOR = 0.85     # 降低 15%
DOCUMENTATION_FACTOR = 0.9       # 降低 10%
AUTHOR_FACTOR = 0.9              # 降低 10%

# 累积：0.8 × 0.9 × 0.9 = 0.65 (降低 35%)
```

### 阈值控制

**新增**:
```python
# 高风险案例不减免
if total_weight > 0.6:
    return total_weight  # 不应用上下文减免

# 最低风险阈值
return max(total_weight, 0.3)  # 不低于 30%
```

## 预期效果

| 指标 | 当前 | 目标 | 改善 |
|------|------|------|------|
| 一致率 | 25% | >70% | +180% |
| 误报数 | 15 个 | <5 个 | -67% |

## 验证方案

```bash
# 测试新权重
python3 benchmark_vs_official_v2.py /path/to/skills \
  --output logs/weight_adjusted.json \
  --sample-size 100 \
  --context-aware
```
