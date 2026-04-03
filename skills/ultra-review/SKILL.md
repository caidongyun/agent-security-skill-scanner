---
name: UltraReview
version: 2.0.0
category: quality-assurance
author: ClawHub Community
description: 深度审查 Agent - 代码/决策/规划全方位审查
---

# UltraReview - 深度审查 Agent

提供代码、决策、规划的全方位深度审查，确保高质量输出。

## 核心能力

1. **代码审查** - 深度代码质量分析
2. **决策审查** - 决策逻辑验证
3. **规划审查** - 规划合理性评估
4. **风险识别** - 潜在风险预警
5. **改进建议** - 具体优化建议

## 审查维度

| 维度 | 检查项 | 权重 |
|------|--------|------|
| **正确性** | 逻辑正确、无 Bug | 30% |
| **可靠性** | 异常处理、容错能力 | 25% |
| **可维护性** | 代码结构、注释文档 | 20% |
| **性能** | 时间/空间复杂度 | 15% |
| **安全性** | 安全漏洞、权限控制 | 10% |

## 使用方式

```bash
# 审查代码
python3 main.py --review code --target path/to/code.py

# 审查决策
python3 main.py --review decision --target decision.json

# 审查规划
python3 main.py --review plan --target plan.yaml

# 深度审查 (所有维度)
python3 main.py --review all --target path/to/target --deep
```

## 集成到 Auto-R&D 体系

```python
from ultra_review import UltraReview

reviewer = UltraReview()

# 在关键节点插入审查
result = reviewer.review(code, type='code')
if result['score'] < 0.8:
    # 低于 80 分，需要改进
    return result['suggestions']
```

## 输出格式

```json
{
  "score": 0.85,
  "level": "A",
  "issues": [
    {"type": "bug", "severity": "high", "description": "..."},
    {"type": "performance", "severity": "medium", "description": "..."}
  ],
  "suggestions": ["建议 1", "建议 2"],
  "passed": true
}
```
