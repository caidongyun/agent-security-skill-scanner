# Security Scanner v6.1.9 - 统一架构版

## 🏗️ 三层检测架构

```
Layer 1: PatternEngine (快速预筛选)
├── 32 个攻击 Pattern
├── Aho-Corasick 自动机 - O(n) 复杂度
└── 速度：~300,000 it/s

        ↓ 候选攻击类型

Layer 2: HybridRuleEngine (深度匹配)
├── AC 自动机预筛选 (3.3ms)
├── 627 条规则 / 44 个类别
├── 只匹配命中的类别子集
└── 风险等级：CRITICAL/HIGH/MEDIUM/LOW/SAFE

        ↓ 可选 (语义分析)

Layer 3: LLMEngine (语义理解)
├── 仅复核 CRITICAL 级别
├── 上下文理解
└── 支持 MiniMax/Qwen/OpenAI
```

## 📊 性能指标

| 指标 | 数值 |
|------|------|
| AC 自动机构建 | 3.3ms |
| 关键词数 | 1081 |
| 规则数 | 627 |
| 类别数 | 44 |
| 扫描速度 | 50-100 it/s (实际) |

## 🚀 使用方法

```bash
# 全量扫描
python3 scanner.py /path/to/skills --workers 8 --max-files 200000

# 启用 LLM
python3 scanner.py /path/to/skills --llm --llm-model qwen

# 输出 JSON
python3 scanner.py /path/to/skills --output json --output-file report.json
```

## 📁 文件结构

```
release/v6.1.9/
├── scanner.py              # 主扫描器 (统一架构)
├── src/engines/
│   ├── __init__.py         # Layer 1/2/3 引擎
│   ├── hybrid_scanner.py   # AC 自动机 + Regex
│   ├── pattern_engine.py   # Pattern 匹配
│   ├── rule_engine.py      # 规则匹配
│   └── llm_engine.py       # LLM 分析
├── whitelist_filter.py     # 白名单过滤
├── config_detector.py      # 配置文件识别
└── rules/
    └── dist/
        └── all_rules.json  # 627 条规则
```

## 🔄 版本历史

- **v6.1.9** - 统一架构，AC 自动机预筛选，规则分组
- **v6.1.0** - 三层架构基础版
