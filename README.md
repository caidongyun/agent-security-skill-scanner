# Agent Security Skill Scanner

> AI Agent 技能安全扫描器 - 保障 Agent 生态系统安全

[![Version](https://img.shields.io/badge/version-2.0.1-blue.svg)](https://gitee.com/caidongyun/agent-security-skill-scanner)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-yellow.svg)](https://www.python.org/)

---

## 为什么需要 Skill Scanner？

随着 AI Agent 的快速发展，各类 Skills（技能）大量涌现，但安全风险也随之增加：

- 恶意技能窃取敏感数据
- 后门代码潜伏在合法技能中
- 权限滥用导致数据泄露
- 供应链攻击防不胜防

**Agent Security Skill Scanner** 为您的 AI Agent 生态系统提供主动防御。

---

## 核心功能

### 恶意代码检测
- `eval()` / `exec()` 危险函数
- 动态代码执行 (`__import__`, `compile`)
- Base64 混淆代码
- 系统命令执行 (`os.system`, `subprocess`)

### 权限滥用检测
- 过度文件系统访问
- 网络请求 unrestricted
- 环境变量窃取
- 敏感路径访问 (/etc/, ~/.ssh/)

### 风险评分
- 综合风险评分 (0-100)
- 五级风险等级: CRITICAL / HIGH / MEDIUM / LOW / SAFE
- 自动化处置建议: REJECT / REVIEW / ALLOW

---

## 快速开始

### 安装

```bash
./install.sh
```

### 基本使用

```bash
# 扫描单个技能
python cli.py scan <skill_directory>

# 批量扫描
python cli.py scan-all <skills_directory>
```

---

## 检测规则

| 规则ID | 类型 | 风险等级 | 说明 |
|--------|------|----------|------|
| EVAL_USAGE | 代码执行 | HIGH | 使用 eval() |
| EXEC_USAGE | 代码执行 | HIGH | 使用 exec() |
| SYSTEM_COMMAND | 命令执行 | CRITICAL | 系统命令 |
| BASE64_DECODE | 混淆 | MEDIUM | Base64 解码 |
| SENSITIVE_FILE | 文件访问 | HIGH | 敏感文件 |
| ENV_ACCESS | 凭据窃取 | MEDIUM | 环境变量 |

---

## Python API

```python
from cli import scan_skill

results = scan_skill("skills/my-skill/")
score = results['overall']['score']

if score >= 60:
    print("此技能存在安全风险，建议审查")
else:
    print("此技能通过安全检查")
```

---

## 配置文件

`skill.yaml` - Skill 元数据配置：

```yaml
name: my-skill
version: 1.0.0
description: 技能描述
maintainer: example@email.com
permissions:
  - filesystem
  - network
risks:
  - medium
```

---

## 许可证

MIT License - 见 LICENSE 文件

---

## 相关链接

- Gitee: https://gitee.com/caidongyun/agent-security-skill-scanner

---

*版本：v2.0.1 | 2026-03-14*
