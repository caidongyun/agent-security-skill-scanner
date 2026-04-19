# v5.9.0 架构设计决策记录

**日期**: 2026-04-14  
**版本**: v5.9.0  
**设计原则**: 准确性优先，LLM 可选，串行执行

---

## 📐 架构设计

### 核心流程

```
文件/文件夹
    ↓
┌─────────────────────────────────────┐
│  Layer 1: Pattern Engine            │
│  - 完整扫描所有 pattern (100+)      │
│  - 返回：命中列表 + 攻击类型        │
└─────────────────────────────────────┘
    ↓ (传递完整结果)
┌─────────────────────────────────────┐
│  Layer 2: Rule Engine               │
│  - 完整扫描所有 rules (50-100)      │
│  - 可参考 L1 结果进行针对性检测     │
│  - 返回：命中列表 + 置信度          │
└─────────────────────────────────────┘
    ↓ (传递完整结果)
┌─────────────────────────────────────┐
│  Layer 3: 综合评估                  │
│  - 合并 L1 + L2 结果                 │
│  - 计算分数 + 风险等级              │
│  - 生成证据链                       │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Layer 4: LLM (可选)                │
│  - 仅当 L2 判定为可疑/恶意时触发    │
│  - 批量扫描：默认关闭               │
│  - 用户个别扫描：可开启             │
│  - 语义确认 + 误报过滤              │
└─────────────────────────────────────┘
    ↓
ScanResult (完整结果对象)
```

---

## 🎯 关键设计决策

### 1. 串行执行 vs 并行执行

**决策**: **串行执行** ✅

**原因**:
- 每层都能获取前层的完整信息
- Rule Engine 可以针对性扫描 L1 命中的类型
- LLM 可以基于前两层的证据进行确认
- 准确性优先于性能

**实现**:
```python
# Layer 1: 完整 Pattern 扫描
layer1_result = self.pattern_engine.scan(content)

# Layer 2: 完整 Rule 扫描 (可使用 L1 结果)
layer2_result = self.rule_engine.scan(content, layer1_result)

# Layer 3: 综合评估
assessment = self._assess(layer1_result, layer2_result)

# Layer 4: LLM 确认 (可选，仅当可疑/恶意时)
if assessment['is_suspicious'] and llm_enabled:
    layer4_result = self.llm_engine.confirm(content, assessment)
```

### 2. LLM 定位

**决策**: **可选 Layer 4，仅在可疑/恶意时触发** ✅

**原因**:
- LLM 长期来看成本会降低
- 批量扫描时不需要（性能考虑）
- 用户个别扫描时可以开启（准确性考虑）
- 仅对可疑/恶意样本进行确认（成本优化）

**触发条件**:
```python
# 批量扫描 (默认关闭 LLM)
scanner = Scanner(llm_enabled=False)

# 用户个别扫描 (可开启 LLM)
scanner = Scanner(llm_enabled=True, llm_config={...})

# LLM 仅在以下情况触发:
if (layer2_result['is_suspicious'] or layer2_result['is_malicious']) 
   and llm_enabled:
    layer4_result = llm_engine.confirm(...)
```

### 3. Pattern vs Rule 关系

**决策**: **独立扫描，串行执行，汇总判断** ✅

**原因**:
- Pattern 是单层正则匹配（快速）
- Rule 是多层条件组合（准确）
- 两者独立扫描，避免遗漏
- 串行执行，Rule 可参考 Pattern 结果
- 汇总判断，综合评分

**区别**:
| 特性 | Pattern | Rule |
|------|---------|------|
| **匹配方式** | 单层正则 | 多条件组合 |
| **数量** | 100+ | 50-100 |
| **速度** | 快 (~0.05ms) | 中 (~0.5ms) |
| **准确性** | 中 | 高 |
| **误报率** | 高 | 低 |
| **作用** | 初筛 | 确认 |

### 4. 结果对象设计

**决策**: **包含各层完整结果 + 综合评估** ✅

```python
@dataclass
class ScanResult:
    # 基本信息
    target: str
    target_type: str  # 'file' or 'folder'
    
    # 核心判断
    is_malicious: bool
    confidence: str  # 'high'/'medium'/'low'
    
    # 风险评分
    score: int
    risk_level: str
    
    # 威胁信息
    threats: List[str]
    threat_types: List[str]
    
    # 各层结果 (完整保留)
    layer1_pattern: Dict  # Pattern 完整结果
    layer2_rule: Dict     # Rule 完整结果
    layer4_llm: Dict      # LLM 结果 (如有)
    
    # 证据链
    evidence: List[Dict]  # 所有匹配的规则/pattern
    
    # 摘要
    summary: str
```

---

## 🔍 关于 AST

### 什么是 AST？

**AST = Abstract Syntax Tree (抽象语法树)**

是一种**代码结构分析技术**，比正则/规则更深入。

### AST vs Rule Engine

| 特性 | Rule Engine | AST Engine |
|------|-------------|------------|
| **分析层级** | 文本/正则 | 语法树 |
| **检测能力** | 模式匹配 | 语义理解 |
| **示例** | `eval\s*\(` | 检测"动态执行用户输入" |
| **优点** | 快速、简单 | 准确、理解语义 |
| **缺点** | 易误报 | 慢、复杂 |
| **适用** | 已知攻击模式 | 未知/混淆攻击 |

### 示例对比

**检测"执行用户输入"**:

```python
# Rule Engine (正则匹配)
r'eval\s*\('  # 匹配 eval() 调用
r'exec\s*\('  # 匹配 exec() 调用

# AST Engine (语法树分析)
# 分析代码结构，检测是否"动态执行用户输入"
def detect_dynamic_exec(ast_tree):
    for node in ast_tree.walk():
        if node.type == 'Call':
            if node.func in ['eval', 'exec']:
                if node.args[0].is_user_input():  # 语义分析
                    return True  # 检测到动态执行用户输入
    return False
```

### AST 是否包含在 Rule Engine 里？

**不包含**。AST 是独立的检测层，可以作為：

**方案 A**: 作为 Rule Engine 的增强
```python
class RuleEngine:
    def scan(self, content, ast_tree=None):
        # 先用正则匹配
        rule_hits = self.regex_scan(content)
        
        # 如果有 AST，再用 AST 确认
        if ast_tree:
            ast_hits = self.ast_scan(ast_tree)
            rule_hits = self.merge(rule_hits, ast_hits)
        
        return rule_hits
```

**方案 B**: 作为独立 Layer 3
```
Layer 1: Pattern (正则)
    ↓
Layer 2: Rule (多条件组合)
    ↓
Layer 3: AST (语法树分析) ← 新增
    ↓
Layer 4: 综合评估
    ↓
Layer 5: LLM (可选)
```

### 是否需要 AST？

**短期**: 不需要，Rule Engine 已经足够

**长期**: 可以考虑，用于检测：
- 混淆代码
- 未知攻击模式
- 语义级恶意行为

---

## 📋 实施计划

### Phase 1: 基础架构 (当前)
- [x] Pattern Engine (100+ patterns)
- [x] Rule Engine (50-100 rules)
- [x] 串行执行
- [x] 综合评估

### Phase 2: LLM 集成 (可选)
- [ ] LLM API 封装
- [ ] 触发条件控制
- [ ] 成本优化

### Phase 3: AST 引擎 (长期)
- [ ] AST 解析器
- [ ] 语义检测规则
- [ ] 与 Rule Engine 集成

---

## 📊 性能对比

| 配置 | 速度 | 准确性 | 成本 |
|------|------|--------|------|
| Pattern only | 快 | 中 | 低 |
| Pattern + Rule | 中 | 高 | 低 |
| Pattern + Rule + LLM | 慢 | 很高 | 中 |
| Pattern + Rule + AST | 慢 | 很高 | 低 |
| Full (Pattern+Rule+AST+LLM) | 很慢 | 最高 | 中 |

**推荐配置**:
- **批量扫描**: Pattern + Rule
- **用户个别扫描**: Pattern + Rule + LLM (可选)
- **高精度需求**: Pattern + Rule + AST + LLM

---

*本文档记录 v5.9.0 架构设计决策*
*最后更新：2026-04-14*
