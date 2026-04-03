# 质量门禁系统设计 - Quality Gate v2.0

**版本**: v2.0  
**创建时间**: 2026-03-25  
**状态**: ✅ 已实现

---

## 🎯 设计目标

在样本生成和规则生成流程中引入**自动化质量门禁**，确保：

1. **样本质量**: 生成的恶意样本符合质量标准
2. **规则质量**: YARA 规则结构完整、语法有效
3. **流程控制**: 质量不达标时自动停止，防止劣质产物进入下一阶段
4. **可追溯**: 所有质量检查结果都有详细报告

---

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                   编排流程 (Makefile)                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  generate ──→ check-gate-sample ──→ rules ──→ scan    │
│                    ↓                      ↓             │
│              quality_report          quality_report     │
│                                                         │
└─────────────────────────────────────────────────────────┘
                         ↓
            ┌────────────────────────┐
            │   Quality Gatekeeper   │
            ├────────────────────────┤
            │ - 样本检查             │
            │ - 规则检查             │
            │ - 批量检查             │
            │ - 决策引擎             │
            └────────────────────────┘
                         ↓
            ┌────────────────────────┐
            │    质量报告 (JSON+MD)   │
            └────────────────────────┘
```

---

## 📋 质量检查项

### 样本质量检查 (Sample Quality Checks)

| 检查项 | 说明 | 阈值 | 权重 |
|--------|------|------|------|
| **文件大小** | 代码行数在合理范围内 | 100-5000 行 | 20% |
| **代码结构** | 包含必需模式 (import/def/if) | 3 个必需 | 25% |
| **恶意模式** | 包含至少 2 个恶意指标 | ≥2 个 | 30% |
| **安全性** | 不包含真正危险的命令 | 0 危险 | 25% (一票否决) |

**恶意指标示例**:
- `subprocess` - 系统命令执行
- `socket` - 网络通信
- `base64` - 编码混淆
- `eval(`/`exec(` - 动态代码执行
- `.ssh` - SSH 密钥访问
- `credential`/`password` - 凭据相关

### 规则质量检查 (Rule Quality Checks)

| 检查项 | 说明 | 阈值 | 权重 |
|--------|------|------|------|
| **必需段落** | 包含 meta/strings/condition | 3 个必需 | 25% |
| **字符串数量** | 规则字符串数量合理 | 2-20 个 | 25% |
| **语法有效性** | YARA 语法正确 | 无错误 | 30% |
| **元数据完整性** | 包含 description/author/severity | ≥2 个 | 20% |

---

## 🚪 门禁决策逻辑

```python
def make_decision(report):
    # 1. 关键失败 → 直接拒绝
    if critical_failures > 0:
        return 'fail'
    
    # 2. 通过率不足 → 拒绝
    if pass_rate < 80%:
        return 'fail'
    
    # 3. 总分不足 → 拒绝
    if overall_score < 70:
        return 'fail'
    
    # 4. 有错误级别失败 → 需要审查
    if error_failures > 0:
        return 'review'
    
    # 5. 全部通过 → 允许
    return 'pass'
```

**决策结果**:
- ✅ **pass**: 质量达标，继续执行
- ⚠️ **review**: 需要人工审查
- ❌ **fail**: 质量不达标，停止执行

---

## 🔧 使用方法

### CLI 命令

```bash
# 检查单个样本
python3 -m quality_gate.gatekeeper \
  --mode sample \
  --input output/samples/python/data_exfil_000.py \
  --output reports/quality_single

# 检查单个规则
python3 -m quality_gate.gatekeeper \
  --mode rule \
  --input output/rules/python_data_exfil.yar \
  --output reports/quality_rule

# 批量检查样本
python3 -m quality_gate.gatekeeper \
  --mode batch \
  --input output/samples/python/ \
  --output reports/quality_batch \
  --threshold 70
```

### Makefile 集成

```bash
# 仅检查样本质量
make check-gate-sample

# 仅检查规则质量
make check-gate-rule

# 完整流程 (含质量门禁)
make all

# 调整质量阈值
make all THRESHOLD=80
```

---

## 📊 输出报告

### JSON 格式 (机器可读)

```json
{
  "timestamp": "2026-03-25T17:30:00",
  "total_items": 50,
  "passed_items": 45,
  "failed_items": 3,
  "overall_score": 82.5,
  "decision": "pass",
  "checks": [
    {
      "name": "batch_summary",
      "passed": true,
      "score": 82.5,
      "message": "总计：50 | 通过：45 | 失败：3 | 待审查：2"
    }
  ]
}
```

### Markdown 格式 (人类可读)

```markdown
# 质量门禁报告

**生成时间**: 2026-03-25T17:30:00
**门禁决策**: ✅ 通过

## 📊 汇总
- 总项目数：50
- 通过数：45
- 失败数：3
- 总体得分：82.5/100

## 🔍 详细检查
| 检查项 | 状态 | 得分 | 详情 |
|--------|------|------|------|
| batch_summary | ✅ | 82 | 总计：50 | 通过：45 | ... |
| pass_rate | ✅ | 90 | 通过率：45/50 = 90.0% |
| quality_score | ✅ | 82 | 平均质量分：82.5 |

## 💡 建议
✅ 质量符合要求，可以进入下一阶段。
```

---

## 🎛️ 配置选项

### 阈值配置

```python
THRESHOLDS = {
    'sample': {
        'min_size': 100,      # 最小行数
        'max_size': 5000,     # 最大行数
        'min_complexity': 5,  # 最小复杂度
        'max_similarity': 0.9, # 最大相似度
    },
    'rule': {
        'min_strings': 2,     # 最小字符串数
        'max_strings': 20,    # 最大字符串数
        'valid_syntax': True, # 语法有效
    },
    'gate': {
        'min_pass_rate': 0.8,   # 最小通过率 80%
        'min_overall_score': 70, # 最小总分 70
        'critical_failures': 0,  # 关键失败数 0
    }
}
```

### 自定义配置

```bash
# 通过配置文件
python3 -m quality_gate.gatekeeper \
  --config config/quality_thresholds.yaml \
  --mode batch \
  --input output/samples/python/

# 通过命令行
python3 -m quality_gate.gatekeeper \
  --threshold 80 \
  --mode batch \
  --input output/samples/python/
```

---

## 📈 质量指标追踪

### 批次质量趋势

| 批次 | 样本数 | 通过率 | 平均分 | 决策 |
|------|--------|--------|--------|------|
| Batch-001 | 50 | 90% | 82.5 | ✅ pass |
| Batch-002 | 50 | - | - | ⏳ pending |

### 常见问题 Top 5

1. ⚠️ 文件太小 (<100 行)
2. ⚠️ 缺少恶意模式
3. ❌ 代码结构不完整
4. ⚠️ YARA 字符串太少
5. ❌ 元数据缺失

---

## 🔄 持续改进

### Phase 1 (已完成) ✅
- [x] 基础质量检查
- [x] 门禁决策引擎
- [x] 报告生成
- [x] Makefile 集成

### Phase 2 (进行中) 🚧
- [ ] 代码相似度检测 (防止重复)
- [ ] 复杂度分析 (AST 解析)
- [ ] 规则覆盖率验证
- [ ] 历史趋势分析

### Phase 3 (计划中) 📋
- [ ] 机器学习质量预测
- [ ] 自动修复建议
- [ ] 质量仪表板
- [ ] CI/CD 集成

---

## 💡 最佳实践

### 1. 设置合理阈值
```bash
# 开发阶段：宽松
make all THRESHOLD=60

# 生产阶段：严格
make all THRESHOLD=80
```

### 2. 定期审查失败样本
```bash
# 查看失败报告
cat reports/quality_sample.md | grep "❌"

# 分析失败原因
python3 reports/analyze_failures.py
```

### 3. 持续优化生成器
```bash
# 根据质量反馈调整模板
edit templates/python/*.template

# 重新生成并验证
make clean && make all
```

---

## 🎯 质量目标

| 指标 | 当前 | 目标 | 状态 |
|------|------|------|------|
| 样本通过率 | 90% | ≥85% | ✅ |
| 规则通过率 | 100% | ≥90% | ✅ |
| 平均质量分 | 82.5 | ≥75 | ✅ |
| 关键失败数 | 0 | 0 | ✅ |

---

## 📚 相关文件

- `quality_gate/gatekeeper.py` - 质量门禁核心实现
- `Makefile` - 编排脚本 (集成门禁)
- `reports/quality_*.md` - 质量报告
- `config/quality_thresholds.yaml` - 阈值配置 (可选)

---

**质量门禁是保证产出质量的关键机制，宁可错杀不可放过！**
