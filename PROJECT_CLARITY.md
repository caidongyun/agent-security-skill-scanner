# Scanner 项目澄清文档

**日期**: 2026-04-14  
**目的**: 明确项目结构、版本关系、开发流程

---

## 📁 项目位置

### 统一项目根目录
```
~/.openclaw/workspace/agent-security-skill-scanner-master/
├── release/
│   ├── v5.8.0/              # 当前生产版本
│   └── v6.0.0/              # 新架构版本 (开发中)
├── docs/                     # 项目文档
├── tests/                    # 测试
└── external-rules/           # 外部规则资源
```

### 当前问题
- v5.8.0 在 `~/.openclaw/workspace/agent-security-skill-scanner-master/`
- v6.0.0 在 `~/agent-security-skill-scanner/` (**位置不对！**)

### 解决方案
**立即整合到统一目录**:
```bash
# 移动 v6.0.0 到正确位置
mv ~/agent-security-skill-scanner/release/v6.0.0 \
   ~/.openclaw/workspace/agent-security-skill-scanner-master/release/

# 移动文档
mv ~/agent-security-skill-scanner/docs \
   ~/.openclaw/workspace/agent-security-skill-scanner-master/

mv ~/agent-security-skill-scanner/plans \
   ~/.openclaw/workspace/agent-security-skill-scanner-master/
```

---

## 📦 版本关系

### v5.8.0 (生产版本)
- **状态**: ✅ 已发布
- **位置**: `release/v5.8.0/`
- **用途**: 生产环境使用
- **维护**: Bug 修复，安全更新

### v5.9.0 (过渡版本) - 可选
- **状态**: ⏳ 规划中
- **位置**: `release/v5.9.0/`
- **用途**: 仅 Pattern 改进 (Gitleaks + Semgrep)
- **维护**: 快速发布，降低风险

### v6.0.0 (新架构版本)
- **状态**: 🚧 开发中
- **位置**: `release/v6.0.0/`
- **用途**: 完整新架构 (Pattern + AST + LLM)
- **维护**: 主要开发分支

---

## 🏗️ 项目结构

```
agent-security-skill-scanner-master/
│
├── release/
│   ├── v5.8.0/                    # v5.8.0 发布版本
│   │   ├── src/                   # 源代码
│   │   │   ├── engines/           # 检测引擎
│   │   │   │   ├── __init__.py    # Scanner 主类
│   │   │   │   ├── pattern_engine.py
│   │   │   │   ├── rule_engine.py
│   │   │   │   ├── ast_engine.py
│   │   │   │   └── llm_engine.py
│   │   │   └── rules/             # 规则文件
│   │   ├── rules/                 # 规则配置
│   │   ├── scripts/               # 扫描脚本
│   │   └── reports/               # 扫描报告
│   │
│   └── v6.0.0/                    # v6.0.0 开发版本
│       ├── src/                   # 新架构代码
│       ├── external-rules/        # 外部规则
│       │   ├── gitleaks.toml
│       │   ├── ai/                # Semgrep AI 规则
│       │   └── converted/         # 转换后的规则
│       └── docs/                  # v6.0.0 文档
│
├── docs/                          # 项目文档 (共享)
│   ├── ARCHITECTURE.md            # 架构设计
│   ├── USER_GUIDE.md              # 用户指南
│   └── API.md                     # API 文档
│
├── plans/                         # 规划文档
│   ├── SCANNER_V6_DESIGN.md       # v6.0.0 设计
│   ├── IMPLEMENTATION_PLAN.md     # 实施计划
│   ├── SOLUTION_ANALYSIS.md       # 方案分析
│   └── PROJECT_CLARITY.md         # 本文档
│
├── tests/                         # 测试
│   ├── test_v5.8.0/               # v5.8.0 测试
│   └── test_v6.0.0/               # v6.0.0 测试
│
└── external-rules/                # 外部规则 (共享)
    ├── gitleaks/
    ├── semgrep-rules/
    └── bandit/
```

---

## 🔄 开发流程

### v5.8.0 维护流程
```
1. 发现 Bug
   ↓
2. 在 release/v5.8.0/ 修复
   ↓
3. 测试验证
   ↓
4. 发布 v5.8.1 (补丁版本)
```

### v6.0.0 开发流程
```
1. 需求分析
   ↓
2. 在 release/v6.0.0/ 开发
   ↓
3. 单元测试
   ↓
4. 集成测试
   ↓
5. 性能测试
   ↓
6. 发布 v6.0.0
```

### 规则更新流程
```
1. 从外部源同步规则
   (gitleaks.toml, semgrep-rules/, bandit/)
   ↓
2. 转换为 Scanner 格式
   ↓
3. 集成到对应版本
   ↓
4. 测试验证
```

---

## 📊 版本对比

| 特性 | v5.8.0 | v6.0.0 |
|------|--------|--------|
| **规则来源** | 内置 + 手动添加 | 内置 + Gitleaks + Semgrep + Bandit |
| **规则数量** | ~200 条 | ~300 条 |
| **检测引擎** | Pattern + Rule + AST | Pattern + AST + LLM(可选) |
| **架构** | 分层扫描 | 统一扫描 |
| **LLM 集成** | 无 | 可选确认 |
| **性能** | ~2ms/file | ~3-5ms/file |
| **状态** | ✅ 生产 | 🚧 开发中 |

---

## 🎯 下一步行动

### 立即行动
1. **整合 v6.0.0 到统一目录**
   ```bash
   mv ~/agent-security-skill-scanner/release/v6.0.0 \
      ~/.openclaw/workspace/agent-security-skill-scanner-master/release/
   ```

2. **清理临时目录**
   ```bash
   rm -rf ~/agent-security-skill-scanner/
   ```

3. **验证结构**
   ```bash
   ls -la ~/.openclaw/workspace/agent-security-skill-scanner-master/release/
   ```

### Phase 1: Gitleaks 集成 (今天)
- [ ] 解析 gitleaks.toml
- [ ] 转换为 Scanner Pattern
- [ ] 集成到 v6.0.0 PatternEngine
- [ ] 测试验证

---

## 📝 常见问题

### Q: v5.8.0 和 v6.0.0 能共存吗？
A: 可以，都在 `release/` 目录下，互不影响。

### Q: 规则如何共享？
A: 外部规则放在 `external-rules/`，v5.8.0 和 v6.0.0 都可以使用。

### Q: 文档放在哪里？
A: 
- 项目共享文档：`docs/`
- v6.0.0 专用文档：`release/v6.0.0/docs/` 或 `plans/`

### Q: 测试如何组织？
A: 
- v5.8.0 测试：`tests/test_v5.8.0/`
- v6.0.0 测试：`tests/test_v6.0.0/`

---

## 📁 关键文件位置

| 文件 | 位置 | 说明 |
|------|------|------|
| **v5.8.0 代码** | `release/v5.8.0/src/` | 生产代码 |
| **v6.0.0 代码** | `release/v6.0.0/src/` | 开发代码 |
| **设计文档** | `plans/SCANNER_V6_DESIGN.md` | v6.0.0 设计 |
| **实施计划** | `plans/IMPLEMENTATION_PLAN.md` | 16 天计划 |
| **Gitleaks 规则** | `external-rules/gitleaks.toml` | 50+ 规则 |
| **Semgrep AI 规则** | `external-rules/ai/` | 112+ 规则 |

---

*项目澄清文档*
*2026-04-14*
