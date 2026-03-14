# Agent Security Skill Scanner v2.0.0 - 安装指南

> **版本**: v2.0.0  
> **发布日期**: 2026-03-13  
> **状态**: ✅ 正式发布

---

## 📦 包内容

```
v2.0.0/
├── scanner_cli.py              # 主入口（统一 CLI）
├── parallel_scanner.py         # 并行扫描器
├── static_analyzer.py          # 静态分析器
├── dynamic_detector.py         # 动态检测器
├── risk_scanner.py             # 风险扫描器
├── rule_iterator.py            # 规则迭代器
├── detection_rules.json        # ⭐ 检测规则库（110 条规则）
│
├── detectors/
│   └── malware.py              # 恶意代码检测器
│
├── whitelist/                  # 误报处理系统（新增）
│   ├── whitelist_manager.py    # 白名单管理
│   ├── remote_analyzer.py      # 远程分析
│   ├── init_official.py        # 官方采集
│   └── privacy_check.py        # 隐私检查
│
├── public.json                 # 公共白名单模板
├── README.md                   # 使用说明
├── INSTALL.md                  # 本文件
└── QUICK-START.md              # 快速开始
```

**总计**: 18 个文件，~150KB

---

## 🚀 快速安装

### 方式 1: 复制发布包

```bash
# 1. 复制整个发布包
cp -r /path/to/agent-security-skill-scanner/release/v2.0.0/ \
      your-project/agent-security-scanner/

# 2. 初始化白名单
cd your-project/agent-security-scanner/
cp public.json whitelist/local.json
```

### 方式 2: 克隆技能仓库

```bash
# 克隆完整技能
git clone https://gitee.com/caidongyun/ai-work.git
cd ai-work/skills/agent-security-skill-scanner/
```

---

## 🔧 配置

### 1. 初始化白名单

```bash
cd agent-security-scanner/

# 复制公共模板
cp whitelist/public.json whitelist/local.json

# 编辑个人配置（可选）
# 添加你信任的技能和规则
```

### 2. 配置文件（可选）

编辑 `whitelist/config.json`:

```json
{
  "llm_provider": "bailian",
  "llm_model": "qwen3.5-plus",
  "confidence_threshold": 0.8,
  "cache_enabled": true
}
```

---

## 📖 使用方法

### 基础扫描

```bash
# 扫描单个技能
python3 scanner_cli.py scan your-skill/

# 扫描目录
python3 scanner_cli.py scan skills/

# 输出 JSON 报告
python3 scanner_cli.py scan skills/ --output scan_result.json
```

### 使用白名单

```bash
# 扫描（自动应用白名单）
python3 scanner_cli.py scan skills/ --use-whitelist

# 添加白名单
python3 whitelist/whitelist_manager.py --action add \
  --type file \
  --value skills/my-skill/cli.py \
  --reason "已人工审核"
```

### 生成报告

```bash
# 生成 HTML 报告
python3 scanner_cli.py report --scan-result scan_result.json

# 查看报告
open report.html
```

---

## 🧪 验证安装

### 测试 1: 扫描真实技能

```bash
# 扫描一个真实技能（应该无误报）
python3 scanner_cli.py scan /path/to/real-skill/

# 预期输出：
# ==================================================
# 📊 扫描结果:
#    总文件：10
#    总问题：0
# ==================================================
```

### 测试 2: 白名单功能

```bash
# 添加白名单
python3 whitelist/whitelist_manager.py --action add \
  --type file \
  --value test.py \
  --reason "测试"

# 检查白名单
python3 whitelist/whitelist_manager.py --action list

# 预期输出：
# wl-xxx [file] test.py - 测试 ✅
```

### 测试 3: 隐私检查

```bash
# 发布前检查
python3 whitelist/privacy_check.py

# 预期输出：
# ✅ 所有文件安全检查通过，可以发布
```

---

## 📊 检测规则

**规则库**: `detection_rules.json` (110 条规则)

| 类别 | 规则数 | 说明 |
|------|--------|------|
| 🔴 恶意代码检测 | 12 | eval/exec 滥用、动态导入等 |
| 🟠 后门模式检测 | 10 | 远程 Shell、隐藏后门等 |
| 🟠 权限滥用检测 | 9 | 工具调用权限滥用 |
| 🔴 硬编码凭据 | 15 | API Key、密码、Token |
| 🔴 数据泄露检测 | 8 | 敏感数据传输 |
| 🟡 不安全执行 | 9 | 命令注入、文件执行 |
| 🟡 文件操作检测 | 8 | 敏感文件读写 |
| 🟡 代码混淆检测 | 8 | Base64、加密混淆 |
| 🟡 依赖风险检测 | 6 | 恶意 npm/Python 包 |
| 🟠 钓鱼/诱导检测 | 10 | 社会工程学攻击 |
| 🔴 C2 通信检测 | 5 | 命令控制通信 |
| 🔴 勒索软件特征 | 3 | 文件加密、勒索信 |

---

## ⚠️ 注意事项

### 不包含的内容

**发布包仅包含用户必要内容**，不包含:
- ❌ 测试样本库（内部使用）
- ❌ 样本生成工具（可能滥用）
- ❌ 评估测试工具（内部研发）
- ❌ 临时数据文件

### 系统要求

- ✅ Python 3.7+
- ✅ Git（可选，用于克隆）
- ✅ 无其他外部依赖

### 性能建议

- 小项目（<100 文件）: 即时扫描
- 中项目（100-1000 文件）: 使用并行扫描（默认 8 线程）
- 大项目（>1000 文件）: 建议使用 `--threads 16`

---

## 🆘 常见问题

### Q1: 扫描结果为 0 文件？

A: 检查路径是否正确，确保目录包含 `.py` 文件

### Q2: 如何添加白名单？

A: 使用 `whitelist_manager.py --action add` 命令

### Q3: 如何更新检测规则？

A: 从 Gitee 拉取最新的 `detection_rules.json`

### Q4: 误报如何处理？

A: 添加到白名单，或使用 `remote_analyzer.py` 进行 LLM 分析

---

## 📝 升级指南

### v1.x → v2.0.0

```bash
# 1. 备份旧配置
cp whitelist/local.json whitelist/local.json.bak

# 2. 复制新版本
cp -r release/v2.0.0/ agent-security-scanner/

# 3. 恢复配置
cp whitelist/local.json.bak agent-security-scanner/whitelist/local.json
```

---

## 🔗 相关资源

- **Gitee**: https://gitee.com/caidongyun/ai-work
- **完整文档**: `README.md`
- **快速开始**: `QUICK-START.md`
- **发布说明**: `RELEASE-NOTES.md`

---

*安装问题？查看 README.md 或提交 Issue*
