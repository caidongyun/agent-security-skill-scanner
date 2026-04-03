# 持续优化自动化流程

本目录包含完整的规则持续优化自动化系统。

## 📁 文件结构

```
agent-security-skill-scanner-master/
├── optimize_rules.sh          # 主优化脚本
├── manage_rules.sh            # 版本管理脚本
├── quality_gate_config.json   # 质量门禁配置
├── performance_config.json    # 性能基准配置
└── rules/
    ├── versions/              # 版本目录
    │   ├── v1.0/
    │   ├── v1.1/
    │   └── ...
    └── CHANGELOG.md           # 变更日志
```

## 🚀 快速开始

### 1. 运行自动化优化

```bash
# 执行完整优化流程
./optimize_rules.sh

# 输出:
# - Benchmark 测试结果
# - 失败样本分析
# - 优化建议
# - 规则权重调整
# - 质量门禁检查
# - 性能基准测试
```

### 2. 管理规则版本

```bash
# 创建新版本
./manage_rules.sh version v1.1 "优化检测率和误报率"

# 查看所有版本
./manage_rules.sh list

# 恢复旧版本
./manage_rules.sh restore v1.0

# 比较版本差异
./manage_rules.sh compare v1.0 v1.1

# 备份当前规则
./manage_rules.sh backup manual_backup
```

## 📊 质量门禁标准

### 核心指标

| 指标 | 目标值 | 关键性 |
|------|--------|--------|
| **检测率 (Recall)** | ≥80% | 🔴 Critical |
| **误报率 (FPR)** | <10% | 🔴 Critical |
| **F1 Score** | ≥85% | 🔴 Critical |
| **精确率 (Precision)** | ≥80% | 🟡 Warning |

### 性能指标

| 指标 | 目标值 | 关键性 |
|------|--------|--------|
| **单规则扫描时间** | <10ms | 🔴 Critical |
| **千规则扫描时间** | <100ms | 🔴 Critical |
| **内存使用** | <512MB | 🟡 Warning |

## 🔄 优化流程

```
┌─────────────────────────────────────────────┐
│  1. 运行 Benchmark 测试                      │
│     - 扫描恶意/白样本                         │
│     - 收集检测结果                           │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  2. 分析失败样本                             │
│     - 误报 (False Positives)                │
│     - 漏报 (False Negatives)                │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  3. 生成优化建议                             │
│     - 按攻击类型分析                         │
│     - 按难度分级分析                         │
│     - 优先级排序                             │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  4. 自动调整规则权重                         │
│     - 备份当前规则                           │
│     - 调整低检测率规则权重                   │
│     - 保存调优日志                           │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  5. 质量门禁检查                             │
│     - 检测率 ≥80%                           │
│     - 误报率 <10%                           │
│     - F1 Score ≥85%                         │
└──────────────┬──────────────────────────────┘
               │
         ┌─────┴─────┐
         │           │
      通过 ✅     失败 ❌
         │           │
         │           ▼
         │    ┌─────────────────┐
         │    │ 生成优化计划    │
         │    │ 人工介入优化    │
         │    └─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  6. 性能基准测试                             │
│     - 单规则性能 <10ms                      │
│     - 批量扫描 <100ms                       │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  7. 版本化保存                               │
│     - 创建 rules/versions/vX.X/            │
│     - 更新 CHANGELOG.md                     │
└─────────────────────────────────────────────┘
```

## 📈 持续集成

### CI/CD 集成示例

```yaml
# .github/workflows/quality-gate.yml
name: Quality Gate

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Optimization
        run: ./optimize_rules.sh
      
      - name: Check Quality Gate
        run: |
          python3 quality_gate/gatekeeper.py \
            --config quality_gate_config.json \
            --output reports/quality_gate.json
      
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: quality-report
          path: reports/
```

### 定期优化任务

```bash
# 添加 crontab 任务
# 每周日凌晨 2 点自动运行优化
0 2 * * 0 cd /path/to/scanner && ./optimize_rules.sh >> logs/optimization.log 2>&1
```

## 🔍 故障排查

### 常见问题

#### 1. 检测率不达标

**现象**: 检测率 <80%

**排查步骤**:
```bash
# 查看详细分析报告
cat reports/benchmark_*_analysis.json | jq '.recommendations'

# 检查哪些攻击类型检测率低
cat reports/benchmark_*.json | jq '.by_attack_type'
```

**解决方案**:
- 针对低检测率攻击类型增加规则
- 调整规则权重
- 优化匹配逻辑

#### 2. 误报率过高

**现象**: 误报率 ≥10%

**排查步骤**:
```bash
# 查看误报样本
cat reports/benchmark_*_analysis.json | jq '.false_positives'

# 检查规则过于宽泛
grep -r "wide_match" rules/*.yaml
```

**解决方案**:
- 收紧规则条件
- 增加排除条件
- 降低过于敏感规则的权重

#### 3. 性能不达标

**现象**: 扫描时间 > 阈值

**排查步骤**:
```bash
# 查看性能报告
cat reports/performance_*.json | jq '.'

# 找出慢规则
cat reports/performance_*.json | jq '.slow_rules'
```

**解决方案**:
- 优化复杂规则的正则表达式
- 减少字符串数量
- 使用更高效的匹配模式

## 📚 相关文档

- [ARCHITECTURE.md](./ARCHITECTURE.md) - 系统架构
- [QUALITY_GATE_DESIGN.md](./QUALITY_GATE_DESIGN.md) - 质量门禁设计
- [BENCHMARK_REPORT_20260328.md](./BENCHMARK_REPORT_20260328.md) - Benchmark 测试报告

## 🎯 最佳实践

### 1. 版本命名规范

```
v<major>.<minor>[.patch]

示例:
- v1.0 - 初始版本
- v1.1 - 优化检测率
- v1.1.1 - 紧急修复
- v2.0 - 重大更新
```

### 2. CHANGELOG 编写规范

```markdown
## [v1.1] - 2026-03-28

### Added
- 新增 10 条 PowerShell 提权检测规则

### Changed
- 优化 Bash 脚本检测逻辑，检测率从 8% 提升至 35%

### Fixed
- 修复 JavaScript 规则误报问题

### Security
- 新增供应链攻击检测规则
```

### 3. 优化频率建议

- **日常**: 每次规则更新后运行 `./optimize_rules.sh`
- **每周**: 审查优化报告，手动调整复杂规则
- **每月**: 版本化发布，更新 CHANGELOG

## 📞 支持

如有问题，请查看:
- 日志文件：`logs/optimization.log`
- 报告目录：`reports/`
- 版本备份：`rules/versions/`

---

*最后更新：2026-03-28*
