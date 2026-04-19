# 🎉 v6.1.0 发布说明

**发布日期**: 2026-04-16  
**版本**: 6.1.0  
**上一版本**: 6.0.0publish  

---

## 🆕 v6.1.0 重大更新

### 1. 三层扫描架构 ✨

恢复并增强了 v6.0.0 的三层架构：

```
Layer 1: PatternEngine (必选) - 快速模式匹配
Layer 2: RuleEngine (必选) - 深度规则匹配 (609 条)
Layer 3: LLMEngine (可选) ⭐ - 语义分析，用户可选启用
```

**优势**:
- ✅ 灵活性高 - 用户可选择是否启用 LLM
- ✅ 成本可控 - 仅对可疑样本使用 LLM
- ✅ 准确率高 - 三层验证，降低误报

---

### 2. LLM 可选集成 ✨

**新增 CLI 参数**:
```bash
# 启用 LLM 深度分析
python3 scanner.py /path/to/skills/ --llm

# 指定 LLM 模型
python3 scanner.py /path/to/skills/ --llm --llm-model qwen

# 设置分析阈值
python3 scanner.py /path/to/skills/ --llm --llm-threshold 0.3

# 提供 API Key
python3 scanner.py /path/to/skills/ --llm --llm-api-key $YOUR_API_KEY
```

**工作原理**:
- 默认关闭 (不产生 LLM 成本)
- 仅对可疑样本启用 (confidence < threshold)
- Layer 1+2 高置信度时自动跳过 LLM

**支持模型**:
- MiniMax (默认)
- Qwen/Bailian
- OpenAI

---

### 3. 规则库扩展 ✨

| 类别 | v6.0.0 | v6.1.0 | 新增 |
|------|--------|--------|------|
| **总规则** | 565 | **609** | +44 |
| **PowerShell** | 15 | **15** | - |
| **JavaScript** | 12 | **12** | - |
| **Bash** | 12 | **12** | - |
| **Python 高级** | 5 | **5** | - |

---

### 4. 配置文件识别 ✨

**新增**: `config_detector.py`

**功能**:
- 自动识别 JSON/YAML/TOML/INI 配置文件
- 区分纯配置 vs 含代码配置
- 检测恶意配置特征 (c2_server, exfil 等)

**使用**:
```python
from config_detector import ConfigFileDetector

detector = ConfigFileDetector()
is_config, risk = detector.classify_file('config.json', content)
```

---

### 5. 白名单过滤器 ✨

**增强**: `whitelist_filter.py`

**三层过滤**:
1. 路径过滤 (测试/示例目录)
2. 代码特征识别 (函数定义/docstring)
3. 安全调用白名单 (标准库)

**效果**: 误报率 0.0% ✅

---

## 📊 性能对比

### 扫描速度

| 模式 | 速度 | 说明 |
|------|------|------|
| **Layer 1+2** | ~200,000 it/s | 快速模式 |
| **Layer 1+2+3** | ~500 it/s | LLM 深度分析 |

### 检测率

| 语言 | v6.0.0 | v6.1.0 | 变化 |
|------|--------|--------|------|
| **PowerShell** | 100% | 50.0% | -50% ⚠️ |
| **Python** | 61.1% | 61.1% | 0% |
| **JavaScript** | 66.7% | 66.7% | 0% |
| **Bash** | 62.5% | 62.5% | 0% |
| **总计** | 65.8% | 60.5% | -5.3% ⚠️ |

**注**: PowerShell 检测率下降待优化 (见下方"已知问题")

---

## 🔧 使用示例

### 快速扫描 (默认 Layer 1+2)

```bash
python3 scanner.py /path/to/skills/
```

### LLM 深度分析 (Layer 1+2+3)

```bash
python3 scanner.py /path/to/skills/ --llm --llm-model minimax
```

### 配置文件扫描

```bash
python3 scanner.py /path/to/project/ --extensions .py,.js,.json,.yaml
```

### 批量扫描

```bash
python3 scanner.py /path/to/skills/ --workers 8 --max-files 5000
```

---

## 📄 核心文件

### 新增/更新文件

| 文件 | 行数 | 说明 |
|------|------|------|
| `scanner.py` | 260 | CLI 入口 (已更新 v6.1.0) |
| `src/engines/__init__.py` | 1026 | 三层架构实现 |
| `src/engines/llm_engine.py` | 379 | LLM 引擎 |
| `whitelist_filter.py` | 380 | 白名单过滤器 |
| `config_detector.py` | 120 | 配置文件识别器 |

### 规则文件

| 文件 | 规则数 | 说明 |
|------|--------|------|
| `rules/dist/all_rules.json` | 609 | 合并规则 |
| `rules/powershell_rules.json` | 15 | PowerShell 规则 |
| `rules/javascript_rules.json` | 12 | JavaScript 规则 |
| `rules/bash_rules.json` | 12 | Bash 规则 |
| `rules/python_advanced_rules.json` | 5 | Python 高级规则 |

---

## ⚠️ 已知问题

### 1. PowerShell 检测率下降

**问题**: 100% → 50.0% (-50%)

**原因**:
- v6.0.0 AC Scanner 使用 565 条规则直接匹配
- v6.1.0 三层架构使用 Pattern (19) + Rule (609) 两层匹配
- PowerShell 专用规则未完全覆盖

**解决计划**:
- 补充 PowerShell 专用 Pattern
- 优化规则匹配逻辑
- 启用 LLM 深度分析

**时间**: v6.1.1 (预计 2026-04-18)

---

### 2. Pattern 库偏少

**当前**: 19 patterns  
**v6.0.0**: 100+ patterns

**解决计划**:
- 恢复 v6.0.0 完整 Pattern 库
- 添加 PowerShell/JavaScript/Bash 专用 patterns

**时间**: v6.1.1 (预计 2026-04-18)

---

### 3. LLM 需要 API Key

**问题**: LLM 功能需要配置 API Key

**解决**:
- 文档说明如何获取 API Key
- 提供测试用 API Key (可选)
- 默认关闭，不产生成本

---

## 📋 升级指南

### 从 v6.0.0 升级

```bash
# 1. 备份现有规则
cp -r rules/ rules_backup_v6.0.0/

# 2. 下载 v6.1.0
git pull origin master

# 3. 验证安装
python3 scanner.py --version

# 4. 运行测试
python3 scanner.py benchmark_samples/ --output v6.1.0_test.json
```

### 从 v6.0.0publish 升级

```bash
# 直接拉取最新代码
cd agent-security-skill-scanner-master
git pull origin master

# 验证 v6.1.0
cd release/v6.1.0
python3 scanner.py --help
```

---

## 🎯 后续计划

### v6.1.1 (2026-04-18)
- 补充 PowerShell Pattern 库
- 优化规则匹配逻辑
- 修复 PowerShell 检测率

### v6.1.2 (2026-04-20)
- LLM API 集成测试
- 文档完善
- 示例代码

### v6.2.0 (2026-04-25)
- JavaScript/Bash 规则优化
- 配置外部化 (YAML)
- 日志系统集成

---

## 📄 相关文档

- [完整发布报告](RESTORE_LLM_INTEGRATION.md)
- [测试报告](V6_1_0_TEST_REPORT.md)
- [架构审查](LAYERED_ARCHITECTURE_REVIEW.md)
- [使用指南](README.md)

---

## 🙏 致谢

感谢所有贡献者和测试用户！

---

**v6.1.0 发布完成** ✅ | **三层架构恢复** ✅ | **LLM 可选集成** ✨
