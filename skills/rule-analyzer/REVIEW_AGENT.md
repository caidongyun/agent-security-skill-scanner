# 规则评审 Agent (Rule Review Agent)

**定位**: 独立的 LLM 驱动规则质量评审 Agent

---

## 🤖 使用模型

基于 OpenClaw 配置:
- **主模型**: `modelstudio/qwen3.5-plus` (通义千问)
- **备选**: `minimax/MiniMax-M2.7`
- **推理**: 启用深度思考模式

---

## 🎯 Agent 能力

### 1. 规则意图理解
- 解析 YARA 规则语法
- 识别检测目标 (攻击类型、行为特征)
- 映射到 MITRE ATLAS 框架

### 2. 误报风险评估
- 分析规则特异性
- 识别宽泛关键词
- 评估常见业务场景影响

### 3. 漏报风险评估
- 分析绕过可能性
- 评估覆盖全面性
- 识别检测盲区

### 4. 优化建议生成
- 添加例外条件
- 增强检测逻辑
- 多条件组合建议

### 5. 置信度评分
- 0-100 分量化评估
- 多维度加权计算
- 可解释性报告

---

## 🏗️ Agent 架构

```
┌─────────────────────────────────────┐
│     Rule Review Agent (主节点)       │
├─────────────────────────────────────┤
│  1. 规则解析器                       │
│     └─ YARA 语法分析                 │
│  2. 意图识别模块                     │
│     └─ LLM 语义理解                  │
│  3. 风险评估模块                     │
│     ├─ FP 风险分析                   │
│     └─ FN 风险分析                   │
│  4. 优化建议模块                     │
│     └─ LLM 生成建议                  │
│  5. 评分聚合模块                     │
│     └─ 多轮推理加权                  │
└─────────────────────────────────────┘
```

---

## 🔄 工作流程

```
规则输入
   ↓
[1] 语法解析 → 提取字符串、条件、元数据
   ↓
[2] 意图识别 → LLM 分析检测目标
   ↓
[3] FP 风险评估 → 分析宽泛程度
   ↓
[4] FN 风险评估 → 分析绕过可能性
   ↓
[5] 优化建议 → LLM 生成改进方案
   ↓
[6] 置信度评分 → 多维度加权
   ↓
[7] 决策建议 → approve/optimize/remove
   ↓
输出 JSON 报告
```

---

## 📝 输入输出

### 输入
```json
{
  "rule_name": "Shell_ReverseShell_Python",
  "rule_content": "rule ... { ... }",
  "source_file": "rules/optimized/l1_high_confidence.yar",
  "analysis_depth": "standard"  // quick|standard|deep
}
```

### 输出
```json
{
  "rule_name": "Shell_ReverseShell_Python",
  "intent": "检测 Python 反向 shell 连接",
  "mitre_mapping": ["T1059.004", "T1071.001"],
  "fp_risk": {
    "level": "高",
    "reason": "包含 subprocess 关键词，良性脚本常用",
    "affected_scenarios": ["DevOps", "DataScience"]
  },
  "fn_risk": {
    "level": "中",
    "reason": "仅匹配特定字符串，易绕过",
    "bypass_methods": ["编码", "动态导入"]
  },
  "suggestions": [
    "移除 subprocess 单独匹配",
    "添加 socket.connect 组合条件",
    "添加路径例外 (/usr/bin/, /opt/)"
  ],
  "confidence_score": 65,
  "recommendation": "optimize",
  "reasoning_trace": "..."  // 推理过程
}
```

---

## 🚀 使用方式

### 单条规则评审
```bash
python3 review_agent.py --rule "Shell_ReverseShell_Python" --depth deep
```

### 批量评审
```bash
python3 review_agent.py --batch rules/optimized/ --workers 4
```

### 持续监控模式
```bash
python3 review_agent.py --watch rules/ --notify feishu
```

---

## 📊 评审标准

### 自动通过 (approve)
- 置信度 ≥ 80
- FP 风险 = 低
- 3+ 具体攻击特征

### 需优化 (optimize)
- 置信度 50-79
- FP 风险 = 中
- 1-2 具体特征 + 宽泛关键词

### 建议移除 (remove)
- 置信度 < 50
- FP 风险 = 高
- 仅宽泛关键词

---

## 🔧 配置

```yaml
# config/review_agent.yaml
models:
  primary: modelstudio/qwen3.5-plus
  fallback: minimax/MiniMax-M2.7
  
analysis:
  quick:
    max_tokens: 1000
    reasoning: false
  standard:
    max_tokens: 2000
    reasoning: true
  deep:
    max_tokens: 4000
    reasoning: true
    multi_round: true

thresholds:
  approve: 80
  optimize: 50
  remove: 0
```

---

**版本**: v1.0  
**状态**: 开发中  
**预计完成**: 2026-04-05
