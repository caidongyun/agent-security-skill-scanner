# v6.1.3 发布说明

**发布日期**: 2026-04-16  
**版本**: 6.1.3  
**上一版本**: 6.1.2

---

## 🎉 重大更新

### 1. npm 包名变更
- **新包名**: `@caidongyun/security-scanner`
- **旧包名**: `@openclaw/security-scanner` (已废弃)
- **安装命令**: `npm install -g @caidongyun/security-scanner`

### 2. 开源仓库发布
- **Gitee**: https://gitee.com/caidongyun/agent-security-skill-scanner
- **GitHub**: https://github.com/caidongyun/agent-security-skill-scanner
- **npm**: https://www.npmjs.com/package/@caidongyun/security-scanner

### 3. 安装方式扩展
- npm 安装 (推荐)
- Gitee 源码安装
- GitHub 源码安装
- 直接下载运行  

---

## 🎉 重大更新

### 1. PowerShell 支持 (🔴 重点)
- **15 条 PowerShell 专用规则**
- **检测率**: 33.3% → **100%** (+66.7%)
- 覆盖攻击类型:
  - 代码执行 (IEX, DownloadString)
  - 凭据窃取 (Get-Credential)
  - 数据外传 (Invoke-WebRequest)
  - 持久化 (Startup, Registry)
  - 混淆绕过 (EncodedCommand, Base64)

### 2. JavaScript 规则扩展
- **12 条 JavaScript 专用规则**
- **检测率**: 60.0% → **66.7%** (+6.7%)
- 覆盖攻击类型:
  - eval/Function 执行
  - 远程代码加载
  - 原型链污染
  - 命令注入

### 3. Bash 规则扩展
- **12 条 Bash 专用规则**
- **检测率**: 75.0% → **62.5%** (波动)
- 覆盖攻击类型:
  - curl|bash 远程执行
  - 命令注入
  - 反向 Shell
  - 权限提升

### 4. Python 高级规则
- **5 条 Python 高级攻击规则**
- 覆盖攻击类型:
  - Prompt Injection
  - Memory Pollution/RAG 投毒
  - Evasion 技术
  - 供应链攻击
  - 反序列化攻击

### 5. 配置文件识别器
- **新增**: `config_detector.py`
- 自动识别 JSON/YAML 配置文件
- 分离代码文件/配置文件统计
- 检测恶意配置特征

---

## 📊 统计数据

| 指标 | v6.0.0 | v6.1.0 | 变化 |
|------|--------|--------|------|
| **规则总数** | 565 | **609** | +44 (+7.8%) |
| **关键词数** | 2104 | **2536** | +432 |
| **自动机大小** | 1016 | **1192** | +176 |
| **检测率** | 62.9% | **65.8%** | +2.9% |
| **误报率** | 0.0% | **0.0%** | 保持 ✅ |
| **扫描速度** | ~16k it/s | **~12k it/s** | -25%* |

*注：速度差异源于样本数增加，单文件扫描速度相当

---

## 📈 各语言检测率

| 语言 | v6.0.0 | v6.1.0 | 提升 | 目标 | 状态 |
|------|--------|--------|------|------|------|
| **PowerShell** | 33.3% | **100%** | +66.7% | 70% | ✅ **超额** |
| **JavaScript** | 60.0% | **66.7%** | +6.7% | 75% | ⚠️ 部分 |
| **Bash** | 75.0% | **62.5%** | -12.5% | 85% | ⚠️ 下降 |
| **Python** | 61.1% | **61.1%** | 0% | 80% | ⚠️ 待优化 |
| **整体** | 62.9% | **65.8%** | +2.9% | 85% | ⚠️ 部分 |

---

## 📂 新增文件

```
release/v6.1.0/
├── rules/
│   ├── powershell_rules.json       # 15 条 PowerShell 规则
│   ├── javascript_rules.json       # 12 条 JavaScript 规则
│   ├── bash_rules.json             # 12 条 Bash 规则
│   ├── python_advanced_rules.json  # 5 条 Python 高级规则
│   └── dist/all_rules.json         # 609 条合并规则
└── config_detector.py              # 配置文件识别器
```

---

## 🔧 技术改进

### 规则引擎
- 扩展 Aho-Corasick 自动机 (2104→2536 关键词)
- 优化正则表达式预编译
- 支持多语言规则动态加载

### 配置文件识别
- 自动识别 JSON/YAML/TOML/INI 配置文件
- 检测配置文件恶意特征
- 分离代码文件/配置文件统计

### 性能优化
- 保持 <0.1s 规则加载时间
- 自动机构建 ~8ms
- 扫描速度 ~12,000 it/s

---

## ⚠️ 已知问题

### 1. Bash 检测率下降
- **原因**: 新增规则与现有规则冲突
- **影响**: 75.0% → 62.5% (-12.5%)
- **解决**: v6.2.0 优化 Bash 规则

### 2. 整体检测率未达 85% 目标
- **当前**: 65.8%
- **目标**: 85%
- **差距**: +19.2%
- **计划**: v6.2.0 继续优化

---

## 🚀 升级指南

### 从 v6.0.0 升级

```bash
# 1. 备份现有规则
cp -r rules/ rules_backup_v6.0.0/

# 2. 下载 v6.1.0
git pull origin master

# 3. 验证安装
python3 scanner.py --version

# 4. 运行基准测试
python3 scanner.py benchmark_samples/ --output v6.1.0_test.json
```

### 规则合并

```python
# 自动合并规则
python3 << 'EOF'
import json

# 加载 v6.0.0 规则
with open('rules/dist/all_rules_v6.0.0.json') as f:
    v6_rules = json.load(f)

# 加载 v6.1.0 新增规则
with open('rules/powershell_rules.json') as f:
    ps_rules = json.load(f)

# 合并...
EOF
```

---

## 📅 后续计划

### v6.2.0 (预计 2026-04-23)
- JavaScript 规则优化 (66.7% → 75%+)
- Bash 规则修复 (62.5% → 75%+)
- Python 高级规则补充 (61.1% → 70%+)
- **目标检测率**: 75%+

### v6.3.0 (预计 2026-04-30)
- 多层次检测 (AST + 行为分析)
- 规则质量优化
- **目标检测率**: 85%+

---

## 🙏 致谢

感谢所有贡献者和测试用户！

---

## 📄 相关文档

- [完整优化报告](V6_1_0_FINAL_REPORT.md)
- [检测率分析](DETECTION_RATE_ANALYSIS_20260416.md)
- [优化执行报告](OPTIMIZATION_EXECUTION_REPORT_20260416.md)

---

**v6.1.0 发布完成** ✅ | **PowerShell 检测率 100%** 🎉
