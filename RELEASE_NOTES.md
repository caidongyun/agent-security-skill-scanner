# Agent Security Scanner v6.2.0 Release Notes

**发布日期**: 2026-04-27  
**版本**: 6.2.0  
**状态**: ✅ 生产就绪

---

## 🎯 核心特性

### 风险分级体系 (新增)

| 分类器 | 功能 | 状态 |
|--------|------|------|
| **CurlRiskClassifier** | Curl 命令风险分级 (白名单域名) | ✅ |
| **CredentialTheftClassifier** | 凭据窃取攻击链检测 (诱导→混淆→外传) | ✅ |
| **RiskTierClassifier** | 统一 5 级风险体系 | ✅ |

### 规则库优化

- **总规则数**: 846 条 (去重 88 条，标准化 419 条 severity)
- **新增规则**: 6 条凭据攻击链规则 (CRED-CHAIN-001 ~ 006)
- **Severity 标准化**: 全部统一为大写 (CRITICAL/HIGH/MEDIUM/LOW)
- **规则优化器**: `rules/rule_optimizer.py` - 自动去重 + 标准化

### 单 Skill 熔断机制 (新增)

- **功能**: 跳过文件数过多的异常 skill 目录，防止恶意 DoS
- **默认阈值**: `--skill-max-files 500`
- **适用场景**: 面向用户的 scanner 防恶意软件塞入大量文件

### 三层检测架构

```
[一层] 白名单/黑名单 → 快速筛查
[二层] 智能评分 + 意图分析 → 边界样本判定
[三层] LLM 深度分析 → 不确定样本
```

### 新增模块

| 模块 | 功能 |
|------|------|
| `context_aware_filter.py` | 上下文感知过滤 |
| `security_tool_detector.py` | 安全工具识别 |
| `credential_theft_classifier.py` | 凭据窃取攻击链检测 |
| `curl_risk_classifier.py` | Curl 风险分级 |
| `risk_tier_classifier.py` | 统一 5 级风险体系 |

---

## 📊 性能指标

| 指标 | v6.2.0 | v6.1.0 | 提升 |
|------|--------|--------|------|
| 规则数 | 846 | 616 | +37% |
| 扫描速度 | ~385 文件/秒 | ~300 文件/秒 | +28% |
| 风险分级 | 5 级 | 无 | ✅ 新增 |
| 熔断保护 | ✅ | ❌ | ✅ 新增 |

---

## 🔧 修复问题

### P0 - 版本一致性
- 修复 `scanner.py` 版本号混用 (`6.2.1-dev` → `6.2.0`)
- 统一 `package.json` 版本为 `6.2.0`

### P0 - 规则数一致性
- 修复 `scanner.py` `rules_count`: 928 → 846
- 统一 `RELEASE_NOTES.md` 规则数为 846
- 修复 `all_rules.json` `optimization_stats.total`: 928 → 846

### P1 - package.json `files` 缺失
- 新增 5 个分类器/检测器模块到 `files` 字段

---

## 📦 发布文件清单 (26 个)

```
v6.2.0/
├── scanner.py                    ← 统一三层架构
├── whitelist_filter.py
├── config_detector.py
├── context_aware_filter.py       ← 新增
├── credential_theft_classifier.py ← 新增 (攻击链检测)
├── curl_risk_classifier.py       ← 新增
├── risk_tier_classifier.py       ← 新增 (5级风险体系)
├── security_tool_detector.py     ← 新增
├── scan
├── index.js
├── index.d.ts
├── package.json
├── requirements.txt
├── README.md
├── RELEASE_NOTES.md
├── SKILL.md
├── rules/dist/all_rules.json     ← 846 条规则
├── rules/rule_optimizer.py       ← 新增
└── src/
    ├── engines/                  ← 8 个引擎模块
    └── *.py
```

---

## 🚀 使用方法

```bash
# 安装
cd release/v6.2.0
pip install -r requirements.txt

# 扫描
python3 scanner.py /path/to/skills --workers 8

# 带熔断阈值
python3 scanner.py /path/to/skills --skill-max-files 500

# 输出 JSON 报告
python3 scanner.py /path/to/skills --output json --output-file report.json
```

---

## 🔗 仓库

- **Gitee**: https://gitee.com/caidongyun/agent-security-skill-scanner-master
- **GitHub**: https://github.com/caidongyun/agent-security-skill-scanner
- **NPM**: @caidongyun/security-scanner@6.2.0
