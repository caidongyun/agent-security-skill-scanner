# 🔍 v5.8.0 扫描器兼容性分析

**问题**: v5.8.0 扫描方式需要调整兼容 Semgrep/Bandit/Trivy 吗？
**答案**: **适度调整**，但**不需要完全兼容**

---

## 📊 方案对比

### 方案 A: 仅融合规则 (推荐) ✅

```
v5.8.0 架构保持不变
    ↓
只转化规则格式
    ↓
Semgrep/Bandit/Trivy 规则 → v5.8.0 正则格式
    ↓
保持原有扫描方式
```

**优点**:
- ✅ 保持高速 (73,610 files/s)
- ✅ 架构简单，易维护
- ✅ 无需依赖外部工具
- ✅ 规则统一管理

**缺点**:
- ❌ 无法利用 AST 分析 (Bandit 核心)
- ❌ 无法利用语义匹配 (Semgrep 优势)
- ❌ 无法利用数据流分析
- ❌ 检测精度略低

**适用场景**:
- 追求速度和简洁
- 主要检测已知模式
- 不需要深度语义分析

---

### 方案 B: 调整架构兼容 (增强版) 🔥

```
v5.8.0 三层架构扩展
    ↓
Layer 1: PatternEngine (保持正则)
    ↓
Layer 2: RuleEngine (多引擎支持)
    ├─ 2A: 正则规则 (v5.8.0 原生)
    ├─ 2B: AST 规则 (Bandit 兼容)
    ├─ 2C: 语义规则 (Semgrep 兼容)
    └─ 2D: Rego 规则 (Trivy 兼容，可选)
    ↓
Layer 3: LLMEngine (统一判定)
```

**优点**:
- ✅ 检测能力大幅增强
- ✅ 可利用 AST 分析 (更准确)
- ✅ 可利用语义匹配 (更智能)
- ✅ 规则格式原汁原味

**缺点**:
- ❌ 架构复杂度 +300%
- ❌ 扫描速度下降 30-50%
- ❌ 维护成本大幅增加
- ❌ 需要依赖外部库

**适用场景**:
- 追求检测精度
- 需要深度语义分析
- 可接受速度下降

---

## 🎯 推荐方案：混合模式 (方案 B 简化版)

### 架构设计

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: PatternEngine (保持原样)                       │
│  - 35 → 200+ 个快速模式                                  │
│  - 正则匹配，~0.05ms/file                               │
│  - 短路评估，无命中直接返回 SAFE                         │
└─────────────────────────────────────────────────────────┘
                    ↓ (Pattern 命中后)
┌─────────────────────────────────────────────────────────┐
│  Layer 2: RuleEngine (适度扩展)                          │
│  ├─ Mode A: 正则规则 (默认，95% 场景)                    │
│  │   - 797 → 1200 条                                     │
│  │   - 来源：Semgrep 转化 + Trivy 转化 + 原生            │
│  │   - 速度：~0.5ms/file                                │
│  │                                                      │
│  └─ Mode B: AST 规则 (可选，5% 复杂场景)                 │
│      - 50-100 条 (仅 Bandit 核心规则)                    │
│      - 来源：Bandit AST 逻辑简化                          │
│      - 速度：~5ms/file (慢 10 倍，但仅用于可疑文件)       │
│      - 触发条件：正则规则命中 2+ 条时启用                │
└─────────────────────────────────────────────────────────┘
                    ↓ (仅 Mode B 需要时)
┌─────────────────────────────────────────────────────────┐
│  Layer 3: LLMEngine (统一判定)                           │
│  - 灰度样本判定                                          │
│  - 冲突仲裁                                              │
└─────────────────────────────────────────────────────────┘
```

### 工作流程

```
文件扫描
    ↓
Layer 1: Pattern 匹配 (200+ patterns)
    ↓ (命中)
Layer 2 Mode A: 正则规则检测 (1200 条)
    ↓ (命中 2+ 条，标记为"高度可疑")
Layer 2 Mode B: AST 深度分析 (50-100 条)
    ↓ (可选)
Layer 3: LLM 判定
    ↓
输出结果
```

### 性能预估

| 场景 | 占比 | 扫描方式 | 速度 | 平均耗时 |
|------|------|---------|------|---------|
| **安全文件** | 90% | Layer 1 only | 73,610/s | ~0.02ms |
| **轻度可疑** | 8% | Layer 1 + 2A | 50,000/s | ~0.5ms |
| **高度可疑** | 2% | Layer 1 + 2A + 2B | 5,000/s | ~5ms |
| **综合速度** | 100% | - | **~60,000/s** | ~0.6ms |

**性能影响**: 仅下降 **18%** (73,610 → 60,000/s)

---

## 🛠️ 需要调整的扫描方式

### 1. Pattern 匹配增强 (必须)

**当前**: 35 个简单正则
**增强**: 200+ 个 Semgrep 转化模式

```python
# 当前
patterns = [
    r'exec\s*\(',
    r'eval\s*\(',
]

# 增强后 (Semgrep 转化)
patterns = [
    # 代码执行
    r'exec\s*\([^)]*\)',
    r'eval\s*\([^)]*\)',
    r'compile\s*\([^)]*\)',
    
    # Shell 注入
    r'os\.system\s*\([^)]*\)',
    r'subprocess\.(call|run|Popen)\s*\([^)]*\)',
    
    # ... 200+ patterns
]
```

**改动**: 小 (仅扩充 pattern 列表)

---

### 2. 规则引擎扩展 (推荐)

**当前**: 仅支持正则规则
**扩展**: 支持正则 + 简单 AST

```python
# 当前
class RuleEngine:
    def scan(self, content):
        for rule in self.rules:
            if re.search(rule.pattern, content):
                self.report(rule)

# 扩展后
class RuleEngine:
    def scan(self, file_path, content):
        # Mode A: 正则规则 (快速)
        hits = []
        for rule in self.regex_rules:
            if re.search(rule.pattern, content):
                hits.append(rule)
        
        # Mode B: AST 规则 (仅当命中 2+ 条正则时启用)
        if len(hits) >= 2:
            ast_hits = self.ast_scan(file_path, content)
            hits.extend(ast_hits)
        
        return hits
    
    def ast_scan(self, file_path, content):
        # 简化的 AST 分析 (仅核心检测)
        import ast
        try:
            tree = ast.parse(content)
            hits = []
            for node in ast.walk(tree):
                # exec/eval 检测
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['exec', 'eval', 'compile']:
                            hits.append('AST_EXEC_EVAL')
                # import 检测
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in ['os', 'sys', 'subprocess']:
                            hits.append('AST_DANGEROUS_IMPORT')
            return hits
        except:
            return []
```

**改动**: 中 (增加 AST 模式，但仅用于可疑文件)

---

### 3. 规则格式兼容 (推荐)

**当前**: v5.8.0 自定义 YAML
**扩展**: 支持多格式导入

```yaml
# 当前格式
rules:
  - id: V580-0001
    pattern: "exec\\s*\\("
    severity: HIGH
    confidence: 95

# 扩展后 (支持 Semgrep 格式导入)
rules:
  - id: SEMGREP-0001
    source: semgrep
    pattern: "exec\\s*\\("  # 从 Semgrep 转化
    severity: HIGH
    confidence: 90
    
  - id: BANDIT-0001
    source: bandit
    pattern: "\\bexec\\b"  # 从 Bandit 转化
    ast_check: true  # 标记需要 AST 验证
    severity: HIGH
    confidence: 85
```

**改动**: 小 (增加规则元数据)

---

### 4. 结果合并 (推荐)

**当前**: 单一结果
**扩展**: 多引擎结果合并

```python
# 当前
result = {
    "risk_level": "CRITICAL",
    "rules_matched": ["V580-0001"]
}

# 扩展后
result = {
    "risk_level": "CRITICAL",
    "rules_matched": [
        {"id": "V580-0001", "source": "native"},
        {"id": "SEMGREP-0001", "source": "semgrep"},
        {"id": "BANDIT-0001", "source": "bandit", "ast_verified": true}
    ],
    "confidence": 95,
    "engines_triggered": ["pattern", "regex", "ast"]
}
```

**改动**: 小 (增加结果元数据)

---

## 📊 改动总结

| 模块 | 改动大小 | 工作量 | 风险 |
|------|---------|--------|------|
| **Pattern 增强** | 小 | 1-2 天 | 低 |
| **规则引擎扩展** | 中 | 3-4 天 | 中 |
| **规则格式兼容** | 小 | 1 天 | 低 |
| **结果合并** | 小 | 1 天 | 低 |
| **总计** | 中 | 6-8 天 | 中 |

---

## 🎯 最终建议

### 推荐：混合模式 (方案 B 简化版)

**核心思路**:
- Layer 1: 保持高速正则匹配 (Semgrep 转化 200+ patterns)
- Layer 2: 主要用正则规则 (1200 条)，仅可疑文件用 AST (50-100 条)
- Layer 3: LLM 统一判定

**优势**:
- ✅ 检测能力大幅增强 (+75% 规则)
- ✅ 保持较高速度 (60,000/s, 仅 -18%)
- ✅ 架构不过度复杂
- ✅ 维护成本可控

**改动范围**:
- Pattern 列表扩充 (35 → 200+)
- 规则引擎增加 AST 模式 (可选触发)
- 规则格式增加元数据
- 结果格式增加来源标记

---

## 🚀 实施步骤

### Step 1: Pattern 增强 (Day 1-2)
```python
# 转化 Semgrep 规则为 patterns
python3 transform_semgrep_to_patterns.py \
    --semgrep-rules semgrep-rules/python/ \
    --output rules/v580_patterns_enhanced.yaml
```

### Step 2: 规则引擎扩展 (Day 3-5)
```python
# 增加 AST 模式
python3 add_ast_mode.py \
    --current src/engines/rule_engine.py \
    --bandit-logic bandit/plugins/ \
    --output src/engines/rule_engine_enhanced.py
```

### Step 3: 规则格式兼容 (Day 6)
```python
# 更新规则格式
python3 update_rule_format.py \
    --rules rules/v580_current.yaml \
    --add-metadata "source,confidence,ast_check" \
    --output rules/v580_enhanced.yaml
```

### Step 4: 测试验证 (Day 7-8)
```python
# 全量测试
python3 benchmark.py \
    --scanner src/engines_enhanced/ \
    --rules rules/v580_enhanced.yaml \
    --samples ~/skills/ \
    --output reports/enhanced_benchmark.json
```

---

## 💡 结论

**需要调整，但不需要完全兼容**:

1. **Pattern 匹配**: 扩充到 200+ (Semgrep 转化) ✅ 必须
2. **规则引擎**: 增加 AST 模式 (仅可疑文件触发) ✅ 推荐
3. **规则格式**: 增加来源元数据 ✅ 推荐
4. **结果合并**: 标记规则来源 ✅ 推荐

**不需要**:
- ❌ 完全兼容 Semgrep 语法
- ❌ 完全兼容 Bandit AST 系统
- ❌ 完全兼容 Trivy Rego
- ❌ 依赖外部工具运行时

**保持**:
- ✅ v5.8.0 核心架构
- ✅ 高速扫描能力
- ✅ 零依赖特性
- ✅ 统一管理

---

**状态**: 兼容性分析完成
**建议**: 采用混合模式，适度调整
