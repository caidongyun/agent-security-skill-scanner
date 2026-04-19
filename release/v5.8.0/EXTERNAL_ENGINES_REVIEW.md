# 外部扫描引擎 Review 报告

**日期**: 2026-04-14  
**目的**: 学习业界优秀扫描引擎，抽取可用技术

---

## 📊 已获取的扫描引擎

### 1. Semgrep (⭐⭐⭐⭐⭐)

**官网**: https://semgrep.dev  
**版本**: v1.159.0 (已安装)  
**类型**: AST + Pattern 混合扫描  
**语言**: Python (开源)

**核心特点**:
- ✅ **AST 分析** - 语法树级别检测
- ✅ **Pattern 匹配** - 支持自定义规则
- ✅ **多语言支持** - Python, JS, Go, Java 等
- ✅ **规则社区** - 1000+ 公开规则

**可学习技术**:
```yaml
# Semgrep 规则示例
rules:
  - id: dangerous-eval
    pattern: eval($USER_INPUT)
    message: "Dangerous eval with user input"
    severity: ERROR
    languages: [python, javascript]
```

**抽取建议**:
- ✅ AST 解析器 (使用 `tree-sitter`)
- ✅ 规则 DSL 设计
- ✅ 多语言支持架构

---

### 2. Bandit (⭐⭐⭐⭐)

**官网**: https://bandit.readthedocs.io  
**版本**: v1.9.4 (已安装)  
**类型**: AST Python 安全扫描  
**语言**: Python (开源)

**核心特点**:
- ✅ **Python 专用** - 深度 AST 分析
- ✅ **插件架构** - 易于扩展
- ✅ **内置规则** - 60+ Python 安全规则
- ✅ **CI/CD 集成** - 易于自动化

**可学习技术**:
```python
# Bandit Plugin 示例
@register_test('B307')
def test_eval_used(context):
    """检测 eval() 使用"""
    if context.node.func.name == 'eval':
        return bandit.Issue(
            severity='HIGH',
            confidence='MEDIUM',
            text='Use of eval detected'
        )
```

**抽取建议**:
- ✅ Python AST 遍历器
- ✅ Plugin 架构设计
- ✅ 规则测试框架

---

### 3. Trivy (⭐⭐⭐⭐⭐)

**官网**: https://trivy.dev  
**版本**: v0.50.0 (安装中)  
**类型**: 综合安全扫描器  
**语言**: Go (开源)

**核心特点**:
- ✅ **多场景支持** - 容器、VM、代码、配置
- ✅ **漏洞数据库** - 内置 CVE 数据库
- ✅ **SBOM 生成** - 软件物料清单
- ✅ **极速扫描** - Go 语言性能优势

**可学习技术**:
- ✅ 漏洞数据库设计
- ✅ 多扫描器编排
- ✅ 报告生成系统

**抽取建议**:
- ⚠️ Go 语言，抽取成本高
- ✅ 可学习漏洞数据库设计
- ✅ 可学习报告格式

---

### 4. Gitleaks (⭐⭐⭐⭐)

**官网**: https://gitleaks.io  
**版本**: 未安装  
**类型**: Git 仓库敏感信息扫描  
**语言**: Go (开源)

**核心特点**:
- ✅ **敏感信息检测** - 密钥、密码、Token
- ✅ **Git 历史扫描** - 检测历史提交
- ✅ **高准确率** - 低误报率
- ✅ **配置灵活** - 自定义规则

**可学习技术**:
```toml
# Gitleaks 配置示例
[[rules]]
id = "aws-access-key"
description = "AWS Access Key"
regex = '''AKIA[0-9A-Z]{16}'''
tags = ["aws", "credential"]
```

**抽取建议**:
- ✅ 敏感信息检测规则
- ✅ 正则规则设计
- ⚠️ Git 历史扫描 (可选)

---

### 5. Skill Scanner (⭐⭐⭐)

**来源**: ClawHub  
**版本**: v0.1.2 (已安装)  
**类型**: AI Skill 专用扫描器  
**语言**: Python

**核心特点**:
- ✅ **AI Skill 专用** - 针对 AI 技能设计
- ✅ **轻量级** - 易于集成
- ✅ **规则简单** - 易于理解

**可学习技术**:
- ✅ AI Skill 特定规则设计
- ✅ 轻量级架构

**抽取建议**:
- ✅ 规则可以直接复用
- ✅ 架构参考

---

### 6. Security Scanner (⭐⭐⭐)

**来源**: ClawHub  
**版本**: v1.0.0 (已安装)  
**类型**: Web 安全扫描器  
**语言**: Python

**核心特点**:
- ✅ **Web 应用扫描** - 漏洞检测
- ✅ **API 安全** - API 漏洞检测
- ✅ **基础设施** - 配置安全检查

**抽取建议**:
- ⚠️ 与 AI Skill 场景不太匹配
- ✅ 可学习报告格式

---

## 🎯 技术抽取优先级

### P0 (立即抽取)

| 技术 | 来源 | 用途 | 优先级 |
|------|------|------|--------|
| **AST 解析器** | Semgrep/Bandit | Layer 3 AST 引擎 | ⭐⭐⭐⭐⭐ |
| **Plugin 架构** | Bandit | 规则扩展机制 | ⭐⭐⭐⭐ |
| **规则 DSL** | Semgrep/Gitleaks | 规则定义语言 | ⭐⭐⭐⭐ |
| **敏感信息检测** | Gitleaks | 凭证/密钥检测 | ⭐⭐⭐⭐ |

### P1 (短期抽取)

| 技术 | 来源 | 用途 | 优先级 |
|------|------|------|--------|
| **漏洞数据库** | Trivy | 规则库管理 | ⭐⭐⭐ |
| **报告生成** | Trivy/Semgrep | 报告格式 | ⭐⭐⭐ |
| **多语言支持** | Semgrep | 扩展到其他语言 | ⭐⭐ |

### P2 (长期抽取)

| 技术 | 来源 | 用途 | 优先级 |
|------|------|------|--------|
| **Git 历史扫描** | Gitleaks | 历史提交检测 | ⭐⭐ |
| **SBOM 生成** | Trivy | 物料清单 | ⭐ |
| **CI/CD 集成** | Bandit | 自动化流程 | ⭐⭐ |

---

## 📐 v6.0.0 架构设计 (融合外部技术)

### 目标架构

```
文件/文件夹
    ↓
┌─────────────────────────────────────┐
│  Layer 1: Pattern Engine            │
│  - 100+ 正则模式                     │
│  - 快速初筛                          │
│  ← 学习：Gitleaks 正则规则          │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Layer 2: Rule Engine               │
│  - 50-100 条核心规则                 │
│  - 多条件组合                        │
│  ← 学习：Semgrep 规则 DSL           │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Layer 3: AST Engine (新增)         │
│  - 语法树分析                        │
│  - 语义理解                          │
│  ← 学习：Semgrep/Bandit AST         │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Layer 4: 综合评估                  │
│  - 合并三层结果                      │
│  - 计算分数 + 置信度                 │
│  ← 学习：Bandit 置信度模型          │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Layer 5: LLM (可选)                │
│  - 语义确认                          │
│  - 误报过滤                          │
└─────────────────────────────────────┘
    ↓
ScanResult
```

### 实施计划

#### Phase 1: AST 引擎 (本周)
- [ ] 集成 `tree-sitter` AST 解析器
- [ ] 实现 Python AST 遍历器
- [ ] 开发 10+ AST 检测规则
- [ ] 与 Pattern/Rule 引擎集成

#### Phase 2: 规则 DSL (下周)
- [ ] 设计规则定义语言
- [ ] 实现规则加载器
- [ ] 迁移现有规则到新格式
- [ ] 规则测试框架

#### Phase 3: Plugin 架构 (长期)
- [ ] 设计 Plugin 接口
- [ ] 实现 Plugin 加载器
- [ ] 开发示例 Plugin
- [ ] 文档和示例

---

## 📋 可直接复用的规则

### Gitleaks 敏感信息规则

```python
# 可直接转换为 Pattern
AWS_ACCESS_KEY = r'AKIA[0-9A-Z]{16}'
AWS_SECRET_KEY = r'[0-9a-zA-Z/+]{40}'
GITHUB_TOKEN = r'gh[pousr]_[A-Za-z0-9_]{36}'
SLACK_TOKEN = r'xox[baprs]-[0-9a-zA-Z]{10,48}'
```

### Bandit Python 安全规则

```python
# 可直接转换为 Rule
B307: eval() 使用检测
B308: exec() 使用检测
B310: 不安全 URL 打开
B311: 弱随机数生成
B312: Telnet 使用检测
```

### Semgrep AI 安全规则

```yaml
# 可直接转换为 Rule
- id: ai-prompt-injection
  pattern: |
    ignore previous instructions
  message: "Potential prompt injection"
  severity: WARNING

- id: ai-data-exfil
  pattern: |
    fetch($USER_INPUT)
  message: "Potential data exfiltration"
  severity: ERROR
```

---

## 🎯 下一步行动

1. **立即**: 实现 AST 引擎 (基于 tree-sitter)
2. **本周**: 迁移 Bandit 10+ Python 安全规则
3. **下周**: 设计规则 DSL，迁移现有规则
4. **长期**: Plugin 架构，支持第三方规则

---

*本报告由外部扫描引擎分析生成*
*最后更新：2026-04-14*
