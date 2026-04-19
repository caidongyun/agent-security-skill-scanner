# 🔥 三工具能力融合方案

**目标**: 将 Semgrep + Bandit + Trivy 的规则和检测能力融合到 v5.8.0
**策略**: 学习 → 转化 → 融合 → 优化
**架构**: 基于 v5.8.0 三层引擎 (Pattern + Rule + LLM)

---

## 📊 当前 v5.8.0 架构

```
┌─────────────────────────────────────────┐
│  Layer 1: PatternEngine (快速模式匹配)   │
│  - 35 个攻击模式                         │
│  - ~0.02ms/file                         │
│  - 短路评估                              │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Layer 2: RuleEngine (规则检测)          │
│  - 797 条高置信度规则                    │
│  - 置信度≥90                            │
│  - 预编译正则                            │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Layer 3: LLMEngine (智能判定 - 可选)    │
│  - 灰度样本深度分析                      │
└─────────────────────────────────────────┘
```

---

## 🎯 融合策略

### 三家特点分析

| 工具 | 核心能力 | 规则格式 | 检测方式 | 优势 |
|------|---------|---------|---------|------|
| **Semgrep** | 模式匹配 | YAML | 语义匹配 | 规则多，易转化 |
| **Bandit** | AST 分析 | Python | AST 遍历 | Python 专用，准确 |
| **Trivy** | 综合扫描 | Rego/YAML | 多引擎 | 全面，业界标准 |

### 融合映射

```
Semgrep 模式匹配 → Layer 1 PatternEngine (增强模式)
         ↓
Bandit AST 分析  → Layer 2 RuleEngine (Python 专用规则)
         ↓
Trivy 综合规则 → Layer 2 RuleEngine (通用安全规则)
         ↓
LLM Engine     → 统一灰度判定
```

---

## 🏗️ 融合架构设计

### 融合后架构

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: PatternEngine (增强版)                         │
│  来源：Semgrep 模式库                                    │
│  - 35 → 200+ 个攻击模式                                  │
│  - 语义模式匹配 (Semgrep 语法转化)                       │
│  - 保持高速 (~0.05ms/file)                              │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│  Layer 2: RuleEngine (融合版)                            │
│  ├─ 2A: Python 专用规则 (来自 Bandit)                    │
│  │   - AST 分析逻辑 → 正则近似实现                       │
│  │   - 200+ → 100 条核心规则                             │
│  ├─ 2B: 通用安全规则 (来自 Trivy)                        │
│  │   - Rego/YAML → 正则转化                              │
│  │   - 1000+ → 200 条高价值规则                          │
│  ├─ 2C: 模式匹配规则 (来自 Semgrep)                      │
│  │   - YAML 规则 → 正则转化                              │
│  │   - 5000+ → 300 条可转化规则                          │
│  └─ 总计：797 → 1400+ 条规则                            │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│  Layer 3: LLMEngine (统一判定)                           │
│  - 灰度样本智能判定                                      │
│  - 多工具结果冲突仲裁                                    │
│  - 误报过滤                                              │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 融合步骤

### Phase 1: Semgrep 融合 (Day 1-3) 🔥

#### 1.1 规则收集
```bash
# 收集 Semgrep Python 规则
cd ~/.openclaw/workspace/agent-security-skill-scanner-master/release/v5.8.0

# 方式 1: 使用 auto 配置
semgrep --config auto --list-rules --lang python > semgrep_python_rules.txt

# 方式 2: 克隆规则仓库
git clone https://github.com/returntocorp/semgrep-rules.git
cd semgrep-rules/python
find . -name "*.yaml" | wc -l  # 统计规则数
```

#### 1.2 规则分析
```python
# analyze_semgrep_rules.py
python3 analyze_semgrep_rules.py \
    --rules semgrep-rules/python/ \
    --output reports/semgrep_rule_analysis.json

# 分析内容:
# - 规则总数
# - 按类型分类 (injection/xss/crypto/etc)
# - 规则质量评分
# - 可转化性评估
```

#### 1.3 规则转化
```python
# transform_semgrep_rules.py
python3 transform_semgrep_rules.py \
    --input reports/semgrep_rule_analysis.json \
    --template rules/v580_pattern_template.yaml \
    --output rules/semgrep_patterns.yaml \
    --filter "confidence>=80%,python_only,easy_transform"

# 转化逻辑:
# Semgrep: pattern: exec($ARG)
# v5.8.0:  pattern: exec\s*\([^)]*\)
```

#### 1.4 集成到 Layer 1
```python
# integrate_to_layer1.py
python3 integrate_to_layer1.py \
    --current src/engines/pattern_engine.py \
    --new-patterns rules/semgrep_patterns.yaml \
    --output src/engines/pattern_engine_enhanced.py \
    --optimize "index,cache"
```

**预期产出**:
- Pattern 数量：35 → 200+
- 检测覆盖：+15 类攻击
- 性能影响：<10%

---

### Phase 2: Bandit 融合 (Day 4-6) 💎

#### 2.1 插件分析
```python
# analyze_bandit_plugins.py
python3 analyze_bandit_plugins.py \
    --plugins ~/.local/lib/python*/site-packages/bandit/plugins/ \
    --output reports/bandit_plugin_analysis.json

# 分析内容:
# - 每个插件的检测逻辑
# - AST 遍历方式
# - 误报率统计
# - 可转化性评估
```

#### 2.2 学习 AST 逻辑
```python
# 示例：exec 检测
# Bandit AST 逻辑:
def visit_Call(self, node):
    if isinstance(node.func, ast.Name) and node.func.id == 'exec':
        self.report_issue(node)

# 转化为 v5.8.0 正则:
pattern: r'\bexec\s*\([^)]*\)'
confidence: 90
```

#### 2.3 实现 Python 专用规则
```python
# create_python_rules.py
python3 create_python_rules.py \
    --bandit-logic reports/bandit_plugin_analysis.json \
    --template rules/v580_python_rule_template.yaml \
    --output rules/bandit_python_rules.yaml \
    --focus "exec,eval,shell_injection,sql_injection,hardcoded_password"
```

#### 2.4 集成到 Layer 2
```python
# integrate_to_layer2.py
python3 integrate_to_layer2.py \
    --current rules/v580_current_rules.yaml \
    --new rules/bandit_python_rules.yaml \
    --output rules/v580_python_enhanced.yaml \
    --deduplicate \
    --test-on ~/skills/sample/
```

**预期产出**:
- Python 专用规则：+100 条
- AST 逻辑学习：20+ 个核心插件
- 检测精度提升：+15%

---

### Phase 3: Trivy 融合 (Day 7-9) 🏆

#### 3.1 规则收集
```bash
# 克隆 Trivy 规则
git clone https://github.com/aquasecurity/trivy-checks.git
cd trivy-checks

# 分析规则类型
find . -name "*.rego" | wc -l  # Rego 规则
find . -name "*.yaml" | wc -l  # YAML 规则
```

#### 3.2 规则分类
```python
# classify_trivy_rules.py
python3 classify_trivy_rules.py \
    --rules trivy-checks/ \
    --output reports/trivy_rule_classification.json

# 分类:
# - 代码漏洞 (可转化)
# - 依赖漏洞 (跳过，v5.8.0 不支持)
# - 配置问题 (部分转化)
# - 密钥泄露 (高价值，转化)
```

#### 3.3 Rego 转正则
```python
# transform_rego_to_regex.py
python3 transform_rego_to_regex.py \
    --rego-rules trivy-checks/**/*.rego \
    --output rules/trivy_patterns.yaml \
    --filter "code_vulnerability,secret_detection"

# Rego 示例:
# default deny = false
# deny = true { input == "exec" }
# 
# 转化为:
# pattern: \bexec\b
```

#### 3.4 集成到 Layer 2
```python
# integrate_trivy_rules.py
python3 integrate_trivy_rules.py \
    --current rules/v580_python_enhanced.yaml \
    --new rules/trivy_patterns.yaml \
    --output rules/v580_final.yaml \
    --test-on ~/skills/ \
    --benchmark
```

**预期产出**:
- 通用安全规则：+200 条
- 密钥检测规则：+50 条
- 覆盖攻击类型：+10 类

---

### Phase 4: LLM 统一判定 (Day 10-11) 🤖

#### 4.1 冲突仲裁
```python
# conflict_resolver.py
python3 conflict_resolver.py \
    --rules rules/v580_final.yaml \
    --create-arbiter src/engines/conflict_arbiter.py

# 仲裁逻辑:
# if (Semgrep 检出 AND Bandit 检出) → 高置信度
# elif (仅 Semgrep 检出) → 中置信度
# elif (仅 Trivy 检出) → 需 LLM 判定
# else → 安全
```

#### 4.2 LLM 判定集成
```python
# integrate_llm_judge.py
python3 integrate_llm_judge.py \
    --current src/engines/llm_engine.py \
    --add-arbiter src/engines/conflict_arbiter.py \
    --output src/engines/llm_engine_enhanced.py
```

**预期产出**:
- 冲突仲裁机制
- 灰度样本准确率：≥95%
- 误报率：<2%

---

### Phase 5: 全量测试 (Day 12-14) 🧪

#### 5.1 性能测试
```python
# performance_test.py
python3 performance_test.py \
    --scanner src/engines/ \
    --rules rules/v580_final.yaml \
    --samples ~/skills/ \
    --output reports/performance_benchmark.json

# 目标:
# - 扫描速度：≥60,000 files/s (当前 73,610)
# - 内存占用：<2.5GB (当前 1.8GB)
# - p99 延迟：<1ms
```

#### 5.2 检出率测试
```python
# detection_test.py
python3 detection_test.py \
    --scanner src/engines/ \
    --rules rules/v580_final.yaml \
    --samples ~/skills/ \
    --output reports/detection_benchmark.json

# 目标:
# - 检出率：+15-20%
# - 误报率：<2%
# - 覆盖攻击类型：+25 类
```

#### 5.3 对比测试
```python
# comparison_test.py
python3 comparison_test.py \
    --v580-original rules/v580_current.yaml \
    --v580-fused rules/v580_final.yaml \
    --tools "semgrep,bandit,trivy" \
    --samples ~/skills/ \
    --output reports/fusion_comparison.json

# 对比:
# - 检出率对比
# - 误报率对比
# - 性能对比
# - 覆盖率对比
```

---

## 📊 融合效果预测

### 规则数量
| 来源 | 原始数量 | 可转化 | 最终集成 |
|------|---------|--------|---------|
| v5.8.0 原有 | 797 | - | 797 |
| Semgrep | 5000+ | 500 | 300 |
| Bandit | 200+ | 150 | 100 |
| Trivy | 1000+ | 400 | 200 |
| **总计** | **7000+** | **1050** | **1400+** |

### 检测能力
| 指标 | 当前 | 融合后 | 提升 |
|------|------|--------|------|
| 攻击类型覆盖 | 10 类 | 35 类 | +250% |
| 检出率 | ?% | ?+20% | +20% |
| 误报率 | 0% | <2% | +2% |
| 扫描速度 | 73,610/s | 60,000/s | -18% |
| 规则置信度 | ≥90 | ≥85 | -5 |

### 架构变化
| 层级 | 当前 | 融合后 | 变化 |
|------|------|--------|------|
| Layer 1 | 35 patterns | 200+ patterns | +470% |
| Layer 2 | 797 rules | 1400+ rules | +75% |
| Layer 3 | 基础 LLM | 冲突仲裁 +LLM | 增强 |

---

## 🎯 关键成功因素

### ✅ 必须做好
1. **规则筛选** - 只转化高价值规则 (置信度≥80%)
2. **去重优化** - 避免规则重复导致性能下降
3. **性能平衡** - 不因规则增加牺牲太多速度
4. **测试充分** - 每条新规则都要验证
5. **文档完整** - 记录规则来源和转化逻辑

### ❌ 避免的坑
1. **盲目转化** - 不分析就直接转
2. **忽略性能** - 规则太多导致速度大幅下降
3. **不测试** - 转化后不验证效果
4. **规则冲突** - 多个规则检测同一问题
5. **不维护** - 融合后不持续更新

---

## 📅 执行时间表

| 阶段 | 时间 | 任务 | 产出 |
|------|------|------|------|
| **Phase 1** | Day 1-3 | Semgrep 融合 | 200+ patterns |
| **Phase 2** | Day 4-6 | Bandit 融合 | 100 Python 规则 |
| **Phase 3** | Day 7-9 | Trivy 融合 | 200 通用规则 |
| **Phase 4** | Day 10-11 | LLM 统一 | 冲突仲裁 |
| **Phase 5** | Day 12-14 | 全量测试 | 对比报告 |
| **发布** | Day 15 | v5.8.0-Fused | 正式版 |

---

## 🚀 启动命令

```bash
cd ~/.openclaw/workspace/agent-security-skill-scanner-master/release/v5.8.0

# Phase 1: Semgrep 融合
./fuse_semgrep.sh

# Phase 2: Bandit 融合
./fuse_bandit.sh

# Phase 3: Trivy 融合
./fuse_trivy.sh

# Phase 4: LLM 统一
./integrate_llm_arbiter.sh

# Phase 5: 全量测试
./run_fusion_benchmark.sh

# 发布
./release_v580_fused.sh
```

---

## 💡 长期维护

### 规则更新
```
每月：同步 Semgrep/Bandit/Trivy 新规则
每季度：清理低效规则
每半年：架构重构优化
```

### 质量监控
```
每日：扫描日志分析
每周：误报/漏报复盘
每月：规则质量评估
```

---

**状态**: 融合方案设计完成
**建议**: 立即开始 Phase 1 (Semgrep 融合)
