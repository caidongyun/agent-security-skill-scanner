# 📍 Scanner Master 文件索引

**版本**: v3.1  
**最后更新**: 2026-04-01  
**总文件数**: 20+

---

## 📁 核心脚本

| 文件 | 路径 | 功能 | 行数 | 状态 |
|------|------|------|------|------|
| `scan` | `scanner-master/scan` | 统一入口 | 280 | ✅ v3.0 |
| `ros-scanner-v2.py` | `scanner-master/ros-scanner-v2.py` | 主扫描器 | 450 | ✅ YARA+Pattern+Intent |
| `ros-scanner.py` | `scanner-master/ros-scanner.py` | 简化版 | 280 | ✅ 保留 |
| `ros-deep-scan.sh` | `research-orchestrator/ros-deep-scan.sh` | 深度扫描 | 180 | ✅ 交叉验证 |

---

## 📁 规则文件

| 文件 | 路径 | 功能 | 规则数 | 状态 |
|------|------|------|--------|------|
| `merged_rules_fixed.yar` | `output/rules/` | YARA 合并 | 5 | ✅ 实际使用 |
| `python_code_execution.yar` | `output/rules/` | 代码执行 | 1 | ✅ |
| `python_credential_theft.yar` | `output/rules/` | 凭证窃取 | 1 | ✅ |
| `python_data_exfil.yar` | `output/rules/` | 数据外传 | 1 | ✅ |
| `python_general.yar` | `output/rules/` | 通用检测 | 1 | ✅ |
| `python_persistence.yar` | `output/rules/` | 持久化 | 1 | ✅ |
| `python_pattern_*.yar` | `output/rules/` | Pattern 规则 | 5 | ✅ |
| `python_all.yar` | `output/rules/` | 原始合并 | 10 | ⚠️ 包含重复 |

**YARA 规则总计**: 21 条 (去重后 5 条)

---

## 📁 索引文件

| 文件 | 路径 | 功能 | 数据量 | 状态 |
|------|------|------|--------|------|
| `payload-index.json` | `samples-index/` | Payload 索引 | 69,604 | ✅ |
| `payload-paths.txt` | `samples-index/` | 路径列表 | 69,604 | ✅ |
| `repository-index.json` | `samples-index/` | 仓库索引 | 94,829 | ✅ |
| `merged-ground-truth.json` | `ground-truth/` | Ground Truth | 69,796 | ✅ |
| `benign_samples.json` | `ground-truth/` | 良性样本 | - | ✅ |

---

## 📁 报告文件

| 文件 | 路径 | 功能 | 生成时间 | 状态 |
|------|------|------|---------|------|
| `README.md` | `scanner-master/` | 使用指南 | 2026-04-01 | ✅ 新建 |
| `FILE_INDEX.md` | `scanner-master/` | 文件索引 | 2026-04-01 | ✅ 本文档 |
| `COMPLETION_REPORT.md` | `scanner-master/` | 完成报告 | 2026-04-01 | ✅ |
| `INTENT_INTEGRATION_REPORT.md` | `scanner-master/` | Intent 集成 | 2026-04-01 | ✅ |
| `benchmark-report-*.md` | `output/` | 基准报告 | 2026-04-01 | ✅ |
| `yara-integration-report.md` | `output/` | YARA 集成 | 2026-04-01 | ✅ |
| `pattern-enhancement-report.md` | `output/` | Pattern 增强 | 2026-04-01 | ✅ |

---

## 📁 配置文件

| 文件 | 路径 | 功能 | 状态 |
|------|------|------|------|
| `config.json` | `expert_mode/` | 配置文件 | ✅ |
| `scan_targets.yaml` | `config/` | 扫描目标 | ✅ |

---

## 📁 依赖文件

| 文件 | 路径 | 功能 | 状态 |
|------|------|------|------|
| `intent_detector_v2.py` | `agent-security-skill-scanner-master/` | Intent 检测 | ✅ |
| `scanner_with_intent_v2.py` | `agent-security-skill-scanner-master/` | 集成扫描 | ✅ |

---

## 📊 统计信息

### 代码统计

| 类型 | 文件数 | 总行数 | 平均行数 |
|------|--------|--------|---------|
| **Python** | 10+ | 3,000+ | 300 |
| **Shell** | 5+ | 1,000+ | 200 |
| **YARA** | 11 | 288 | 26 |
| **Markdown** | 10+ | 2,000+ | 200 |
| **JSON** | 5+ | 50,000+ | 10,000 |

### 规则统计

| 层级 | 类型 | 数量 | 贡献 |
|------|------|------|------|
| **L1** | YARA 规则 | 5 条 | ~15% |
| **L2** | Pattern 规则 | 56 条 | ~83% |
| **L3** | Intent 分析 | 1 个 | ~2% |
| **总计** | - | **61+** | 100% |

### 样本统计

| 类型 | 数量 | 占比 |
|------|------|------|
| **总样本** | 69,604 | 100% |
| **恶意样本** | 53,668 | 77.1% |
| **良性样本** | 15,936 | 22.9% |
| **攻击类型** | 13 类 | - |

---

## 🗂️ 目录结构

```
~/.openclaw/workspace/
├── ai-work/skills/
│   ├── scanner-master/              # Scanner Master 主目录
│   │   ├── scan                     # ✅ 统一入口
│   │   ├── ros-scanner-v2.py        # ✅ 主扫描器
│   │   ├── ros-scanner.py           # ✅ 简化版
│   │   ├── README.md                # ✅ 使用指南
│   │   ├── FILE_INDEX.md            # ✅ 文件索引
│   │   ├── COMPLETION_REPORT.md     # ✅ 完成报告
│   │   └── INTENT_INTEGRATION_REPORT.md  # ✅ Intent 集成
│   │
│   └── research-orchestrator/       # ROS 编排
│       ├── ros-taskmaster.sh        # ✅ 任务编排
│       ├── ros-deep-scan.sh         # ✅ 深度扫描
│       └── ...
│
├── agent-security-skill-scanner-master/  # 现有扫描器
│   ├── output/rules/                # YARA 规则
│   │   ├── merged_rules_fixed.yar   # ✅ 5 条规则
│   │   └── python_*.yar             # ✅ 原始规则
│   ├── intent_detector_v2.py        # ✅ Intent 检测
│   └── ...
│
└── Desktop/security-benchmark/      # 样本库
    ├── samples/                     # 样本文件
    ├── samples-index/               # 索引文件
    │   ├── payload-index.json       # ✅ 69,604
    │   └── repository-index.json    # ✅ 94,829
    └── ground-truth/                # Ground Truth
        └── merged-ground-truth.json # ✅ 69,796
```

---

## 🔍 快速查找

### 找扫描器
```bash
# 主扫描器
ls -lh ~/.openclaw/workspace/ai-work/skills/scanner-master/ros-scanner-v2.py

# 简化版
ls -lh ~/.openclaw/workspace/ai-work/skills/scanner-master/ros-scanner.py
```

### 找规则
```bash
# YARA 规则
ls -lh ~/.openclaw/workspace/agent-security-skill-scanner-master/output/rules/
```

### 找索引
```bash
# Payload 索引
ls -lh /home/cdy/Desktop/security-benchmark/samples-index/
```

### 找报告
```bash
# 最新报告
ls -lt ~/.openclaw/workspace/agent-security-skill-scanner-master/output/*.md | head -5
```

---

## 📈 版本历史

| 版本 | 日期 | 关键变更 | 检测率 |
|------|------|---------|--------|
| **v1.0** | 2026-03-25 | 初始版本 | 51.9% |
| **v2.0** | 2026-04-01 | YARA 集成 | 67.8% |
| **v2.1** | 2026-04-01 | Pattern 增强 | 98.0% |
| **v3.0** | 2026-04-01 | 统一入口 | 98.0% |
| **v3.1** | 2026-04-01 | Intent 集成 | 98.0% |

---

## 🎯 维护指南

### 更新规则

1. 编辑 `output/rules/python_*.yar`
2. 运行 `./scan rules optimize`
3. 验证 `./scan rules validate`

### 更新索引

1. 运行 `manage-index.sh update`
2. 验证样本完整性

### 生成报告

1. 运行完整扫描
2. 自动生成 Markdown 报告
3. 保存到 `output/` 目录

---

**索引生成**: 2026-04-01  
**维护者**: Scanner Master Team
