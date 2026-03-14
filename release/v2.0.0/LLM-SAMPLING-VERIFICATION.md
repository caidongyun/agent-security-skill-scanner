# 大模型抽样验证方案

> **创建日期**: 2026-03-13  
> **用途**: 使用大模型（Bailian/MiniMax）对扫描结果进行抽样验证

---

## 🎯 验证目标

使用大模型 AI 能力对扫描结果进行**智能抽样验证**，确保：
1. ✅ 恶意代码判定准确
2. ✅ 误报识别正确
3. ✅ 风险等级合理
4. ✅ 修复建议可行

---

## 📊 抽样策略

### 分层抽样

| 层级 | 抽样比例 | 样本数 | 验证重点 |
|------|----------|--------|----------|
| **严重** | 100% | 全部 | 关键恶意代码 |
| **高危** | 10% | ~1,800 | 主要威胁 |
| **中危** | 1% | ~600 | 可疑模式 |
| **低危** | 0.1% | ~150 | 轻微问题 |
| **无问题** | 0.1% | ~150 | 误报检查 |

**总计**: ~2,850 个样本

---

## 🔧 验证流程

### 1. 扫描样本

```bash
python3 release/v2.0.0/scanner_cli.py scan \
  scripts/samples/ \
  --threads 16 \
  --output release/v2.0.0/test-results/full-scan-result.json
```

### 2. 抽样

```python
import json
import random

# 读取扫描结果
with open('test-results/full-scan-result.json', 'r') as f:
    results = json.load(f)

# 分层抽样
samples = {
    'critical': random.sample(results['critical_issues'], min(100, len(results['critical_issues']))),
    'high': random.sample(results['high_issues'], min(500, len(results['high_issues']))),
    'medium': random.sample(results['medium_issues'], min(200, len(results['medium_issues']))),
    'low': random.sample(results['low_issues'], min(50, len(results['low_issues']))),
}

# 保存抽样结果
with open('test-results/sampled-for-llm.json', 'w') as f:
    json.dump(samples, f, indent=2)
```

### 3. 大模型验证

**提示词模板**:

```
你是一个代码安全专家。请分析以下代码是否存在安全风险：

## 代码
```python
{code_snippet}
```

## 扫描器判定
- 风险等级：{severity}
- 检测规则：{rule_id}
- 问题描述：{description}

## 分析任务
请回答：
1. 扫描器判定是否准确？(准确/误报/漏报)
2. 风险等级是否合理？(合理/过高/过低)
3. 详细理由
4. 修复建议（如有风险）

请以 JSON 格式返回：
{
  "verdict": "准确/误报/漏报",
  "severity_assessment": "合理/过高/过低",
  "reasoning": "...",
  "suggestion": "..."
}
```

### 4. 结果比对

```python
# 比对扫描器结果和 LLM 判定
def compare_results(scanner_result, llm_result):
    if llm_result['verdict'] == '准确':
        return True
    else:
        return False

# 计算准确率
accuracy = sum(compare_results(s, l) for s, l in zip(scanner_results, llm_results)) / len(scanner_results)
print(f"扫描器准确率：{accuracy:.2%}")
```

---

## 📈 验证指标

| 指标 | 计算方法 | 目标值 |
|------|----------|--------|
| **准确率** | 准确数/总抽样数 | >95% |
| **误报率** | 误报数/总抽样数 | <5% |
| **漏报率** | 漏报数/总抽样数 | <5% |
| **等级准确率** | 等级合理数/总抽样数 | >90% |

---

## 🤖 大模型选择

### 推荐模型

| 模型 | 适用场景 | 成本 |
|------|----------|------|
| **Bailian Qwen-Max** | 深度分析 | 中 |
| **MiniMax-M2.5** | 批量验证 | 低 |
| **Claude** | 复杂推理 | 高 |

### 配置

```json
{
  "llm_provider": "bailian",
  "llm_model": "qwen-max",
  "max_tokens": 1000,
  "temperature": 0.1,
  "batch_size": 100,
  "timeout": 30
}
```

---

## 📝 验证报告模板

```markdown
# 大模型抽样验证报告

## 抽样统计
- 严重：100 个（100%）
- 高危：500 个（10%）
- 中危：200 个（1%）
- 低危：50 个（0.1%）
- 无问题：50 个（0.1%）
- **总计**: 900 个

## 验证结果
- 准确率：97.5% ✅
- 误报率：1.2% ✅
- 漏报率：1.3% ✅
- 等级准确率：94.8% ✅

## 误报分析
### 误报案例 1
**文件**: example.py:42
**扫描器判定**: 高危 - eval 滥用
**LLM 判定**: 误报 - 安全的配置加载
**理由**: eval 用于解析配置字符串，非用户输入

### 误报案例 2
...

## 结论
✅ 扫描器 v2.0.0 通过大模型验证，可以发布
```

---

## 🔗 集成到测试流程

### 自动化脚本

```bash
#!/bin/bash
# run-llm-verification.sh

# 1. 扫描
python3 scanner_cli.py scan scripts/samples/ --output full-scan-result.json

# 2. 抽样
python3 scripts/sample_for_llm.py full-scan-result.json sampled-for-llm.json

# 3. 大模型验证
python3 scripts/llm_verify.py sampled-for-llm.json llm-verification-result.json

# 4. 生成报告
python3 scripts/generate_verification_report.py llm-verification-result.json
```

---

## ✅ 固定测试环节

### 发布前必做

- [x] 全量扫描测试
- [x] 性能测试
- [x] 误报率测试
- [ ] **大模型抽样验证** ⭐ 新增

### 验证频率

| 场景 | 频率 | 抽样数 |
|------|------|--------|
| **日常开发** | 每次提交 | 100 个 |
| **版本发布** | 每个版本 | 900 个 |
| **规则更新** | 每次更新 | 200 个 |
| **定期审查** | 每月 | 500 个 |

---

*方案创建：2026-03-13*  
*维护人：Security Team*
