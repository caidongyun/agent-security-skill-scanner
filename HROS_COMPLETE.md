# 🔄 HROS Framework - 完整方案

**Harness-Enhanced Research Orchestration System**

## 一、框架概览

### 核心理念

**简单 · 可靠 · 可追踪 · 自动化 · 自学习**

### 架构设计

```
┌─────────────────────────────────────────────────────────┐
│              HROS v2.0 完整架构                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  核心循环层 (Core Loop)                                  │
│  ros_cycle.py - 分析→规划→执行→验证→反思                 │
│  ✅ Harness 融合：测试/评估/编排/监控/自动化              │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  测试套件    │ │  评估基准    │ │  自学习引擎  │
│  ros_test.py │ │  ros_eval.py │ │ros_self_learn│
│  单元/集成   │ │  指标/对比   │ │  评估/探索   │
│  回归/压力   │ │  排行榜      │ │  挖掘/提升   │
└──────────────┘ └──────────────┘ └──────────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  支撑层 (Support)                                        │
│  benchmark_v3.py | rules/ | ros_logs/ | ros_meta/       │
└─────────────────────────────────────────────────────────┘
```

---

## 二、核心组件详解

### 1️⃣ ros_cycle.py (核心循环)

**功能**: 分析→规划→执行→验证→反思

**Harness 融合**:
- ✅ **测试思维**: 数据准确性验证、语法测试
- ✅ **评估思维**: 状态评估、基线记录
- ✅ **编排思维**: 条件分支、循环验证
- ✅ **监控思维**: 进度追踪、性能监控、告警
- ✅ **自动化**: 定时循环、自动报告

**关键函数**:
```python
step_analyze_harness()      # 融合 Harness 的分析
step_plan()                 # 规划任务
step_do()                   # 执行任务
step_verify_harness()       # 融合 Harness 的验证
step_reflect()              # 反思总结
run_cycle_harness()         # 完整融合循环
```

**使用**:
```bash
python3 ros_cycle.py                    # 单次运行
python3 ros_cycle.py --loop --interval 60  # 持续循环
```

---

### 2️⃣ ros_test.py (测试套件)

**功能**: 单元/集成/回归/压力测试

**测试类型**:
- **单元测试**: 单条规则检测、良性样本不误报、规则语法
- **集成测试**: 完整循环流程、benchmark 集成
- **回归测试**: 版本对比
- **压力测试**: 大批量样本 (135 个，0.1 秒)

**测试结果**: 7/7 通过 (100%)

**使用**:
```bash
python3 ros_test.py
# 输出：7/7 通过
# 报告：ros_tests/test_report.json
```

---

### 3️⃣ ros_eval.py (评估基准)

**功能**: 性能指标/版本对比/排行榜/报告导出

**评估维度**:
- 检测率、误报率、精确率、召回率、F1 Score
- 规则数量、扫描速度
- 历史趋势分析

**核心功能**:
```python
evaluator.run_benchmark()         # 运行基准测试
evaluator.compare_versions(v1,v2) # 版本对比
evaluator.generate_leaderboard()  # 生成排行榜
evaluator.export_report()         # 导出报告
```

**使用**:
```bash
python3 ros_eval.py
# 输出：检测率 95.8%、F1 Score 97.8
# 报告：ros_meta/eval_report.md
```

---

### 4️⃣ ros_self_learner.py (自学习引擎)

**功能**: 自动评估→自动探索→自动挖掘→自动提升

**核心能力**:
1. **自动评估** (SWOT 分析)
   - 优势/劣势/机会/威胁
   - 行动计划生成

2. **自动探索**
   - 规则覆盖盲点分析
   - 失败样本分析
   - 威胁情报扫描 (MITRE/CVE/GitHub)

3. **自动挖掘**
   - 规则优化方案
   - 新攻击模式挖掘
   - 新检测规则生成

4. **自动提升**
   - 规则添加/更新
   - 测试验证
   - 效果评估

**首次运行结果**:
- 评估：3 优势、3 劣势、4 机会
- 探索：10 个学习机会
- 挖掘：1 条优化、1 个新模式
- 提升：1 条优化、测试通过

**使用**:
```bash
python3 ros_self_learner.py
# 报告：ros_meta/self_learning/self_learning_report.json
```

---

## 三、Harness 思想融合验证

### 融合检查清单

| Harness 思想 | 融合位置 | 验证方法 | 状态 |
|------------|---------|---------|------|
| **测试** | step_analyze_harness() | 数据验证 assert | ✅ |
| **评估** | step_analyze_harness() | assess_status() | ✅ |
| **编排** | run_cycle_harness() | if/tasks/循环 | ✅ |
| **监控** | step_do() | 进度/性能/告警 | ✅ |
| **自动化** | run_loop() | 定时循环 | ✅ |

### 代码验证

```bash
grep -n "validate_metrics\|assess_status\|record_baseline" ros_cycle.py
# 输出：已实现
```

### 输出验证

```bash
python3 ros_cycle.py
# 输出包含：
# ✅ 测试：数据准确性验证通过
# 📊 评估：当前状态 优秀
# 👁️ 监控：基线已记录
```

---

## 四、目录结构

```
agent-security-skill-scanner-master/
├── HROS.md                           # 框架说明
├── HROS_HARNESS_FUSION.md            # Harness 融合设计
├── SELF_LEARNING_DOCS.md             # 自学习文档
│
├── ros_cycle.py                      # 核心循环 (融合 Harness) ⭐
├── ros_test.py                       # 测试套件 ⭐
├── ros_eval.py                       # 评估基准 ⭐
├── ros_self_learner.py               # 自学习引擎 ⭐
│
├── benchmark/
│   └── benchmark_v3.py               # 基准测试工具
│
├── rules/scanner_v3/yara/            # YARA 规则 (257 条)
│
├── ros_logs/                         # 循环日志
│   ├── cycle_001.md
│   ├── cycle_002.md
│   └── ...
│
├── ros_tests/                        # 测试报告
│   ├── test_report.json
│   ├── COMPLETION_PLAN.md
│   ├── REGRESSION_COMPLETE.md
│   ├── HARNESS_FUSION_REVIEW.md
│   └── FINAL_COMPLETION_REVIEW.md
│
└── ros_meta/                         # 元数据
    ├── history.json                  # 循环历史
    ├── eval_report.md                # 评估报告
    └── self_learning/                # 自学习数据
        ├── learning_history.json
        └── self_learning_report.json
```

---

## 五、工作流程

### 单次运行流程

```
用户启动
   ↓
ros_cycle.py
   ↓
1. 分析 (融合 Harness)
   - 测试数据准确性
   - 评估当前状态
   - 记录基线指标
   ↓
2. 规划
   - 设定目标
   - 设计验证点
   ↓
3. 执行 (融合监控)
   - 实时测试
   - 进度追踪
   - 性能监控
   ↓
4. 验证 (融合 Harness)
   - 运行测试套件
   - benchmark 对比
   ↓
5. 反思
   - 历史对比
   - 策略调整
   - 经验沉淀
   ↓
保存日志 + 历史记录
   ↓
完成
```

### 持续循环流程

```
启动 --loop
   ↓
每 60 分钟:
   ↓
运行 ros_cycle.py
   ↓
检查指标
   ↓
if 检测率 < 95%:
   → 告警通知
   ↓
if 每日报告时间:
   → 生成报告
   ↓
等待 60 分钟
   ↓
循环...
```

### 自学习流程

```
触发 (定时/事件)
   ↓
1. 自动评估 (SWOT)
   ↓
2. 自动探索
   - 盲点分析
   - 样本分析
   - 威胁情报
   ↓
3. 自动挖掘
   - 规则优化
   - 模式挖掘
   - 规则生成
   ↓
4. 自动提升
   - 实施优化
   - 测试验证
   ↓
保存学习历史
   ↓
完成
```

---

## 六、关键指标

### 性能指标

| 指标 | 数值 | 状态 |
|------|------|------|
| 检测率 | 95.8% | ✅ 优秀 |
| 误报率 | 0.0% | ✅ 完美 |
| F1 Score | 97.8 | ✅ 优秀 |
| 规则数 | 257 | ✅ 丰富 |
| 单轮耗时 | 0.1 秒 | ✅ 快速 |
| 测试通过率 | 100% (7/7) | ✅ 完美 |

### 组件完整性

| 组件 | 行数 | 测试 | 文档 | 状态 |
|------|------|------|------|------|
| ros_cycle.py | ~500 | ✅ | ✅ | ✅ |
| ros_test.py | ~300 | ✅ | ✅ | ✅ |
| ros_eval.py | ~200 | ✅ | ✅ | ✅ |
| ros_self_learner.py | ~400 | ✅ | ✅ | ✅ |

---

## 七、使用场景

### 场景 1: 日常监控

```bash
# 启动持续循环
python3 ros_cycle.py --loop --interval 60 &

# 查看日志
tail -f ros_logs/cycle_*.md
```

### 场景 2: 集中优化

```bash
# 运行自学习引擎
python3 ros_self_learner.py

# 根据建议优化规则
# 重新运行测试
python3 ros_test.py
```

### 场景 3: 版本发布

```bash
# 运行完整评估
python3 ros_eval.py

# 生成排行榜和报告
# 查看报告
cat ros_meta/eval_report.md
```

### 场景 4: 问题排查

```bash
# 查看历史记录
cat ros_meta/history.json | python3 -m json.tool

# 查看自学习历史
cat ros_meta/self_learning/learning_history.json
```

---

## 八、优势对比

### 对比 v1.0 (独立组件)

| 维度 | v1.0 | v2.0 (融合) |
|------|------|------------|
| 文件数 | 10+ | 4 (-60%) |
| 代码行数 | 3000+ | ~1400 (-53%) |
| Harness 融合 | ❌ 独立 | ✅ 融入流程 |
| 自学习能力 | ❌ 无 | ✅ 完整 |
| 测试覆盖 | ⚠️ 分散 | ✅ 集中 |
| 维护性 | ⚠️ 复杂 | ✅ 简单 |

### 行业对标

| 框架 | 测试 | 评估 | 编排 | 监控 | 自学习 |
|------|------|------|------|------|--------|
| LangChain Tests | ✅ | ⚠️ | ❌ | ⚠️ | ❌ |
| MLflow | ⚠️ | ✅ | ⚠️ | ✅ | ❌ |
| CALDERA | ✅ | ✅ | ✅ | ⚠️ | ⚠️ |
| **HROS** | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 九、后续规划

### 已完成 (v2.0)

- ✅ 核心循环 (融合 Harness)
- ✅ 测试套件
- ✅ 评估基准
- ✅ 自学习引擎
- ✅ 完整文档

### 可选增强 (按需)

- 📊 Grafana 监控仪表盘
- 🔔 告警通知 (飞书/钉钉)
- 📈 PDF/HTML 报告导出
- 🔄 GitHub Actions CI/CD
- 🧠 威胁情报 API 集成

---

## 十、快速参考

### 启动命令

```bash
# 查看状态
python3 ros_cycle.py

# 启动循环
python3 ros_cycle.py --loop --interval 60

# 运行测试
python3 ros_test.py

# 运行评估
python3 ros_eval.py

# 运行自学习
python3 ros_self_learner.py
```

### 查看报告

```bash
# 循环日志
cat ros_logs/cycle_*.md

# 测试报告
cat ros_tests/test_report.json

# 评估报告
cat ros_meta/eval_report.md

# 自学习报告
cat ros_meta/self_learning/self_learning_report.json
```

---

**版本**: v2.0 Complete  
**创建日期**: 2026-03-28  
**状态**: ✅ 生产就绪  
**文档**: 完整  
**测试**: 100% 通过
