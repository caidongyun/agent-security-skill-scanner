# 🔧 Skill Scanner 规则优化方案

## 一、问题总结

### 1.1 测试失败根因
| 问题 | 位置 | 原因 |
|------|------|------|
| 类型错误 | test_runner.py:189 | input 是 dict 不是 string |
| 规则分离 | test_runner.py:30-180 | 硬编码规则 vs 目录规则 |
| 无效规则 | rules/*.json | 规则格式与检测器不匹配 |

### 1.2 需要修复的文件
1. `tests/test_runner.py` - 修复输入类型处理
2. `tests/run_tests.py` - 统一测试入口
3. 规则加载逻辑 - 打通规则目录

---

## 二、修复计划

### 2.1 修复测试运行器

```python
# 修复 input 类型处理
def detect(self, input_data):
    # 处理 dict 类型的 input
    if isinstance(input_data, dict):
        input_text = input_data.get("content", "")
    else:
        input_text = str(input_data)
    
    # 继续检测...
```

### 2.2 统一规则加载

```python
# 从 rules/ 目录加载规则
def _load_rules_from_dir(self) -> Dict:
    rules = {}
    rules_dir = Path(__file__).parent.parent / "rules"
    
    for category_dir in rules_dir.iterdir():
        if category_dir.is_dir():
            category = category_dir.name
            rules[category] = []
            
            for rule_file in category_dir.rglob("*.json"):
                with open(rule_file) as f:
                    rule = json.load(f)
                    rules[category].append({
                        "id": rule["id"],
                        "pattern": rule["patterns"][0] if rule.get("patterns") else "",
                        "risk": rule.get("severity", "MEDIUM").upper()
                    })
    
    return rules
```

---

## 三、执行步骤

### Step 1: 修复测试运行器 (10 分钟)
- [ ] 修复 input 类型处理
- [ ] 添加规则目录加载
- [ ] 验证测试可以运行

### Step 2: 运行测试 (5 分钟)
- [ ] 运行完整测试套件
- [ ] 收集失败用例
- [ ] 分析检测率

### Step 3: 优化规则 (30 分钟)
- [ ] 补充缺失 patterns
- [ ] 优化正则表达式
- [ ] 调整风险评分

### Step 4: 质量验证 (15 分钟)
- [ ] 检测率 ≥ 95%
- [ ] 误报率 < 5%
- [ ] p99 延迟 < 50ms

---

## 四、预期效果

| 指标 | 当前 | 目标 |
|------|------|------|
| 检测率 | 0% (测试失败) | ≥95% |
| 误报率 | N/A | <5% |
| 规则数 | 128 条 | 扩展到 200+ |
| 测试覆盖 | 20+ 用例 | 100+ 用例 |

---

## 五、立即执行

```bash
cd ~/.openclaw/workspace/skills/agent-security-skill-scanner/expert_mode

# 运行测试
python3 tests/test_runner.py --verbose

# 预期输出:
# ❌ TypeError: expected string or bytes-like object, got 'dict'
```

现在开始修复？
