# 🎯 Round 8 - 规则验证与性能优化 - 详细设计

**轮次**: Round 8  
**主题**: 规则验证与性能优化  
**状态**: 📋 设计阶段  
**时间**: 2026-03-18 12:54  
**前置**: Round 7 ✅ (160 条规则已创建)

---

## 📋 目标与指标

### 核心指标 (KPI)

| 指标 | 目标 | 测量方法 |
|------|------|----------|
| **检测率** | ≥95% | TP / (TP + FN) |
| **误报率** | <5% | FP / (FP + TN) |
| **性能 (p99)** | <50ms | 规则匹配延迟 99 分位 |
| **规则覆盖率** | 100% | 6 攻击类型 × 5 规则类型 |

### 验收标准

- [ ] 所有 160 条规则通过验证测试
- [ ] 检测率 ≥95% (每类攻击)
- [ ] 误报率 <5% (整体)
- [ ] p99 延迟 <50ms (单规则)
- [ ] 生成完整的验证报告

---

## 🏗️ 架构设计

### 验证框架架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    Round 8 验证框架                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 测试用例生成器 │  │ 规则执行引擎  │  │ 结果分析器    │          │
│  │              │  │              │  │              │          │
│  │ - 阳性样本   │  │ - YARA 扫描   │  │ - 检测率计算  │          │
│  │ - 阴性样本   │  │ - Sigma 模拟  │  │ - 误报率计算  │          │
│  │ - 边界样本   │  │ - DLP 检测    │  │ - 性能统计    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│           │                │                │                   │
│           └────────────────┼────────────────┘                   │
│                            │                                    │
│                   ┌────────▼────────┐                           │
│                   │   报告生成器     │                           │
│                   │                 │                           │
│                   │ - JSON 报告     │                           │
│                   │ - Markdown 报告  │                           │
│                   │ - 可视化图表    │                           │
│                   └─────────────────┘                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 目录结构

```
expert_mode/
├── round8/
│   ├── framework/
│   │   ├── __init__.py
│   │   ├── test_case_generator.py    # 测试用例生成
│   │   ├── rule_executor.py          # 规则执行引擎
│   │   ├── result_analyzer.py        # 结果分析器
│   │   └── report_generator.py       # 报告生成器
│   │
│   ├── test_cases/
│   │   ├── positive/                 # 阳性样本 (攻击)
│   │   │   ├── tool_poisoning/
│   │   │   ├── remote_load/
│   │   │   ├── data_exfil/
│   │   │   ├── prompt_injection/
│   │   │   ├── resource_exhaustion/
│   │   │   └── memory_pollution/
│   │   │
│   │   ├── negative/                 # 阴性样本 (正常)
│   │   │   └── (同上结构)
│   │   │
│   │   └── boundary/                 # 边界样本
│   │       └── (同上结构)
│   │
│   ├── benchmarks/
│   │   ├── performance_test.py       # 性能基准测试
│   │   └── load_test.py              # 负载测试
│   │
│   ├── scripts/
│   │   ├── run_validation.sh         # 验证执行脚本
│   │   ├── fix_false_positives.py    # 误报优化脚本
│   │   └── optimize_performance.py   # 性能优化脚本
│   │
│   └── reports/
│       ├── validation_report.json
│       ├── validation_report.md
│       └── performance_report.json
│
├── rules/                            # Round 7 规则 (160 条)
│   ├── yara/
│   ├── runtime/
│   ├── dlp/
│   ├── ioc/
│   └── sigma/
│
└── lib/
    ├── logger.py                     # 统一日志
    ├── config.py                     # 配置管理
    └── metrics.py                    # 指标计算
```

---

## 📝 模块详细设计

### 1. 测试用例生成器 (test_case_generator.py)

#### 功能
- 基于攻击类型生成阳性/阴性/边界测试用例
- 支持批量生成和手动添加
- 自动标注测试用例元数据

#### 输入
```python
{
    "attack_type": "tool_poisoning",
    "rule_type": "yara",
    "sample_count": 20,  # 每类样本数量
    "variants": ["base", "obfuscated", "polymorphic"]
}
```

#### 输出
```python
{
    "test_case_id": "tc_tool_poisoning_001",
    "attack_type": "tool_poisoning",
    "sample_type": "positive",  # positive/negative/boundary
    "content": "...",
    "expected_result": True,
    "metadata": {
        "variant": "base",
        "difficulty": "easy",
        "created_at": "2026-03-18T12:54:00Z"
    }
}
```

#### 测试用例设计

| 攻击类型 | 阳性样本 | 阴性样本 | 边界样本 | 总计 |
|----------|----------|----------|----------|------|
| tool_poisoning | 20 | 20 | 10 | 50 |
| remote_load | 20 | 20 | 10 | 50 |
| data_exfil | 20 | 20 | 10 | 50 |
| prompt_injection | 20 | 20 | 10 | 50 |
| resource_exhaustion | 20 | 20 | 10 | 50 |
| memory_pollution | 20 | 20 | 10 | 50 |
| **总计** | **120** | **120** | **60** | **300** |

---

### 2. 规则执行引擎 (rule_executor.py)

#### 功能
- 加载并执行所有规则
- 支持并行执行
- 记录执行时间和结果

#### 执行流程
```
加载规则 → 预处理 → 执行匹配 → 记录结果 → 释放资源
   ↓         ↓         ↓          ↓          ↓
 验证格式   编译优化   多线程     指标采集   内存清理
```

#### 性能要求
- 单规则执行时间：<50ms (p99)
- 并发执行：支持 10+ 线程
- 内存占用：<500MB

---

### 3. 结果分析器 (result_analyzer.py)

#### 指标计算

```python
# 混淆矩阵
TP = True Positive   # 正确检测攻击
FP = False Positive  # 误报 (正常判为攻击)
TN = True Negative   # 正确识别正常
FN = False Negative  # 漏报 (攻击判为正常)

# 核心指标
检测率 (Recall) = TP / (TP + FN)
准确率 (Precision) = TP / (TP + FP)
误报率 (FPR) = FP / (FP + TN)
F1 Score = 2 * (Precision * Recall) / (Precision + Recall)
```

#### 分析维度

| 维度 | 分析内容 |
|------|----------|
| 按攻击类型 | 每类攻击的检测率/误报率 |
| 按规则类型 | YARA/Sigma/DLP/IOC/Runtime 对比 |
| 按严重程度 | high/medium 规则表现 |
| 按风险评分 | 70-95 分段规则表现 |

---

### 4. 报告生成器 (report_generator.py)

#### 报告内容

**JSON 报告** (`validation_report.json`):
```json
{
    "round": 8,
    "timestamp": "2026-03-18T12:54:00Z",
    "summary": {
        "total_rules": 160,
        "total_test_cases": 300,
        "detection_rate": 0.96,
        "false_positive_rate": 0.04,
        "performance_p99_ms": 42
    },
    "by_attack_type": {
        "tool_poisoning": {
            "detection_rate": 0.95,
            "false_positive_rate": 0.03,
            "rules_count": 25
        }
        // ... 其他攻击类型
    },
    "by_rule_type": {
        "yara": {
            "detection_rate": 0.97,
            "false_positive_rate": 0.02,
            "avg_performance_ms": 35
        }
        // ... 其他规则类型
    },
    "failed_rules": [
        {
            "rule_id": "yara_tool_poisoning_003",
            "issue": "low_detection_rate",
            "value": 0.75,
            "target": 0.95
        }
    ],
    "recommendations": [
        "优化 rule_003 的正则表达式",
        "增加 rule_007 的特征模式"
    ]
}
```

**Markdown 报告** (`validation_report.md`):
- 执行摘要
- 指标概览 (表格 + 图表)
- 详细分析
- 问题规则列表
- 优化建议

---

### 5. 性能基准测试 (benchmarks/)

#### 测试场景

| 场景 | 描述 | 目标 |
|------|------|------|
| 单规则性能 | 单条规则执行 1000 次 | p99<50ms |
| 批量规则性能 | 160 条规则并行执行 | 总耗时<10s |
| 高负载测试 | 1000 个样本连续处理 | 吞吐量>100 样本/s |
| 内存泄漏测试 | 持续运行 1 小时 | 内存增长<10% |

#### 性能优化策略

1. **规则编译优化**
   - YARA 规则预编译
   - 正则表达式缓存
   - 规则索引建立

2. **执行优化**
   - 多线程并行
   - 规则优先级调度
   - 短路评估 (short-circuit)

3. **内存优化**
   - 流式处理
   - 对象池复用
   - 及时释放资源

---

## 🔄 执行流程

### Phase 1: 测试准备 (2 小时)

```bash
# 1. 创建测试用例目录
mkdir -p round8/test_cases/{positive,negative,boundary}/{6 攻击类型}

# 2. 生成测试用例
python round8/framework/test_case_generator.py --generate-all

# 3. 验证测试用例
python round8/framework/test_case_generator.py --validate
```

**交付物**:
- 300 个测试用例 (120 阳性 + 120 阴性 + 60 边界)
- 测试用例索引文件

---

### Phase 2: 规则验证 (4 小时)

```bash
# 1. 执行验证测试
python round8/scripts/run_validation.sh

# 2. 收集结果
# 自动输出到 round8/reports/validation_report.json
```

**验证矩阵**:
```
              │ 阳性样本 (120) │ 阴性样本 (120) │ 边界样本 (60) │
──────────────┼────────────────┼────────────────┼───────────────┤
YARA (32 条)   │     检测       │     排除       │    边界测试    │
Runtime (32 条)│     检测       │     排除       │    边界测试    │
DLP (32 条)    │     检测       │     排除       │    边界测试    │
IOC (32 条)    │     检测       │     排除       │    边界测试    │
Sigma (32 条)  │     检测       │     排除       │    边界测试    │
```

**交付物**:
- 验证执行日志
- 原始结果数据

---

### Phase 3: 结果分析 (2 小时)

```bash
# 1. 分析验证结果
python round8/framework/result_analyzer.py --input=reports/validation_report.json

# 2. 生成分析报告
python round8/framework/report_generator.py --format=md,json
```

**分析内容**:
- 检测率计算 (按攻击类型/规则类型)
- 误报率计算
- 性能统计 (p50/p90/p99)
- 问题规则识别

**交付物**:
- `validation_report.json`
- `validation_report.md`
- `performance_report.json`

---

### Phase 4: 优化迭代 (4 小时)

```bash
# 1. 修复误报规则
python round8/scripts/fix_false_positives.py --auto

# 2. 优化性能瓶颈
python round8/scripts/optimize_performance.py --target-p99=50

# 3. 重新验证
python round8/scripts/run_validation.sh --retest
```

**优化策略**:

| 问题类型 | 优化方法 | 预期提升 |
|----------|----------|----------|
| 检测率低 | 增加特征模式 | +10-20% |
| 误报率高 | 收紧正则表达式 | -5-10% |
| 性能差 | 预编译 + 缓存 | -30-50ms |

**交付物**:
- 优化后的规则集 (v1.1)
- 优化日志

---

### Phase 5: 最终验证与沉淀 (2 小时)

```bash
# 1. 最终验证
python round8/scripts/run_validation.sh --final

# 2. 生成完成报告
python round8/framework/report_generator.py --final

# 3. 规则归档
cp rules/ rules_backup_round8/
```

**交付物**:
- 最终验证报告
- Round 8 完成报告
- 规则归档 (v1.1)

---

## 📊 预期结果

### 指标达成预测

| 指标 | Round 7 | Round 8 目标 | Round 8 预测 |
|------|---------|-------------|-------------|
| 检测率 | 待验证 | ≥95% | 96-98% |
| 误报率 | 待验证 | <5% | 3-4% |
| 性能 p99 | 待验证 | <50ms | 35-45ms |
| 规则数 | 160 | 160 | 160 (优化版) |

### 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 检测率不达标 | 中 | 高 | 增加测试用例，迭代优化 |
| 误报率过高 | 中 | 中 | 收紧规则，增加白名单 |
| 性能不达标 | 低 | 中 | 预编译优化，并行执行 |
| 测试用例不足 | 低 | 中 | 手动补充边界用例 |

---

## 🛠️ 技术栈

### 核心依赖

```python
# requirements.txt
yara-python>=4.3.0      # YARA 规则引擎
pyyaml>=6.0             # YAML 解析 (Sigma)
jsonschema>=4.0         # JSON 验证
pytest>=7.0             # 测试框架
multiprocessing         # 并行执行
```

### 脚本工具

| 脚本 | 功能 | 执行时间 |
|------|------|----------|
| `run_validation.sh` | 执行完整验证 | ~30 分钟 |
| `fix_false_positives.py` | 自动修复误报 | ~10 分钟 |
| `optimize_performance.py` | 性能优化 | ~15 分钟 |

---

## 📁 交付物清单

### 代码文件

- [ ] `round8/framework/__init__.py`
- [ ] `round8/framework/test_case_generator.py`
- [ ] `round8/framework/rule_executor.py`
- [ ] `round8/framework/result_analyzer.py`
- [ ] `round8/framework/report_generator.py`
- [ ] `round8/benchmarks/performance_test.py`
- [ ] `round8/benchmarks/load_test.py`
- [ ] `round8/scripts/run_validation.sh`
- [ ] `round8/scripts/fix_false_positives.py`
- [ ] `round8/scripts/optimize_performance.py`

### 测试用例

- [ ] 120 个阳性测试用例
- [ ] 120 个阴性测试用例
- [ ] 60 个边界测试用例

### 报告文件

- [ ] `round8/reports/validation_report.json`
- [ ] `round8/reports/validation_report.md`
- [ ] `round8/reports/performance_report.json`
- [ ] `ROUND8_COMPLETION_REPORT.md`

---

## ✅ 验收检查清单

- [ ] 所有 160 条规则通过验证
- [ ] 检测率 ≥95% (每类攻击)
- [ ] 误报率 <5% (整体)
- [ ] p99 延迟 <50ms (单规则)
- [ ] 生成完整的验证报告
- [ ] 代码通过审查
- [ ] 文档完整
- [ ] 规则归档完成

---

## 📝 备注

1. **测试用例质量**: 测试用例的质量直接决定验证的可靠性，需仔细设计
2. **性能基准**: 在相同硬件环境下测试，确保结果可比
3. **版本管理**: 所有规则优化需保留历史记录，便于回滚
4. **自动化**: 验证流程应支持一键执行，便于后续回归测试

---

**下一步**: 开始 Phase 1 - 测试准备

**设计时间**: 2026-03-18 12:54  
**设计作者**: Agent Security Skill Scanner
