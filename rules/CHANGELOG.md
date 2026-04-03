# 规则变更日志 (CHANGELOG)

本文档记录规则系统的所有重要变更。

## 格式说明

- **Added**: 新增功能
- **Changed**: 变更现有功能
- **Deprecated**: 即将移除的功能
- **Removed**: 已移除的功能
- **Fixed**: 修复的问题
- **Security**: 安全相关的修复

---

## [v1.0] - 2026-03-28

### Description
初始版本 - 建立规则版本管理体系

### Changes
- 创建 rules/versions/v1.0/ 版本目录
- 建立 CHANGELOG 文档规范
- 集成质量门禁配置
- 性能基准：<10ms/单规则，<100ms/千规则

### Quality Metrics
- 检测率目标：≥80%
- 误报率目标：<10%
- F1 Score 目标：≥85%

### Files Included
- rules/*.yaml - Sigma/YARA 规则
- rules/*.json - IOC 规则
- rules/sigma/ - Sigma 规则目录
- rules/yara/ - YARA 规则目录

---

## [v0.9] - 2026-03-25

### Description
预发布版本 - 规则系统初始实现

### Added
- 基础 YARA 规则 (JS, PowerShell, Shell)
- Sigma 规则集成
- IOC 规则支持

### Known Issues
- Bash 脚本检测率偏低 (8.3%)
- JavaScript 检测能力待增强
- 权限提升类攻击规则缺失

---
