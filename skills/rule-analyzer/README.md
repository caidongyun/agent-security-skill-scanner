# 多模型规则分析器 (Multi-Model Rule Analyzer)

**目标**: 使用多个 LLM 交叉分析规则质量，减少人工审核工作量

---

## 🔧 功能

1. **规则意图分析** - 理解规则检测什么
2. **误报风险评估** - 高/中/低
3. **漏报风险评估** - 高/中/低
4. **优化建议** - 具体改进方案
5. **置信度评分** - 0-100 分

---

## 🤖 支持模型

- GPT-4 / GPT-4o
- Claude 3 / Claude 3.5
- Qwen (通义千问)
- MiniMax

---

## 📊 分析流程

```
规则 → 多模型分析 → 结果聚合 → 共识决策
       ├─ GPT-4
       ├─ Claude
       ├─ Qwen
       └─ MiniMax
       
共识规则:
- 3+ 模型一致 → 自动通过
- 2 模型一致 → 人工复核
- 无共识 → 人工审核
```

---

## 🚀 使用

```bash
# 分析单条规则
python3 analyze_rule.py --rule "rule_name"

# 批量分析
python3 batch_analyze.py --rules rules/optimized/ --models 4

# 生成报告
python3 generate_report.py --output reports/rule_quality.md
```

---

## 📁 输出

```
rules/reviewed/
├── L1_auto_approved/    # 自动通过
├── L2_human_review/     # 人工复核
├── L3_human_review/     # 人工审核
└── analysis_reports/    # 分析报告
```
