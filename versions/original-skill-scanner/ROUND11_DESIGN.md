# 🔧 Round 11 - 检测规则优化

**日期**: 2026-03-22  
**目标**: 规则去重 + 性能优化 + 行为分析增强

---

## 🎯 目标

| 指标 | Round 10 | Round 11 目标 | 优化方向 |
|------|----------|-------------|----------|
| 规则总数 | 160 条 | ≤120 条 | 去重 25% |
| 检测率 | 100% | ≥98% | 保持高水平 |
| 误报率 | 0% | <2% | 允许小幅上升 |
| p99 延迟 | <10ms | <5ms | 性能提升 50% |
| 行为规则 | ~30 条 | ≥50 条 | 增强行为分析 |

---

## 📋 任务清单

### 1. 规则去重 (Rule Deduplication)

**问题**: 160 条规则中存在冗余

**检测方法**:
- 相同 `condition` 的规则
- 相同 `indicators` 的规则
- 覆盖相同攻击类型的相似规则

**优化策略**:
```
原始规则 A: contains=["curl", "bash"] + contains=["|"]
原始规则 B: contains=["curl | bash"]
→ 合并为：regex=["curl.*\|.*bash"]
```

**预期**: 160 条 → 120 条 (-25%)

---

### 2. 规则分级 (Rule Tiering)

**三级规则体系**:

| 级别 | 名称 | 特点 | 执行顺序 |
|------|------|------|----------|
| **L1** | 快速过滤 | 简单字符串匹配，<1ms | 第一层 |
| **L2** | 精确匹配 | 正则/指标匹配，1-5ms | 第二层 |
| **L3** | 行为分析 | 复杂逻辑，5-20ms | 第三层 |

**执行流程**:
```
样本 → L1 过滤 (淘汰 50%) → L2 匹配 (淘汰 30%) → L3 分析 (深度检测)
```

**预期效果**: 平均延迟降低 60%

---

### 3. 行为分析增强 (Behavior Analysis)

**新增行为规则类型**:

| 行为类别 | 检测内容 | 规则数 |
|----------|----------|--------|
| **文件操作** | 敏感文件读写、配置文件修改 | +10 |
| **网络行为** | 外传请求、可疑域名、DNS 隧道 | +10 |
| **代码执行** | 动态执行、反序列化、命令注入 | +10 |
| **持久化** | 启动项、定时任务、服务注册 | +5 |
| **规避检测** | 沙箱检测、延迟执行、条件触发 | +5 |

**总计**: +40 条行为规则

---

### 4. 规则索引优化 (Rule Indexing)

**当前**: 线性扫描所有规则  
**优化**: 按攻击类型索引 + 缓存热点规则

```python
# 优化前
for rule in all_rules:
    if match(rule, sample):
        return True

# 优化后
attack_type = detect_type(sample)
for rule in rules_by_type[attack_type]:
    if match(rule, sample):
        return True
```

**预期**: 规则匹配速度提升 70%

---

## 📁 文件结构

```
expert_mode/
├── ROUND11_DESIGN.md
├── round11/
│   ├── rule_optimizer.py        # 规则优化器 (去重 + 合并)
│   ├── rule_tiering.py          # 规则分级
│   ├── behavior_analyzer.py     # 行为分析引擎
│   ├── rule_indexer.py          # 规则索引生成
│   ├── results/
│   │   ├── optimization_report.json
│   │   └── performance_comparison.json
│   └── reports/
│       └── ROUND11_REPORT.md
└── rules/
    ├── optimized/               # 优化后规则
    │   ├── L1_fast_rules.yaml
    │   ├── L2_precision_rules.yaml
    │   └── L3_behavior_rules.yaml
    └── archive/                 # 归档旧规则
```

---

## 🚀 执行步骤

### Step 1: 规则分析与去重
```bash
cd ~/.openclaw/workspace/skills/agent-security-skill-scanner/expert_mode
python3 round11/rule_optimizer.py --analyze --deduplicate
```

### Step 2: 规则分级
```bash
python3 round11/rule_tiering.py --tier-all --output rules/optimized/
```

### Step 3: 行为规则生成
```bash
python3 round11/behavior_analyzer.py --generate --attack-types all
```

### Step 4: 性能测试
```bash
python3 round11/auto_test.py --compare-with-round10
```

### Step 5: 生成报告
```bash
python3 round11/generate_report.py
```

---

## 📊 质量指标

| 指标 | 测量方法 | 目标 |
|------|----------|------|
| **规则压缩率** | (原始 - 优化)/原始 | ≥25% |
| **检测率** | 恶意样本检出比例 | ≥98% |
| **误报率** | 白样本误报比例 | <2% |
| **p99 延迟** | 99% 请求的耗时 | <5ms |
| **内存占用** | 规则引擎内存 | <50MB |

---

## ✅ 完成标准

- [ ] 规则总数 ≤120 条
- [ ] 三级规则体系建立
- [ ] 行为规则 ≥50 条
- [ ] 检测率 ≥98%
- [ ] p99 延迟 <5ms
- [ ] 完成 Round 11 报告

---

## 📈 预期对比

| 指标 | Round 10 | Round 11 | 改进 |
|------|----------|----------|------|
| 规则数 | 160 | 120 | -25% |
| 检测率 | 100% | 98-100% | 保持 |
| 误报率 | 0% | <2% | 可接受 |
| p99 延迟 | <10ms | <5ms | -50% |
| 行为规则 | ~30 | ≥50 | +67% |

---

**位置**: `~/.openclaw/workspace/skills/agent-security-skill-scanner/expert_mode/`  
**下一轮**: Round 12 - 实时检测与告警系统集成
