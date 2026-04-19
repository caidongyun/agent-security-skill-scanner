# 集成扫描器批量测试报告

**时间**: 2026-04-08 21:45  
**测试样本**: 100 个 Skills（随机抽样）  
**检测方式**: 完整检测（基础 + AST + LLM）

---

## 📊 测试结果

### 集成扫描器判定分布

| 判定 | 数量 | 占比 |
|------|------|------|
| **SAFE** | 66 | 66.0% |
| **SUSPICIOUS** | 15 | 15.0% |
| **MALICIOUS** | 19 | 19.0% |

### 官方判定对比

| 来源 | 恶意占比 |
|------|---------|
| **官方** | 1.2% |
| **集成扫描器** | 19.0% |

**差异**: 集成扫描器过度敏感 **15.8 倍**！

---

## ⚠️ 问题分析

### 问题 1: 仍然过于敏感

**表现**: 19.0% 判定为 MALICIOUS，官方仅 1.2%

**原因**:
- AST 意图检测是简化版（非真实 AST）
- LLM 分析是规则模拟（非真实 LLM）
- 基础扫描规则过于敏感

---

### 问题 2: 缺少真实 AST 分析

**当前实现**:
```python
def _simple_ast_detector(self, skill_path):
    # 只是检查文件名，不是真实 AST
    is_install_script = file_name in ['install.sh', ...]
```

**应该实现**:
```python
# 真实 AST 分析代码意图
ast_tree = parse_python_code(content)
if has_malicious_ast_pattern(ast_tree):
    verdict = 'MALICIOUS'
```

---

### 问题 3: 缺少真实 LLM 调用

**当前实现**:
```python
def _simple_llm_analyzer(self, skill_path, base_result):
    # 只是规则模拟，不是真实 LLM
    if is_official:
        verdict = 'SUSPICIOUS'
```

**应该实现**:
```python
# 调用 OpenClaw LLM
llm_result = call_openclaw_llm(prompt)
verdict = llm_result['verdict']
```

---

## 🎯 下一步优化

### 方案 1: 集成真实 AST 分析器

**实施**:
```bash
# 使用真实 Python AST 分析
python3 -c "import ast; ast.parse(code)"
```

**预期**: 准确率提升至 85%+

---

### 方案 2: 集成真实 LLM

**实施**:
```bash
# 调用 OpenClaw LLM API
python3 llm_skill_judge.py /path/to/skill --enable-llm
```

**预期**: 准确率提升至 90%+

---

### 方案 3: 降低基础扫描敏感度

**实施**:
```python
# 提高阈值
if malicious_files >= 3:
    verdict = 'MALICIOUS'
```

**预期**: 误报降低 50%+

---

## 📋 结论

**集成扫描器架构正确**（基础 + AST + LLM），但需要：
1. ✅ 集成真实 AST 分析器
2. ✅ 集成真实 LLM 调用
3. ✅ 降低基础扫描敏感度

**当前状态**: 架构完成，组件待完善  
**预期效果**: 完整实现后一致率>85%，误报率<10%

---

**测试完成！集成扫描器架构正确，需要集成真实 AST 和 LLM 组件。** 📊
