# 🚀 v5.8.0 融合增强 - 详细实施计划

**版本**: v5.8.0-Enhanced
**方案**: 混合模式 (方案 A)
**周期**: 8 天
**目标**: 融合 Semgrep/Bandit/Trivy 能力，检出率 +20%, 速度保持≥60,000/s

---

## 📋 任务分解

### Phase 1: Pattern 增强 (Day 1-2)

#### Task 1.1: Semgrep 规则收集
**ID**: T1.1
**优先级**: P0
**工时**: 2h
**输入**: Semgrep 规则仓库
**输出**: `semgrep_python_rules.json`

**执行步骤**:
```bash
# 1. 克隆规则仓库
git clone https://github.com/returntocorp/semgrep-rules.git

# 2. 统计 Python 规则
cd semgrep-rules
find python/ -name "*.yaml" -o -name "*.yml" | wc -l

# 3. 提取规则元数据
python3 scripts/extract_semgrep_metadata.py \
    --rules python/ \
    --output reports/semgrep_python_rules.json
```

**验收标准**:
- [ ] 收集 5000+ Python 规则
- [ ] 提取规则元数据 (ID/名称/类型/严重级别)
- [ ] 生成规则索引

---

#### Task 1.2: Pattern 转化
**ID**: T1.2
**优先级**: P0
**工时**: 4h
**输入**: `semgrep_python_rules.json`
**输出**: `rules/v580_patterns_semgrep.yaml`

**执行步骤**:
```python
# transform_semgrep_patterns.py
python3 scripts/transform_semgrep_patterns.py \
    --input reports/semgrep_python_rules.json \
    --template rules/v580_pattern_template.yaml \
    --output rules/v580_patterns_semgrep.yaml \
    --filter "confidence>=80%,python_only,easy_transform" \
    --limit 200
```

**转化逻辑**:
```yaml
# Semgrep 原始规则
rules:
  - id: python-exec-use
    patterns:
      - pattern: exec($ARG)
    message: "Use of exec() detected"
    severity: WARNING

# 转化为 v5.8.0 Pattern
patterns:
  - id: V580-P0036
    name: python_exec_call
    pattern: "\\bexec\\s*\\([^)]*\\)"
    severity: HIGH
    confidence: 90
    source: semgrep
    original_id: python-exec-use
```

**验收标准**:
- [ ] 转化 200 个 patterns
- [ ] 每个 pattern 通过正则测试
- [ ] 无语法错误
- [ ] 性能测试通过 (<0.05ms/pattern)

---

#### Task 1.3: Pattern 单元测试
**ID**: T1.3
**优先级**: P0
**工时**: 2h
**输入**: `rules/v580_patterns_semgrep.yaml`
**输出**: `tests/pattern_unit_test_results.json`

**执行步骤**:
```python
# test_patterns.py
python3 tests/test_patterns.py \
    --patterns rules/v580_patterns_semgrep.yaml \
    --test-cases tests/pattern_test_cases/ \
    --output tests/pattern_unit_test_results.json
```

**测试用例结构**:
```
tests/pattern_test_cases/
├── exec_eval/
│   ├── test_exec_1.py (应匹配)
│   ├── test_exec_2.py (应匹配)
│   └── test_safe_1.py (不应匹配)
├── shell_injection/
│   ├── test_os_system_1.py (应匹配)
│   └── ...
└── ...
```

**验收标准**:
- [ ] 200 个 patterns 全部通过测试
- [ ] 真阳性率 ≥95%
- [ ] 假阳性率 <5%
- [ ] 性能达标 (<0.05ms/pattern)

---

### Phase 2: 规则引擎扩展 (Day 3-5)

#### Task 2.1: AST 模式设计
**ID**: T2.1
**优先级**: P1
**工时**: 4h
**输入**: Bandit 插件源码
**输出**: `docs/ast_mode_design.md`

**执行步骤**:
```python
# analyze_bandit_ast.py
python3 scripts/analyze_bandit_ast.py \
    --plugins ~/.local/lib/python*/site-packages/bandit/plugins/ \
    --output reports/bandit_ast_patterns.json
```

**设计文档内容**:
```markdown
# AST 模式设计

## 核心检测
1. exec/eval/callable 检测
2. 危险 import 检测
3. 硬编码密码检测
4. SQL 注入检测
5. 不安全哈希检测

## AST 节点类型
- Call (函数调用)
- Import (导入)
- Assign (赋值)
- Attribute (属性访问)

## 触发条件
- Layer 1 Pattern 命中 ≥2 条
- 或 Layer 2 正则规则命中 ≥3 条
```

**验收标准**:
- [ ] 设计文档完整
- [ ] 覆盖 Bandit 核心 20 个插件
- [ ] 性能预估合理 (<5ms/file)

---

#### Task 2.2: AST 引擎实现
**ID**: T2.2
**优先级**: P0
**工时**: 8h
**输入**: `docs/ast_mode_design.md`
**输出**: `src/engines/ast_engine.py`

**代码结构**:
```python
# src/engines/ast_engine.py
class ASTEngine:
    def __init__(self):
        self.rules = self.load_rules()
    
    def scan(self, file_path: str, content: str) -> List[Hit]:
        """AST 扫描"""
        try:
            tree = ast.parse(content)
            hits = []
            
            for node in ast.walk(tree):
                # exec/eval检测
                if isinstance(node, ast.Call):
                    hits.extend(self.check_call(node))
                # import 检测
                elif isinstance(node, ast.Import):
                    hits.extend(self.check_import(node))
                # ...
            
            return hits
        except SyntaxError:
            return []
    
    def check_call(self, node: ast.Call) -> List[Hit]:
        """检查函数调用"""
        hits = []
        if isinstance(node.func, ast.Name):
            if node.func.id in ['exec', 'eval', 'compile']:
                hits.append(Hit(
                    rule_id='AST-EXEC-001',
                    line=node.lineno,
                    severity='HIGH'
                ))
        return hits
```

**验收标准**:
- [ ] 实现 50-100 条 AST 规则
- [ ] 单元测试通过率 100%
- [ ] 性能测试 <5ms/file
- [ ] 代码覆盖率 ≥80%

---

#### Task 2.3: 规则引擎集成
**ID**: T2.3
**优先级**: P0
**工时**: 4h
**输入**: `src/engines/rule_engine.py`, `src/engines/ast_engine.py`
**输出**: `src/engines/rule_engine_v2.py`

**集成逻辑**:
```python
# src/engines/rule_engine_v2.py
class RuleEngineV2:
    def __init__(self):
        self.regex_rules = self.load_regex_rules()
        self.ast_engine = ASTEngine()
    
    def scan(self, file_path: str, content: str) -> ScanResult:
        # Mode A: 正则规则 (快速)
        regex_hits = self.regex_scan(content)
        
        # Mode B: AST 规则 (仅当命中 2+ 条正则时启用)
        ast_hits = []
        if len(regex_hits) >= 2:
            ast_hits = self.ast_engine.scan(file_path, content)
        
        # 合并结果
        return ScanResult(
            hits=regex_hits + ast_hits,
            risk_level=self.calculate_risk(regex_hits, ast_hits),
            engines_triggered=['regex'] + (['ast'] if ast_hits else [])
        )
```

**验收标准**:
- [ ] 正则+AST 集成完成
- [ ] 触发逻辑正确
- [ ] 结果合并正确
- [ ] 性能测试通过

---

### Phase 3: 规则融合 (Day 6)

#### Task 3.1: 规则库合并
**ID**: T3.1
**优先级**: P0
**工时**: 3h
**输入**: 
- `rules/v580_current.yaml` (797 条)
- `rules/v580_patterns_semgrep.yaml` (200 条)
- `rules/bandit_converted.yaml` (100 条)
- `rules/trivy_converted.yaml` (200 条)

**输出**: `rules/v580_enhanced.yaml` (1400+ 条)

**执行步骤**:
```python
# merge_rules.py
python3 scripts/merge_rules.py \
    --base rules/v580_current.yaml \
    --new rules/v580_patterns_semgrep.yaml \
    --new rules/bandit_converted.yaml \
    --new rules/trivy_converted.yaml \
    --output rules/v580_enhanced.yaml \
    --deduplicate \
    --optimize
```

**去重策略**:
- 相同 pattern 合并
- 相似规则合并 (相似度>90%)
- 保留最高置信度

**验收标准**:
- [ ] 规则总数 1400+ 条
- [ ] 无重复规则
- [ ] 规则索引生成
- [ ] YAML 格式验证通过

---

### Phase 4: 单元测试 (Day 7 上午)

#### Task 4.1: 完整单元测试套件
**ID**: T4.1
**优先级**: P0
**工时**: 4h
**输入**: 所有源代码
**输出**: `tests/unit_test_results.json`

**测试范围**:
```
tests/
├── test_pattern_engine.py      # Pattern 引擎测试
├── test_rule_engine.py         # 规则引擎测试
├── test_ast_engine.py          # AST 引擎测试
├── test_llm_engine.py          # LLM 引擎测试
├── test_integration.py         # 集成测试
└── test_performance.py         # 性能测试
```

**执行命令**:
```bash
# 运行所有单元测试
pytest tests/ -v --cov=src/engines --cov-report=html \
    --output tests/unit_test_results.json
```

**验收标准**:
- [ ] 测试通过率 100%
- [ ] 代码覆盖率 ≥80%
- [ ] 无性能回归
- [ ] 生成测试报告

---

### Phase 5: Benchmark 测试 (Day 7 下午)

#### Task 5.1: 性能 Benchmark
**ID**: T5.1
**优先级**: P0
**工时**: 3h
**输入**: `src/engines/`, `rules/v580_enhanced.yaml`
**输出**: `reports/performance_benchmark.json`

**测试场景**:
```python
# benchmark_performance.py
python3 benchmarks/benchmark_performance.py \
    --scanner src/engines/ \
    --rules rules/v580_enhanced.yaml \
    --samples ~/skills/ \
    --output reports/performance_benchmark.json

# 测试指标:
# - 扫描速度 (files/s)
# - p99 延迟 (ms)
# - 内存占用 (MB)
# - CPU 使用率 (%)
```

**目标指标**:
| 指标 | 当前 | 目标 | 验收 |
|------|------|------|------|
| 扫描速度 | 73,610/s | ≥60,000/s | ✅/❌ |
| p99 延迟 | 0.07ms | <1ms | ✅/❌ |
| 内存占用 | 1.8GB | <2.5GB | ✅/❌ |

---

#### Task 5.2: 检出率 Benchmark
**ID**: T5.2
**优先级**: P0
**工时**: 3h
**输入**: `src/engines/`, `rules/v580_enhanced.yaml`
**输出**: `reports/detection_benchmark.json`

**测试样本**:
- 52,626 OpenClaw skills
- 已知恶意样本集 (如有)

**执行命令**:
```bash
python3 benchmarks/benchmark_detection.py \
    --scanner src/engines/ \
    --rules rules/v580_enhanced.yaml \
    --samples ~/skills/ \
    --output reports/detection_benchmark.json
```

**目标指标**:
| 指标 | 当前 | 目标 | 验收 |
|------|------|------|------|
| 检出率 | ?% | ?+20% | ✅/❌ |
| 误报率 | 0% | <2% | ✅/❌ |
| 覆盖攻击类型 | 10 类 | 35 类 | ✅/❌ |

---

### Phase 6: 对比测试 (Day 8 上午)

#### Task 6.1: 多工具对比
**ID**: T6.1
**优先级**: P1
**工时**: 3h
**输入**: v5.8.0-Enhanced, Semgrep, Bandit, Trivy
**输出**: `reports/multi_tool_comparison.json`

**执行命令**:
```bash
python3 benchmarks/compare_tools.py \
    --samples validation_samples/ \
    --tools "v580_enhanced,semgrep,bandit,trivy" \
    --output reports/multi_tool_comparison.json
```

**对比维度**:
- 检出率
- 误报率
- 性能
- 覆盖率

---

#### Task 6.2: 优化前后对比
**ID**: T6.2
**优先级**: P0
**工时**: 2h
**输入**: v5.8.0-original, v5.8.0-enhanced
**输出**: `reports/before_after_comparison.json`

**执行命令**:
```bash
python3 benchmarks/compare_before_after.py \
    --original rules/v580_current.yaml \
    --enhanced rules/v580_enhanced.yaml \
    --samples ~/skills/ \
    --output reports/before_after_comparison.json
```

**对比内容**:
- 新增检出样本
- 规则数量变化
- 性能变化
- 误报变化

---

### Phase 7: 问题修复与发布 (Day 8 下午)

#### Task 7.1: 问题修复
**ID**: T7.1
**优先级**: P0
**工时**: 3h
**输入**: Benchmark 测试发现的问题
**输出**: 修复后的代码

**执行流程**:
```
发现问题 → 记录 Issue → 修复 → 回归测试 → 关闭 Issue
```

**验收标准**:
- [ ] 所有 P0 Issue 修复
- [ ] 回归测试通过
- [ ] 性能达标

---

#### Task 7.2: 发布准备
**ID**: T7.2
**优先级**: P0
**工时**: 2h
**输入**: 所有代码和报告
**输出**: `release/v5.8.0-Enhanced/`

**发布内容**:
```
release/v5.8.0-Enhanced/
├── src/                      # 源代码
├── rules/                    # 规则库
├── docs/                     # 文档
│   ├── RELEASE_NOTES.md
│   ├── MIGRATION_GUIDE.md
│   └── PERFORMANCE_REPORT.md
├── reports/                  # 测试报告
│   ├── unit_tests.json
│   ├── performance.json
│   ├── detection.json
│   └── comparison.json
└── README.md
```

**验收标准**:
- [ ] 所有文件齐全
- [ ] 文档完整
- [ ] 测试报告齐全
- [ ] 发布脚本就绪

---

## 📅 时间表

| Day | 上午 (9:00-12:00) | 下午 (14:00-18:00) | 晚上 (可选) |
|-----|------------------|-------------------|-----------|
| **1** | T1.1: Semgrep 收集 | T1.2: Pattern 转化 (上) | - |
| **2** | T1.2: Pattern 转化 (下) | T1.3: Pattern 测试 | - |
| **3** | T2.1: AST 设计 | T2.2: AST 实现 (上) | - |
| **4** | T2.2: AST 实现 (下) | T2.2: AST 实现 (续) | - |
| **5** | T2.3: 规则引擎集成 | T2.3: 集成测试 | - |
| **6** | T3.1: 规则库合并 | T3.1: 去重优化 | - |
| **7** | T4.1: 单元测试 | T5.1+T5.2: Benchmark | - |
| **8** | T6.1+T6.2: 对比测试 | T7.1+T7.2: 修复发布 | 庆功 🎉 |

---

## 📊 验收标准

### 功能验收
- [ ] Pattern 数量：35 → 200+ ✅
- [ ] 规则总数：797 → 1400+ ✅
- [ ] AST 引擎实现 ✅
- [ ] 触发逻辑正确 ✅

### 性能验收
- [ ] 扫描速度：≥60,000 files/s ✅
- [ ] p99 延迟：<1ms ✅
- [ ] 内存占用：<2.5GB ✅

### 质量验收
- [ ] 检出率提升：+20% ✅
- [ ] 误报率：<2% ✅
- [ ] 单元测试通过率：100% ✅
- [ ] 代码覆盖率：≥80% ✅

### 文档验收
- [ ] 发布说明完整 ✅
- [ ] 测试报告齐全 ✅
- [ ] 使用文档更新 ✅

---

## 🚀 启动命令

```bash
cd ~/.openclaw/workspace/agent-security-skill-scanner-master/release/v5.8.0

# 创建任务目录
mkdir -p scripts tests benchmarks reports rules

# 启动 Phase 1
./run_phase1.sh

# 查看进度
./check_progress.sh
```

---

## 📈 进度追踪

### 看板
```
待处理：T1.1-T7.2 (15 个任务)
进行中：-
已完成：0
阻塞：0
```

### 燃尽图
```
任务：15 14 13 12 11 10 9  8  7  6  5  4  3  2  1
      █  █  █  █  █  █  █  █  █  █  █  █  █  █  █
```

---

**状态**: 详细设计完成，准备启动
**最后更新**: 2026-04-13 22:36
