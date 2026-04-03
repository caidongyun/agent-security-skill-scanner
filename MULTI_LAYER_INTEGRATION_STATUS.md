# 🏗️ 多层架构集成状态

**版本**: v1.0  
**创建时间**: 2026-04-03  
**目标**: 对齐历史系统设计

---

## 📊 多层检测架构

| 层级 | 功能 | 状态 | 文件位置 |
|------|------|------|----------|
| **Layer 1** | YARA 规则 | ✅ 已集成 | `rules/scanner_v3/yara/scanner_rules.yar` |
| **Layer 2** | 意图识别 | ⏳ 待集成 | `expert_mode/intent_analyzer.py` (待创建) |
| **Layer 3** | AST 分析 | ✅ 可用 | `expert_mode/round16/ast_analyzer.py` |
| **Layer 4** | 控制流 | ⏳ 待集成 | `expert_mode/round20/cfg_analyzer.py` (待创建) |
| **Layer 5** | 语义分析 | ⏳ 待集成 | `expert_mode/round19/semantic_detector.py` (待创建) |
| **Layer 6** | 行为分析 | ✅ 可用 | `agent-security-skill-scanner-gitee/dynamic_detector.py` |
| **Layer 7** | ML 分类 | ✅ 可用 | `round24/integration/ml_classifier.py` |
| **Layer 8** | LLM 分析 | ❌ 禁用 | - |

---

## ✅ 已可用检测器

### Layer 1: YARA 规则
- **文件**: `rules/scanner_v3/yara/scanner_rules.yar`
- **规则数**: 544 条
- **状态**: ✅ 运行中

### Layer 3: AST 分析
- **文件**: `expert_mode/round16/ast_analyzer.py`
- **功能**: 代码抽象语法树分析，检测混淆代码
- **状态**: ✅ 文件存在

### Layer 6: 行为分析
- **文件**: `agent-security-skill-scanner-gitee/dynamic_detector.py`
- **功能**: 运行时行为检测
- **状态**: ✅ 文件存在

### Layer 7: ML 分类
- **文件**: `round24/integration/ml_classifier.py`
- **功能**: 机器学习分类
- **状态**: ✅ 文件存在

---

## ⏳ 待集成检测器

### Layer 2: 意图识别
- **目标文件**: `expert_mode/intent_analyzer.py`
- **状态**: ⏳ 待创建
- **参考**: 历史系统中的 intent_analyzer

### Layer 4: 控制流
- **目标文件**: `expert_mode/round20/cfg_analyzer.py`
- **状态**: ⏳ 待创建
- **参考**: round20/cfg_generator.py

### Layer 5: 语义分析
- **目标文件**: `expert_mode/round19/semantic_detector.py`
- **状态**: ⏳ 待创建
- **参考**: round19/semantic_detector.py

---

## 🎯 集成计划

### 阶段 1: 基础层 (已完成)
- ✅ Layer 1: YARA 规则

### 阶段 2: 静态分析层 (进行中)
- ✅ Layer 3: AST 分析
- ⏳ Layer 2: 意图识别
- ⏳ Layer 4: 控制流
- ⏳ Layer 5: 语义分析

### 阶段 3: 动态分析层 (待开始)
- ⏳ Layer 6: 行为分析
- ⏳ Layer 7: ML 分类

### 阶段 4: 智能分析层 (可选)
- ❌ Layer 8: LLM 分析

---

## 🔧 使用方法

```bash
cd ~/.openclaw/workspace/agent-security-skill-scanner-master

# 运行多层扫描器
python3 multi_layer_scanner.py

# 查看状态
cat MULTI_LAYER_INTEGRATION_STATUS.md
```

---

## 📈 当前进度

```
多层架构集成进度:
████████░░░░░░░░░░░░░░ 40% (4/8 层)

已完成:
- Layer 1: YARA 规则
- Layer 3: AST 分析
- Layer 6: 行为分析
- Layer 7: ML 分类

待完成:
- Layer 2: 意图识别
- Layer 4: 控制流
- Layer 5: 语义分析
- Layer 8: LLM 分析 (可选)
```

---

## 💡 下一步

1. **集成意图识别** - 创建 intent_analyzer.py
2. **集成控制流** - 创建 cfg_analyzer.py
3. **集成语义分析** - 创建 semantic_detector.py
4. **统一接口** - 所有检测器使用相同输入输出格式
5. **综合判断** - 多层结果加权投票

---

**目标**: 恢复历史系统的完整多层架构！ 🎯
