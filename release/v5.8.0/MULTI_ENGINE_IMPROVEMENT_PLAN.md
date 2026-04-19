# 🔍 多引擎差异分析提升方案

**版本**: v5.8.0
**目标**: 通过多引擎对比 + 差异分析，逐步提升检出率
**方法**: 批量扫描 → 找差异 → 分析原因 → 针对性优化 → 迭代

---

## 📂 扫描器目录

```
~/.openclaw/workspace/agent-security-skill-scanner-master/release/v5.8.0/
```

---

## 🎯 核心思路

```
┌─────────────────────────────────────────────────────────┐
│  多引擎并行扫描同一批样本                                │
│  ↓                                                      │
│  对比结果，找出"差异样本"                                │
│  (引擎 A 检出 vs 引擎 B 未检出)                          │
│  ↓                                                      │
│  分析差异原因                                            │
│  - 为什么 A 检出但 B 没检出？                            │
│  - B 的规则缺失？阈值过高？模式不匹配？                  │
│  ↓                                                      │
│  针对性优化                                              │
│  - 补充缺失规则                                          │
│  - 调整阈值                                              │
│  - 优化模式匹配                                          │
│  ↓                                                      │
│  验证效果 → 下一批样本 → 迭代                            │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 多引擎架构

### 引擎配置

| 引擎 | 版本/类型 | 规则数 | 特点 | 用途 |
|------|----------|--------|------|------|
| **引擎 1** | v5.8.0 (当前) | 797 条 | 三层架构，高速低误报 | Baseline |
| **引擎 2** | v5.6.1-R5 | 177 条 | 保守策略，高检出高误报 | 对比参考 |
| **引擎 3** | 内容分析 | N/A | 静态特征扫描 | 发现可疑 |
| **引擎 4** | LLM 判定 | - | 智能分析 | 最终裁判 |

### 引擎职责

```
引擎 1 (v5.8.0): 主扫描器，追求精确
         ↓
引擎 2 (v5.6.1-R5): 保守扫描，宁可错杀
         ↓
引擎 3 (内容分析): 提取所有可疑模式
         ↓
引擎 4 (LLM): 对差异样本智能判定
```

---

## 📊 差异样本分类

### 类型 1: 漏检 (False Negative) 🔴
```
引擎 1: ✅ 安全
引擎 2: 🔴 恶意
引擎 3: 🔴 可疑
LLM:   🔴 恶意

→ 引擎 1 漏检！需要补充规则
```

### 类型 2: 误报 (False Positive) 🟡
```
引擎 1: ✅ 安全
引擎 2: 🔴 恶意
引擎 3: 🟢 无可疑
LLM:   🟢 良性

→ 引擎 2 误报！引擎 1 正确
```

### 类型 3: 灰度样本 ⚪
```
引擎 1: ✅ 安全
引擎 2: 🟡 可疑
引擎 3: 🟡 部分可疑
LLM:   ⚪ 不确定

→ 需要人工审查或更多上下文
```

### 类型 4: 一致通过 ✅
```
引擎 1: ✅ 安全
引擎 2: ✅ 安全
引擎 3: 🟢 无可疑

→ 确认良性，无需处理
```

---

## 🔄 迭代流程

### 单轮迭代 (Per Batch)

```
步骤 1: 选择一批样本 (100-500 个)
         ↓
步骤 2: 多引擎并行扫描
         ↓
步骤 3: 对比结果，识别差异样本
         ↓
步骤 4: 分析差异原因
         ↓
步骤 5: 针对性优化 (规则/阈值/模式)
         ↓
步骤 6: 重新扫描验证效果
         ↓
步骤 7: 记录经验 → 下一批
```

### 迭代周期

| 阶段 | 批次 | 样本数 | 目标 | 预期提升 |
|------|------|--------|------|---------|
| **Phase 1** | Batch 1-3 | 300 | 修复明显漏检 | +3-5% |
| **Phase 2** | Batch 4-6 | 300 | 优化灰度样本 | +2-3% |
| **Phase 3** | Batch 7-10 | 400 | 覆盖长尾场景 | +2-3% |
| **总计** | 10 批 | 1000 | 综合提升 | +7-11% |

---

## 📁 样本选择策略

### 策略 1: 随机抽样
```bash
# 从 52K skills 中随机抽取
python3 sample_selector.py --strategy random --count 100
```
**优点**: 无偏
**缺点**: 可能错过重点

### 策略 2: 高风险优先
```bash
# 优先选择包含可疑模式的样本
python3 sample_selector.py --strategy risk --patterns "exec,curl,base64"
```
**优点**: 更可能发现漏检
**缺点**: 有偏

### 策略 3: 类别均衡
```bash
# 按攻击类型均衡抽样
python3 sample_selector.py --strategy balanced --types "injection,exfil,credential"
```
**优点**: 覆盖全面
**缺点**: 需要预分类

### 策略 4: 历史误报
```bash
# 优先选择历史上被检出的样本
python3 sample_selector.py --strategy historical --from v5.6.1-reports
```
**优点**: 针对性强
**缺点**: 依赖历史数据

---

## 🛠️ 工具设计

### 工具 1: 多引擎扫描器
```python
# multi_engine_scanner.py
python3 multi_engine_scanner.py \
    --samples /path/to/batch \
    --engines v5.8.0,v5.6.1-R5,content,llm \
    --output batch_001_results.json
```

### 工具 2: 差异分析器
```python
# diff_analyzer.py
python3 diff_analyzer.py \
    --results batch_001_results.json \
    --output diff_001.json \
    --focus "v5.8.0_missed"
```

### 工具 3: 原因分类器
```python
# root_cause_classifier.py
python3 root_cause_classifier.py \
    --diffs diff_001.json \
    --output causes_001.json \
    --categories "rule_missing,threshold_high,pattern_mismatch"
```

### 工具 4: 规则生成器
```python
# rule_generator.py
python3 rule_generator.py \
    --causes causes_001.json \
    --samples /path/to/missed_samples \
    --output new_rules_batch_001.yaml
```

### 工具 5: 效果验证器
```python
# validation_runner.py
python3 validation_runner.py \
    --rules new_rules_batch_001.yaml \
    --samples /path/to/batch \
    --output validation_001.json
```

---

## 📊 数据记录

### 批次报告模板
```markdown
## Batch 001 报告

**样本数**: 100
**扫描时间**: 2026-04-13 22:15

### 引擎对比
| 引擎 | 检出 | 漏检 | 误报 |
|------|------|------|------|
| v5.8.0 | 5 | ? | 0 |
| v5.6.1-R5 | 12 | - | 3 |
| 内容分析 | 18 | - | - |
| LLM | 8 | - | - |

### 差异样本
- 总数：7 个
- 类型分布:
  - 漏检：3 个
  - 误报：1 个
  - 灰度：3 个

### 根因分析
- 规则缺失：2 个
- 阈值过高：1 个
- 模式不匹配：0 个

### 新增规则
- 规则数：5 条
- 覆盖攻击类型：credential_theft, data_exfil

### 验证结果
- 检出率提升：+3%
- 误报率：0%
```

---

## 🎯 提升指标

### 核心指标
| 指标 | 当前 | 目标 | 测量方式 |
|------|------|------|---------|
| 检出率 | ?% | +10% | Benchmark 测试 |
| 漏检数 | - | -50% | 多引擎对比 |
| 规则数 | 797 | +100 | 规则库统计 |
| 误报率 | 0% | <2% | LLM 验证 |

### 过程指标
| 指标 | 目标 |
|------|------|
| 每批样本数 | 100-200 |
| 每批差异样本 | 5-15 个 |
| 每批新增规则 | 5-15 条 |
| 每批耗时 | <2 小时 |

---

## 📅 执行计划

### Day 1: 准备阶段
- [ ] 搭建多引擎扫描框架
- [ ] 准备 Benchmark 样本集
- [ ] 测试工具链
- [ ] 选择 Batch 1 样本 (100 个)

### Day 2-3: Phase 1 (Batch 1-3)
- [ ] Batch 1: 扫描 → 分析 → 优化 → 验证
- [ ] Batch 2: 扫描 → 分析 → 优化 → 验证
- [ ] Batch 3: 扫描 → 分析 → 优化 → 验证
- [ ] 阶段总结：检出率 +3-5%

### Day 4-5: Phase 2 (Batch 4-6)
- [ ] Batch 4-6: 同上
- [ ] 重点优化灰度样本
- [ ] 阶段总结：检出率 +2-3%

### Day 6-7: Phase 3 (Batch 7-10)
- [ ] Batch 7-10: 同上
- [ ] 覆盖长尾场景
- [ ] 最终总结：检出率 +7-11%

---

## 💡 关键成功因素

### ✅ 要做的事
1. **小步快跑** - 每批 100-200 样本，快速迭代
2. **数据驱动** - 基于差异分析结果优化
3. **质量优先** - 每条新规则都要验证
4. **记录经验** - 每批总结，避免重复错误
5. **自动化** - 工具化流程，减少人工

### ❌ 避免的坑
1. **盲目加规则** - 不分析原因就加规则
2. **忽略误报** - 只关注检出率，不管误报
3. **批量太大** - 一次处理太多，难以分析
4. **不验证** - 加了规则不测试效果
5. **不记录** - 同样的错误犯多次

---

## 🚀 启动命令

```bash
cd ~/.openclaw/workspace/agent-security-skill-scanner-master/release/v5.8.0

# 1. 准备样本
python3 sample_selector.py --strategy risk --count 100 --output batch_001/

# 2. 多引擎扫描
python3 multi_engine_scanner.py \
    --samples batch_001/ \
    --engines v5.8.0,v5.6.1-R5,content \
    --output reports/batch_001_scan.json

# 3. 差异分析
python3 diff_analyzer.py \
    --results reports/batch_001_scan.json \
    --output reports/batch_001_diff.json

# 4. 根因分析
python3 root_cause_classifier.py \
    --diffs reports/batch_001_diff.json \
    --output reports/batch_001_causes.json

# 5. 生成规则
python3 rule_generator.py \
    --causes reports/batch_001_causes.json \
    --samples batch_001/missed/ \
    --output rules/batch_001_new.yaml

# 6. 验证效果
python3 validation_runner.py \
    --rules rules/batch_001_new.yaml \
    --samples batch_001/ \
    --output reports/batch_001_validation.json
```

---

## 📈 进度追踪

### 看板
```
待处理: Batch 1-10 (1000 样本)
进行中: Batch 1
已完成: 0
```

### 燃尽图
```
批次：  1  2  3  4  5  6  7  8  9  10
剩余： 10  9  8  7  6  5  4  3  2  1
        █  █  █  █  █  █  █  █  █  █
```

---

## 📞 沟通机制

### 每批汇报
```
Batch XX 完成报告:
- 样本数：XXX
- 差异样本：XX 个
- 新增规则：XX 条
- 检出率提升：+X%
- 问题/风险：XXX
```

### 阶段总结
```
Phase X 总结:
- 总样本：XXX
- 总新增规则：XXX
- 累计提升：+XX%
- 经验教训：XXX
- 下阶段计划：XXX
```

---

**状态**: 方案设计完成，等待确认
**最后更新**: 2026-04-13 22:14
