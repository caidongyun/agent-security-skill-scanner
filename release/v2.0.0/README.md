# Agent Security Skill Scanner v2.0.0

> **发布日期**: 2026-03-13  
> **版本**: v2.0.0  
> **状态**: ✅ 正式发布

---

## 🎯 新增功能（v2.0.0）

### 误报处理系统
- ✅ **本地白名单** - 文件/模式/规则/哈希 4 种类型
- ✅ **远程分析** - LLM 上下文关联分析
- ✅ **隐私保护** - 公共/个人白名单分离
- ✅ **官方采集** - 自动采集可信技能

---

## 📦 包内容

```
release/v2.0.0/
├── README.md                     # 本文件
├── REGRESSION-TEST.md            # 回归测试方案
├── scanner_cli.py                # 主扫描器
├── static_analyzer.py            # 静态分析器
└── whitelist/                    # 误报处理系统
    ├── whitelist_manager.py      # 白名单管理
    ├── remote_analyzer.py        # 远程分析
    ├── init_official.py          # 官方采集
    └── privacy_check.py          # 隐私检查
```

---

## 🚀 快速开始

### 安装
```bash
# 复制发布包到项目
cp -r release/v2.0.0/ your-project/agent-security-scanner/
```

### 基础扫描
```bash
python agent-security-scanner/scanner_cli.py \
  --target skills/your-skill/ \
  --format json
```

### 使用白名单
```bash
# 1. 初始化个人配置
cp agent-security-scanner/whitelist/public.json \
   agent-security-scanner/whitelist/local.json

# 2. 扫描（自动应用白名单）
python agent-security-scanner/scanner_cli.py \
  --target skills/your-skill/ \
  --use-whitelist
```

---

## 📊 v1.x → v2.0.0 升级

### 变更
- 新增误报处理系统
- 优化扫描性能
- 改进报告格式

### 兼容性
- ✅ 向后兼容 v1.x
- ✅ 配置文件格式不变
- ✅ CLI 参数兼容

---

## 🧪 回归测试

运行回归测试验证功能：
```bash
# 查看测试方案
cat REGRESSION-TEST.md

# 运行测试
python scanner_cli.py --target samples/real_skills/ --use-whitelist
```

---

## 📝 完整文档

- **主技能**: `skills/agent-security-skill-scanner/SKILL.md`
- **误报处理设计**: `docs/false-positive-complete-design.md`
- **隐私保护指南**: `docs/whitelist-privacy-guide.md`
- **发布审查清单**: `PUBLISH-REVIEW.md`

---

## 🔒 安全说明

### 对外发布
- ✅ 已脱敏（无个人信息）
- ✅ 最小必要原则
- ✅ 隐私检查通过

### 内部工具（不发布）
- ❌ `ai_agent_attack_generator.py` - 样本生成（可能滥用）
- ❌ `code_security_generator.py` - 恶意代码生成
- ❌ `evaluation_metrics.py` - 内部评估

详见：`PUBLISH-REVIEW.md`

---

*发布人：Security Team*  
*审核状态：✅ 已通过*
