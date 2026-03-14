# Agent Security Skill Scanner - 项目简报

> **版本**: v2.0.1-beta | **日期**: 2026-03-14 | **状态**: 公开测试版

---

## 📌 项目概述

**Agent Security Skill Scanner** 是 AI Agent 技能安全扫描器，检测恶意技能、后门代码、权限滥用。

⚠️ **Beta 版本**: 公开测试中，可能存在未知问题，生产环境请谨慎使用。

---

## 🎯 核心功能

1. **静态分析引擎** - 检测 eval/exec 滥用、混淆代码、硬编码凭据 (98% 检出率)
2. **动态检测引擎** - 运行时行为监控、沙箱执行分析
3. **风险评分系统** - 0-100 分量化风险，五级分类 (CRITICAL/HIGH/MEDIUM/LOW/SAFE)
4. **并行扫描优化** - 4-8 倍性能提升，支持 100+ 技能批量扫描

---

## 📊 测试数据

| 指标 | 数值 | 说明 |
|------|------|------|
| 检测规则 | 110 条 | 5 大类别 |
| 综合检出率 | 95.6% | 2,100 个测试样本 |
| 误报率 | 3.0% | 正常样本测试 |
| 扫描速度 | 2.3 秒/技能 | 平均耗时 |
| 样本库规模 | 298,381 个 | 真实技能样本 |

---

## 🚀 快速开始

```bash
# 方式 1: Git 克隆
git clone https://github.com/caidongyun/agent-security-skill-scanner.git
cd agent-security-skill-scanner
./install.sh

# 方式 2: PyPI (即将发布)
pip install agent-security-scanner

# 方式 3: npm 规则库 (即将发布)
npm install agent-security-rules

# 使用
python cli.py scan <skill_directory>
```

---

## 📦 发布渠道

| 平台 | 状态 | 链接 |
|------|------|------|
| **GitHub** | ✅ 已发布 | https://github.com/caidongyun/agent-security-skill-scanner |
| **Gitee** | ✅ 已发布 | https://gitee.com/caidongyun/agent-security-skill-scanner |
| **ClawHub** | ⏳ 配置完成 | OpenClaw 内置市场 |

> **注**: PyPI、npm、Hugging Face 等平台正在内部测试中，暂不对外公开。

---

## 🛡️ 使用场景

- **技能市场审核** - 新技能上架前安全扫描
- **企业 Agent 治理** - 内部技能库安全审计
- **开发者自检** - 发布前安全自测
- **CI/CD 集成** - 自动化安全检查

---

## 📝 技术栈

- **语言**: Python 3.8+
- **核心代码**: 3,338 行
- **模块数**: 10 个核心模块
- **许可**: MIT License

---

## ⚠️ Beta 说明

**此版本为公开测试版 (Beta)**:
- 功能可能发生变化
- 可能存在未知 Bug
- 不建议用于生产环境
- 欢迎反馈问题和改进建议

**反馈渠道**:
- GitHub Issues: https://github.com/caidongyun/agent-security-skill-scanner/issues
- Gitee Issues: https://gitee.com/caidongyun/agent-security-skill-scanner/issues

---

## 📈 版本演进

| 版本 | 日期 | 核心能力 |
|------|------|---------|
| v1.0 | 2026-02-15 | 基础静态分析 |
| v1.5 | 2026-02-28 | 动态检测 + 白名单 |
| v2.0 | 2026-03-10 | 并行扫描 + 自动迭代 |
| v2.0.1-beta | 2026-03-14 | 多语言支持 + 完整文档 |

---

## 🔗 相关链接

- **项目仓库**: https://github.com/caidongyun/agent-security-skill-scanner
- **文档**: https://github.com/caidongyun/agent-security-skill-scanner/blob/master/README.md
- **发布指南**: https://github.com/caidongyun/agent-security-skill-scanner/blob/master/docs/PUBLISH_GUIDE.md

---

*最后更新：2026-03-14 | 版本：v2.0.1-beta | 状态：公开测试版*
