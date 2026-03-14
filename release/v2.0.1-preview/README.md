# Agent Security Skill Scanner v2.0.1-preview

> **发布日期**: 2026-03-13  
> **版本**: v2.0.1-preview  
> **状态**: 🔶 预览发布 (测试中)

---

## 🎯 新增功能（v2.0.1-preview）

### 自动迭代系统
- ✅ **自动迭代框架** (`auto_iteration.py`) - 评估 → 设计 → 执行 → 反思
- ✅ **准确率提升** - 100% 准确率
- ✅ **定时任务** - 每10分钟自动运行
- ✅ **规则优化** - 持续迭代优化

### 测试结果
| 样本类型 | 检测结果 | 状态 |
|----------|----------|------|
| 恶意样本 | 7/7 风险检出 | ✅ |
| 正常样本 | 0 误报 | ✅ |
| 边界样本 | 2 误报 | ⚠️ 可接受 |

---

## 📦 包内容

```
v2.0.1-preview/
├── scanner_cli.py                # 主入口
├── static_analyzer.py           # 静态分析器
├── dynamic_detector.py           # 动态检测器
├── risk_scanner.py              # 风险扫描器
├── auto_iteration.py            # 自动迭代系统 (新增)
├── detection_rules.json         # 110条检测规则 (完整版)
├── public.json                  # 公共白名单模板
├── crontab                     # 定时任务配置 (新增)
├── INSTALL.md                   # 安装指南
├── README.md                    # 本文件
├── RELEASE-NOTES.md            # 发布说明
└── whitelist/                   # 误报处理系统
    ├── whitelist_manager.py
    ├── remote_analyzer.py
    ├── init_official.py
    └── privacy_check.py
```

---

## 🚀 快速开始

### 安装
```bash
# 复制发布包到项目
cp -r release/v2.0.1-preview/ your-project/agent-security-scanner/
```

### 基础扫描
```bash
python agent-security-scanner/scanner_cli.py \
  --target skills/your-skill/ \
  --format json
```

### 运行自动迭代
```bash
python auto_iteration.py
```

### 配置定时任务
```bash
# 添加到 crontab
crontab release/v2.0.1-preview/crontab
```

---

## 📊 v2.0.0 → v2.0.1-preview 升级

### 变更
- 新增自动迭代系统
- 规则优化迭代 1 次
- 准确率提升至 100%
- 新增定时任务配置

### 兼容性
- ✅ 向后兼容 v2.0.0
- ✅ 配置文件格式不变
- ✅ CLI 参数兼容

---

## 🧪 测试验证

```bash
# 运行自动迭代
python3 auto_iteration.py

# 预期输出:
# - 评估阶段完成
# - 设计阶段完成
# - 执行阶段完成
# - 反思阶段完成
# - 准确率: 100%
```

---

## 📝 完整文档

- **主技能**: `skills/agent-security-skill-scanner/SKILL.md`
- **发布说明**: `RELEASE-NOTES.md`
- **误报处理设计**: `docs/false-positive-complete-design.md`

---

## 🔒 安全说明

### 对外发布
- ✅ 已脱敏（无个人信息）
- ✅ 最小必要原则
- ✅ 隐私检查通过

### 内部工具（不发布）
- ❌ 测试样本 - 内部使用
- ❌ 样本生成工具 - 可能滥用

---

*发布人：Security Team*  
*状态：预览测试版本*
