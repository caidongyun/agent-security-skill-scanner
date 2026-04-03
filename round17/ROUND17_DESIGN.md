# Round 17: 多 Agent 协同优化

**目标**: 构建 5 个专用 Agent 协同工作

---

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────┐
│              Orchestrator Agent                     │
│  (协调/任务分发/结果汇总)                            │
└─────────────────┬───────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│Detection│ │Analysis │ │  Rule   │
│ Agent   │ │ Agent   │ │ Agent   │
│         │ │         │ │         │
│ AST 扫描 │ │ 行为分析 │ │ 规则生成 │
└─────────┘ └─────────┘ └─────────┘
    │             │             │
    └─────────────┼─────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│Intel    │ │ Report  │ │ Validator│
│ Agent   │ │ Agent   │ │ Agent   │
│         │ │         │ │         │
│ 情报采集 │ │ 报告生成 │ │ 质量验证 │
└─────────┘ └─────────┘ └─────────┘
```

---

## 📋 Agent 职责

### 1. Orchestrator Agent (协调者)
- **职责**: 任务分解、Agent 调度、结果汇总
- **输入**: 用户请求/扫描任务
- **输出**: 最终报告

### 2. Detection Agent (检测)
- **职责**: AST 扫描、混淆检测、行为分析
- **工具**: ast_engine_v2.py
- **输出**: 检测结果 JSON

### 3. Analysis Agent (分析)
- **职责**: 深度分析、攻击模式识别、威胁分类
- **工具**: malicious_skill_analyzer.py
- **输出**: 分析报告

### 4. Rule Agent (规则)
- **职责**: 规则生成、规则优化、规则验证
- **工具**: rule_generator.py
- **输出**: Sigma/YARA/IOC 规则

### 5. Intel Agent (情报)
- **职责**: 威胁情报采集、APT 组织追踪、CVE 关联
- **工具**: threat_intel_product.py
- **输出**: 情报报告

### 6. Report Agent (报告)
- **职责**: 报告生成、可视化、文档沉淀
- **工具**: report_generator.py
- **输出**: Markdown/JSON 报告

### 7. Validator Agent (验证)
- **职责**: 质量验证、指标计算、回归测试
- **工具**: test_runner.py
- **输出**: 验证报告

---

## 🔄 工作流程

```
1. 用户请求
   ↓
2. Orchestrator 分解任务
   ↓
3. 并行执行 (Detection + Analysis + Intel)
   ↓
4. Rule Agent 生成规则
   ↓
5. Validator Agent 验证
   ↓
6. Report Agent 生成报告
   ↓
7. Orchestrator 汇总输出
```

---

## 📈 目标指标

| 指标 | 目标 |
|------|------|
| 任务并发数 | ≥3 |
| 单轮扫描时间 | <5 分钟 |
| 检测率 | ≥98% |
| 误报率 | <2% |
| 规则生成速度 | ≥100 条/分钟 |

---

## 📁 实现文件

```
round17/
├── orchestrator.py        # 协调 Agent
├── agents/
│   ├── detection.py       # 检测 Agent
│   ├── analysis.py        # 分析 Agent
│   ├── rule.py            # 规则 Agent
│   ├── intel.py           # 情报 Agent
│   ├── report.py          # 报告 Agent
│   └── validator.py       # 验证 Agent
├── config.yaml            # 配置
└── ROUND17_REPORT.md      # 完成报告
```

---

## 下一步

1. 创建 Orchestrator 框架
2. 实现各 Agent 模块
3. 配置通信机制
4. 集成测试
5. 性能优化
