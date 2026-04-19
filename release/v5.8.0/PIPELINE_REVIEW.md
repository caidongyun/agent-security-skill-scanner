# v5.8.0 Scanner 管线信息详解

**文档版本**: 1.0  
**最后更新**: 2026-04-14  
**适用范围**: v5.8.0 Scanner

---

## 🏗️ 一、检测架构全景图

### 1.1 系统架构

```
┌──────────────────────────────────────────────────────────────────┐
│                        用户调用层                                 │
│  smart_scan_clawhub.py | scan_all_skills.py | detection_rate_... │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                        Scanner 主类                               │
│  Scanner (src/engines/__init__.py)                               │
│  - scan_file(file_path) → ScanResult                             │
│  - _evaluate(pattern, rule, weight) → (risk, score, types)       │
└──────────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────┴─────────────────────┐
        ↓                                           ↓
┌──────────────────┐                    ┌──────────────────┐
│  PatternEngine   │                    │   RuleEngine     │
│  (Layer 1)       │                    │   (Layer 2)      │
│  - 104 patterns  │                    │   - 797 rules    │
│  - ~0.05ms/file  │                    │   - ~0.5ms/file  │
│  - 权重 8-60     │                    │   - 置信度 40-95 │
└──────────────────┘                    └──────────────────┘
        ↓                                           ↓
        └─────────────────────┬─────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                      Layer 3: 综合评估                            │
│  - 合并 Pattern + Rule 结果                                      │
│  - 计算最终分数 (0-100)                                          │
│  - 判定风险等级 (SAFE/LOW/MEDIUM/HIGH/CRITICAL)                  │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                        结果输出层                                 │
│  ScanResult (dataclass) → JSON/Markdown 报告                     │
└──────────────────────────────────────────────────────────────────┘
```

### 1.2 数据流

```
文件路径 (Path)
    ↓
[Scanner.scan_file]
    ↓
读取文件内容 (UTF-8)
    ↓
┌─────────────────────────────────────┐
│  并行执行                            │
│  ├→ PatternEngine.scan(content)     │
│  │   → [(type, pattern, weight)]    │
│  │   → max_weight                   │
│  └→ RuleEngine.scan(content, 60)    │
│      → [(id, category, pattern, c)] │
└─────────────────────────────────────┘
    ↓
Scanner._evaluate(pattern_matches, rule_matches, pattern_weight)
    ↓
(risk_level, score, attack_types)
    ↓
构建 ScanResult 对象
    ↓
返回 ScanResult
```

---

## 🔄 二、扫描流程详解

### 2.1 单文件扫描流程

```python
# 1. 初始化 Scanner
scanner = Scanner()
#    ↓
#    - 创建 PatternEngine (编译 104 个正则)
#    - 创建 RuleEngine (加载并编译 797 条规则)
#    - 初始化统计计数器

# 2. 扫描文件
result = scanner.scan_file(file_path)
#    ↓
#    a. 读取文件内容
#    b. Layer 1: Pattern 扫描
#       - 遍历 104 个 pattern
#       - 正则匹配
#       - 去重
#       - 返回匹配列表 + max_weight
#    c. Layer 2: Rule 扫描
#       - 遍历 797 条规则
#       - 检查置信度 >= 60
#       - 正则匹配
#       - 去重
#       - 返回匹配列表
#    d. Layer 3: 综合评估
#       - 合并攻击类型
#       - 计算分数：max(pattern_weight, rule_confidence) + type_bonus
#       - 判定风险等级
#    e. 构建结果对象
#       - ScanResult(score, risk_level, attack_types, ...)

# 3. 处理结果
if result.is_malicious:
    # 标记为恶意
elif result.score >= 30:
    # 标记为可疑
else:
    # 标记为安全
```

### 2.2 多文件扫描流程（智能扫描）

```python
# 1. 发现技能文件夹
skill_folders = [d for d in skills_path.iterdir() if d.is_dir()]
#    → 17,483 个文件夹

# 2. 创建线程池
with ThreadPoolExecutor(max_workers=8) as executor:
    # 3. 提交任务
    future_to_folder = {
        executor.submit(scan_with_own_scanner, f): f 
        for f in skill_folders
    }
    #    → 每个任务独立创建 Scanner 实例
    
    # 4. 收集结果
    for future in as_completed(future_to_folder):
        result = future.result()
        #    → scan_skill_folder() 扫描文件夹内所有关键文件
        #    → 综合评估整个技能的风险
```

### 2.3 技能文件夹扫描流程

```
技能文件夹/
├── SKILL.md          ← 扫描 ✅
├── main.py           ← 扫描 ✅
├── utils.js          ← 扫描 ✅
├── config.yaml       ← 扫描 ✅
└── README.md         ← 跳过 ❌

扫描过程:
1.  glob 匹配关键文件 (*.md, *.py, *.js, *.yaml, *.json, etc.)
2.  对每个文件调用 scanner.scan_file()
3.  综合所有文件结果:
    - final_score = max_score + avg_score * 0.3
    - is_malicious = final_score >= 70 or max_score >= 90
4.  返回技能综合风险评估
```

---

## 📦 三、核心对象详解

### 3.1 ScanResult (数据类)

```python
@dataclass
class ScanResult:
    """扫描结果"""
    file_path: str              # 文件路径
    is_malicious: bool          # 是否恶意
    risk_level: str             # 风险等级 (SAFE/LOW/MEDIUM/HIGH/CRITICAL)
    score: int                  # 分数 (0-100)
    attack_types: List[str]     # 攻击类型列表
    matched_patterns: List[Dict]  # 匹配的 Pattern
    matched_rules: List[Dict]     # 匹配的规则
    scan_time_ms: float         # 扫描耗时 (毫秒)
    
    def to_dict(self) -> Dict:
        """转换为字典（用于 JSON 序列化）"""
        return asdict(self)
```

**使用示例**:
```python
result = scanner.scan_file('skill/main.py')
print(f"文件：{result.file_path}")
print(f"分数：{result.score}")
print(f"风险：{result.risk_level}")
print(f"恶意：{result.is_malicious}")
print(f"攻击类型：{result.attack_types}")
print(f"匹配 Pattern: {len(result.matched_patterns)}")
print(f"匹配规则：{len(result.matched_rules)}")
print(f"耗时：{result.scan_time_ms:.2f}ms")
```

### 3.2 PatternEngine

```python
class PatternEngine:
    """Pattern 引擎 - Layer 1"""
    
    # 类常量：104 个攻击模式
    ATTACK_PATTERNS: List[Tuple[str, str, int]] = [
        # (攻击类型，正则表达式，权重)
        ("credential_theft", r'\.ssh/', 40),
        ("credential_theft", r'\.aws/', 40),
        ("prompt_injection", r'ignore\s+previous', 45),
        # ... 共 104 个
    ]
    
    # 实例属性
    compiled: List[Tuple]  # 编译后的正则 [(type, compiled_regex, pattern, weight)]
    max_weight: int        # 最大权重值
    
    # 核心方法
    def scan(self, content: str) -> Tuple[List[Tuple], int]:
        """
        扫描内容
        返回：(匹配列表，最大权重)
        匹配列表格式：[(attack_type, pattern, weight), ...]
        """
```

**Pattern 分类统计**:

| 攻击类型 | Pattern 数量 | 权重范围 |
|---------|-------------|----------|
| credential_theft | 9 | 8-40 |
| data_exfiltration | 8 | 15-50 |
| prompt_injection | 4 | 35-45 |
| reverse_shell | 3 | 55-60 |
| arbitrary_execution | 4 | 10-20 |
| obfuscation | 4 | 10-30 |
| supply_chain_attack | 3 | 45-60 |
| persistence | 3 | 30-35 |
| evasion | 12 | 20-40 |
| resource_exhaustion | 9 | 30-50 |
| memory_pollution | 8 | 35-50 |
| false_prone | 20 | 30-60 |
| tool_poisoning | 5 | 30-50 |
| common_pattern | 4 | 25-35 |
| **总计** | **104** | **8-60** |

### 3.3 RuleEngine

```python
class RuleEngine:
    """Rule 引擎 - Layer 2"""
    
    # 实例属性
    rules_file: Path           # 规则文件路径
    extra_rules_file: Path     # 额外规则文件
    rules: List[Dict]          # 规则列表（原始 JSON）
    compiled: List[Tuple]      # 编译后的规则
    
    # 核心方法
    def load(self) -> bool:
        """加载并编译规则"""
        
    def scan(self, content: str, min_confidence: int = 60) -> List[Tuple]:
        """
        扫描内容
        返回：[(rule_id, category, pattern, confidence), ...]
        """
```

**规则来源**:

| 来源 | 文件路径 | 规则数 |
|------|---------|--------|
| 主规则 | `release/v5.7.0/src/rules/cleaned/high_value_rules.json` | ~750 |
| 额外规则 | `release/v5.8.0/rules/evasion_rules.json` | ~47 |
| **总计** | | **~797** |

**规则置信度分布**:

| 置信度 | 等级 | 数量 | 说明 |
|--------|------|------|------|
| 95 | critical | ~150 | 明确恶意 |
| 80 | high | ~250 | 高度可疑 |
| 60 | medium | ~300 | 中等风险 |
| 40 | low | ~97 | 低风险（不编译） |

### 3.4 Scanner

```python
class Scanner:
    """主扫描器 - 协调 Pattern 和 Rule 引擎"""
    
    # 类常量
    VERSION = "v5.8.0"
    SCANNER_NAME = "agent-security-skill-scanner"
    
    # 实例属性
    version: str                    # 版本号
    pattern_engine: PatternEngine   # Pattern 引擎实例
    rule_engine: RuleEngine         # Rule 引擎实例
    stats: Dict                     # 统计信息
    
    # 核心方法
    def scan_file(self, file_path: Path) -> ScanResult:
        """扫描单个文件"""
        
    def _evaluate(self, pattern_matches, rule_matches, pattern_weight) 
        -> Tuple[str, int, List[str]]:
        """综合评估"""
```

**统计信息**:

```python
scanner.stats = {
    'files_scanned': 0,    # 已扫描文件数
    'threats_found': 0,    # 发现威胁数
    'pattern_hits': 0,     # Pattern 命中数
    'rule_hits': 0         # Rule 命中数
}
```

---

## ⚙️ 四、配置要点

### 4.1 关键阈值

| 参数 | 默认值 | 说明 | 调整建议 |
|------|--------|------|----------|
| `min_confidence` | 60 | Rule 最低置信度 | 降低→检出率↑误报↑ |
| `pattern_weight` | 8-60 | Pattern 权重范围 | 建议标准化为 10-50 |
| `type_bonus` | 3 | 每种攻击类型加分 | 当前：min(types*3, 10) |
| `max_score` | 100 | 最高分数 | 不建议调整 |

### 4.2 风险等级阈值

```python
if score >= 90 or rule_score >= 95:
    risk_level = "CRITICAL"
elif score >= 70:
    risk_level = "HIGH"
elif score >= 30:
    risk_level = "MEDIUM"
elif score >= 25:  # 新增
    risk_level = "LOW"
else:
    risk_level = "SAFE"
```

**判定逻辑**:
- `is_malicious` = risk_level in ("MEDIUM", "HIGH", "CRITICAL")
- `is_suspicious` = risk_level == "LOW" (如有)
- `is_safe` = risk_level == "SAFE"

### 4.3 文件限制

| 限制项 | 当前值 | 建议值 |
|--------|--------|--------|
| 最大文件大小 | 无限制 | 10MB |
| 支持编码 | UTF-8 (errors='ignore') | UTF-8 + Latin-1 fallback |
| 超时限制 | 无 | 30 秒/文件 |

---

## 📊 五、性能指标

### 5.1 单文件扫描性能

| 阶段 | 耗时 | 占比 |
|------|------|------|
| 文件 I/O | ~1.2ms | 60% |
| Pattern 匹配 | ~0.05ms | 2.5% |
| Rule 匹配 | ~0.5ms | 25% |
| 评估 + 序列化 | ~0.25ms | 12.5% |
| **总计** | **~2ms** | **100%** |

### 5.2 多线程扫描性能

| 线程数 | 速度 (skills/s) | 内存 (MB) |
|--------|----------------|-----------|
| 1 | 80 | 3 |
| 4 | 280 | 12 |
| 8 | 482 | 24 |
| 16 | 650 | 48 |

**最佳配置**: 8 线程（性能/资源平衡）

### 5.3 大规模扫描统计

| 扫描项目 | 样本数 | 耗时 | 速度 |
|---------|--------|------|------|
| Benchmark 全量 | 13,100 | 3min | 4,366/min |
| ClawHub Skills | 17,483 | 36s | 482/s |
| 单文件测试 | 1 | 2ms | - |

---

## 🔧 六、常见问题

### 6.1 为什么 Pattern 命中但 Rule 没命中？

**原因**: Rule 的 `min_confidence=60`，只有置信度≥60 的规则才会匹配。

**解决**: 降低 `min_confidence` 阈值（但可能增加误报）。

### 6.2 为什么分数相同但风险等级不同？

**原因**: 风险等级还考虑了 `rule_score`。

```python
if score >= 90 or rule_score >= 95:
    risk_level = "CRITICAL"  # 即使 score<90，rule_score>=95 也是 CRITICAL
```

### 6.3 为什么多线程扫描比单线程快？

**原因**: 
- 每线程独立 Scanner 实例，无锁竞争
- I/O 并行化（8 线程同时读取文件）
- CPU 多核并行（正则匹配）

### 6.4 如何添加自定义规则？

**方法 1**: 修改 `ATTACK_PATTERNS` 列表（需重新编译）

**方法 2**: 添加 JSON 规则文件，传给 `RuleEngine(rules_file=path)`

**方法 3** (推荐): 使用外部规则配置文件

```yaml
# rules.yaml
patterns:
  - type: "custom_attack"
    pattern: "malicious_pattern"
    weight: 40
```

---

## 📝 七、最佳实践

### 7.1 扫描技能文件夹

```python
from smart_scan_clawhub import smart_scan

smart_scan(
    skills_dir='/path/to/skills',
    output_json='report.json',
    output_md='report.md',
    max_workers=8
)
```

### 7.2 扫描单个文件

```python
from src.engines import Scanner

scanner = Scanner()
result = scanner.scan_file('file.py')

if result.is_malicious:
    print(f"⚠️ 恶意文件！Score: {result.score}")
    print(f"攻击类型：{result.attack_types}")
```

### 7.3 批量扫描 + 进度显示

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def scan_with_own_scanner(file_path):
    s = Scanner()
    return s.scan_file(file_path)

with ThreadPoolExecutor(max_workers=8) as executor:
    futures = [executor.submit(scan_with_own_scanner, f) for f in files]
    
    for i, future in enumerate(as_completed(futures), 1):
        result = future.result()
        if i % 1000 == 0:
            print(f"进度：{i}/{len(files)}")
```

### 7.4 性能优化建议

1. **使用多线程** - 8 线程最佳
2. **复用 Scanner** - 单线程场景下复用实例
3. **限制文件大小** - 跳过>10MB 文件
4. **批量 I/O** - 预读取文件内容
5. **结果缓存** - 相同文件不重复扫描

---

*本文档由 v5.8.0 Scanner 架构分析生成*
*最后更新：2026-04-14 12:05*
