# v6.0.0 规则集成到 v5.8.0 计划

**日期**: 2026-04-14  
**目标**: 将 v6.0.0 的外部规则资源集成到 v5.8.0，增强检测能力

---

## 📊 现状分析

### v5.8.0 (生产版本)
- ✅ 三层架构完整：PatternEngine + RuleEngine + LLMEngine
- ✅ 内置 Pattern: ~30 条
- ✅ 内置 Rule: 5 条高置信度规则
- ✅ 全量 Benchmark 通过：11 类恶意 100% 检测，3 类良性 0% 误报

### v6.0.0 (开发版本)
- 📦 外部规则资源：
  - `gitleaks.toml`: 50+ 条密钥检测规则
  - `ai/semgrep-rules/`: 112+ 条 Semgrep AI 规则（按语言分类）
  - `converted/semgrep_ai_patterns.json`: 已转换的 JSON 格式

### 集成策略
**不合并代码**（架构已一致），**只集成规则资源**：
1. Gitleaks 规则 → 转换为 PatternEngine 规则
2. Semgrep AI 规则 → 转换为 RuleEngine 规则
3. 保持 v5.8.0 架构不变

---

## 🎯 集成范围

### P0: Gitleaks 密钥检测 (今天)
- **来源**: `v6.0.0/external-rules/gitleaks.toml`
- **目标**: 转换为 PatternEngine 规则
- **预期**: 新增 30-50 条密钥检测 pattern
- **优先级**: 高危规则优先（1password, AWS, Azure, GitHub 等）

### P1: Semgrep AI 规则 (本周)
- **来源**: `v6.0.0/external-rules/ai/python/` (112 条中的 Python 子集)
- **目标**: 转换为 RuleEngine 规则
- **预期**: 新增 20-30 条 AI 安全规则
- **优先级**: Python 相关（当前主要扫描 Python skills）

### P2: 规则去重优化 (下周)
- **任务**: 检测并合并重复规则
- **目标**: 避免重复检测，提升性能
- **预期**: 规则总数控制在 100 条以内

---

## 📋 实施步骤

### Step 1: Gitleaks 规则转换 (P0)

#### 1.1 解析 gitleaks.toml
```python
# 脚本：scripts/convert_gitleaks_to_patterns.py
import toml

with open('v6.0.0/external-rules/gitleaks.toml') as f:
    config = toml.load(f)

rules = config['rules']
# 提取：id, description, regex, keywords, entropy
```

#### 1.2 转换为 PatternEngine 格式
```python
# 输出：rules/gitleaks_patterns.json
{
  "patterns": [
    {
      "attack_type": "credential_theft",
      "pattern": "\\bA3-[A-Z0-9]{6}-...",
      "weight": 55,
      "source": "gitleaks/1password-secret-key",
      "description": "1Password secret key"
    },
    ...
  ]
}
```

#### 1.3 集成到 PatternEngine
```python
# 修改：release/v5.8.0/src/engines/pattern_engine.py
def __init__(self):
    # 加载内置 patterns
    self.compiled = self._compile_builtin()
    
    # 加载 Gitleaks patterns
    self.compiled.extend(self._load_gitleaks())
    
    print(f"✅ PatternEngine: {len(self.compiled)} patterns " +
          f"(内置:{len(self._compile_builtin())}, Gitleaks:{len(self._load_gitleaks())})")
```

#### 1.4 测试验证
```bash
# 使用 v5.8.0 全量样本测试
cd release/v5.8.0
python3 scripts/convert_gitleaks_to_patterns.py
python3 benchmark_full_scan.py --samples ~/Desktop/security-benchmark/samples/from-templates/
```

**验收标准**:
- Gitleaks 规则加载成功
- 检测率 ≥95%（保持 v5.8.0 水平）
- 误报率 ≤5%
- 性能无明显下降

---

### Step 2: Semgrep AI 规则转换 (P1)

#### 2.1 解析 Semgrep 规则
```python
# 脚本：scripts/convert_semgrep_to_rules.py
import json

with open('v6.0.0/external-rules/converted/semgrep_ai_patterns.json') as f:
    patterns = json.load(f)

# 提取：pattern, message, severity, category
```

#### 2.2 转换为 RuleEngine 格式
```python
# 输出：rules/semgrep_ai_rules.json
{
  "rules": [
    {
      "id": "SEMGREP-AI-001",
      "name": "Hardcoded API Key",
      "category": "credential_theft",
      "patterns": [r"api[_-]?key\\s*=\\s*['\"][^'\"]{16,}"],
      "min_matches": 1,
      "confidence": 90,
      "source": "semgrep/python/hardcoded-api-key"
    },
    ...
  ]
}
```

#### 2.3 集成到 RuleEngine
```python
# 修改：release/v5.8.0/src/engines/rule_engine.py
def load_builtin_rules(self):
    # 加载内置 rules
    self.rules = self._load_builtin()
    
    # 加载 Semgrep AI rules
    self.rules.extend(self._load_semgrep_ai())
    
    self._compile_rules()
    
    print(f"✅ RuleEngine: {len(self.compiled)} rules " +
          f"(内置:{len(self._load_builtin())}, Semgrep:{len(self._load_semgrep_ai())})")
```

#### 2.4 测试验证
```bash
# 使用全量样本测试
python3 benchmark_full_scan.py --samples ~/Desktop/security-benchmark/samples/from-templates/
```

**验收标准**:
- Semgrep 规则加载成功
- 检测率 ≥98%
- 误报率 ≤3%

---

### Step 3: 规则去重与优化 (P2)

#### 3.1 规则去重
```python
# 脚本：scripts/deduplicate_rules.py
# 检测重复的 pattern
# 合并相同攻击类型的规则
```

#### 3.2 性能优化
- 预编译所有正则
- 建立规则索引（按攻击类型）
- 实现规则缓存

---

## 📁 文件变更清单

### 新增文件
- `release/v5.8.0/rules/gitleaks_patterns.json` (P0)
- `release/v5.8.0/rules/semgrep_ai_rules.json` (P1)
- `release/v5.8.0/scripts/convert_gitleaks_to_patterns.py` (P0)
- `release/v5.8.0/scripts/convert_semgrep_to_rules.py` (P1)
- `release/v5.8.0/scripts/deduplicate_rules.py` (P2)

### 修改文件
- `release/v5.8.0/src/engines/pattern_engine.py` (P0)
- `release/v5.8.0/src/engines/rule_engine.py` (P1)

### 不变文件
- `release/v5.8.0/src/engines/__init__.py` (Scanner 主类)
- `release/v5.8.0/src/engines/llm_engine.py`
- `release/v5.8.0/src/engines/ast_engine.py`

---

## ⏱️ 时间计划

| 阶段 | 任务 | 预计时间 | 状态 |
|------|------|----------|------|
| P0 | Gitleaks 规则转换 | 2-3 小时 | ⏳ 待开始 |
| P0 | 集成到 PatternEngine | 1 小时 | ⏳ 待开始 |
| P0 | 测试验证 | 1 小时 | ⏳ 待开始 |
| P1 | Semgrep AI 规则转换 | 3-4 小时 | ⏳ 待开始 |
| P1 | 集成到 RuleEngine | 1 小时 | ⏳ 待开始 |
| P1 | 测试验证 | 1 小时 | ⏳ 待开始 |
| P2 | 规则去重优化 | 2-3 小时 | ⏳ 待开始 |
| P2 | 性能优化 | 1-2 小时 | ⏳ 待开始 |
| **总计** | | **12-16 小时** | |

---

## 📊 预期效果

### 规则数量对比
| 来源 | 规则数 | 类型 |
|------|--------|------|
| 内置 Pattern | ~30 | 攻击模式 |
| Gitleaks | +30-50 | 密钥检测 |
| 内置 Rule | 5 | 高置信度规则 |
| Semgrep AI | +20-30 | AI 安全 |
| **总计** | **~85-115** | 混合 |

### 检测能力对比
| 指标 | v5.8.0 (当前) | v5.8.0+ (集成后) |
|------|---------------|------------------|
| 检测率 | 100% (11 类) | ≥100% (保持) |
| 误报率 | 0% (3 类) | ≤3% |
| 密钥检测 | 基础 | 增强 (50+ 规则) |
| AI 安全 | 基础 | 增强 (20+ 规则) |
| 性能 | ~2ms/file | ~2-3ms/file |

---

## 🚀 快速开始

### 立即执行 P0 (Gitleaks 集成)
```bash
cd ~/.openclaw/workspace/agent-security-skill-scanner-master

# 1. 创建转换脚本
mkdir -p release/v5.8.0/scripts
nano release/v5.8.0/scripts/convert_gitleaks_to_patterns.py

# 2. 运行转换
cd release/v5.8.0
python3 scripts/convert_gitleaks_to_patterns.py

# 3. 验证输出
cat rules/gitleaks_patterns.json | head -50

# 4. 集成到 PatternEngine
# (修改 pattern_engine.py，添加 _load_gitleaks() 方法)

# 5. 测试
python3 benchmark_full_scan.py --samples ~/Desktop/security-benchmark/samples/from-templates/
```

---

## ✅ 验收标准

### P0 验收
- [ ] Gitleaks 规则成功转换为 JSON 格式
- [ ] PatternEngine 加载 Gitleaks 规则
- [ ] 全量样本测试通过（检测率≥95%）
- [ ] 无性能回归

### P1 验收
- [ ] Semgrep AI 规则成功转换
- [ ] RuleEngine 加载 Semgrep 规则
- [ ] 全量样本测试通过（检测率≥98%）
- [ ] 误报率≤3%

### P2 验收
- [ ] 规则去重完成
- [ ] 规则总数≤100 条
- [ ] 性能优化完成（<3ms/file）

---

*集成计划文档*
*2026-04-14*
