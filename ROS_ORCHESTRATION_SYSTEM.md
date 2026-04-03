# ROS 编排脚本系统总览

**版本**: v2.0  
**更新时间**: 2026-04-02  
**状态**: ✅ 完整编排系统

---

## 📚 脚本分类

### 1. 核心编排脚本

| 脚本 | 用途 | 状态 |
|------|------|------|
| `ros_cycle.py` | 核心循环引擎 | ✅ |
| `ros_eval.py` | 评估引擎 | ✅ |
| `ros_self_learner.py` | 自学习引擎 | ✅ |
| `ros_test.py` | 测试引擎 | ✅ |
| `ros-train.sh` | 训练主流程 | ✅ |
| `ros-train-v2.sh` | 训练 v2 流程 | ✅ |
| `ros-train-v3.py` | 训练 v3 流程 | ✅ |

### 2. 优化脚本系列

| 脚本 | 用途 | 优化目标 |
|------|------|----------|
| `ros-01-rule-optimization.sh` | 规则优化循环 | FP < 5% |
| `ros-02-fine-tune.sh` | 精细调优 | FP < 2% |
| `ros-03-whitelist-optimize.sh` | 白名单优化 | FP < 1% |
| `ros-04-100percent-optimization.sh` | 100% 准确率优化 | DR > 98% |
| `ros-05-rapid-optimize.sh` | 快速优化 (2 小时) | FP -50% |

### 3. 训练脚本系列

| 脚本 | 用途 | 批量 |
|------|------|------|
| `ros-01-batch-train.sh` | 批量训练 | 标准 |
| `ros-01-batch-train-full.sh` | 批量训练 | 全量 |
| `ros-01-train-improve.sh` | 训练改进 | 迭代 |

### 4. Orchestrator 脚本

| 脚本 | 用途 |
|------|------|
| `ros-orchestrator/ros-benchmark.sh` | Benchmark 自动化 |
| `ros-orchestrator/ros-deep-scan.sh` | 深度扫描 |
| `ros-orchestrator/ros-fault-tolerance.sh` | 容错处理 |
| `ros-orchestrator/ros-health-daemon.sh` | 健康守护 |
| `ros-orchestrator/ros-taskmaster.sh` | 任务调度 |

### 5. 扩展脚本

| 脚本 | 用途 |
|------|------|
| `scripts/ros-15-rule-expansion.sh` | 规则扩展 |
| `scripts/ros-16-sample-expansion.sh` | 样本扩展 |

### 6. 扫描器

| 脚本 | 版本 | 用途 |
|------|------|------|
| `scanner-master/ros-scanner.py` | v1 | 基础扫描 |
| `scanner-master/ros-scanner-v2.py` | v2 | 增强扫描 |

---

## 🔄 完整编排流程

```
┌─────────────────────────────────────────────────────────────┐
│                    ROS 编排系统 v2.0                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 需求输入                                                │
│     └─ 用户需求 / 系统检测 / 定期回顾                       │
│                                                             │
│  2. 任务规划 (ros-planning/)                                │
│     ├─ 需求分析 (LLM)                                       │
│     ├─ 任务分解                                             │
│     └─ 资源分配                                             │
│                                                             │
│  3. 执行编排                                                │
│     ├─ 训练流程 (ros-train*.sh)                             │
│     ├─ 优化流程 (ros-01 ~ ros-05)                           │
│     └─ 测试流程 (ros_test.py)                               │
│                                                             │
│  4. 质量保障                                                │
│     ├─ Benchmark (ros-benchmark.sh)                         │
│     ├─ 深度扫描 (ros-deep-scan.sh)                          │
│     └─ 健康监控 (ros-health-daemon.sh)                      │
│                                                             │
│  5. 自学习循环                                              │
│     ├─ 评估 (ros_eval.py)                                   │
│     ├─ 学习 (ros_self_learner.py)                           │
│     └─ 优化 (ros_cycle.py)                                  │
│                                                             │
│  6. 发布部署                                                │
│     ├─ 版本打包                                             │
│     ├─ 文档更新                                             │
│     └─ 持续监控                                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 常用编排命令

### 快速启动

```bash
# 1. 完整训练流程
./ros-train.sh

# 2. 规则优化循环
./ros-01-rule-optimization.sh

# 3. 快速优化 (2 小时)
./ros-05-rapid-optimize.sh

# 4. Benchmark 测试
./ros-orchestrator/ros-benchmark.sh

# 5. 深度扫描
./ros-orchestrator/ros-deep-scan.sh
```

### 自动化循环

```bash
# 启动健康守护
./ros-orchestrator/ros-health-daemon.sh start

# 启动任务调度
./ros-orchestrator/ros-taskmaster.sh start

# 查看状态
./ros-orchestrator/ros-health-daemon.sh status
```

---

## 📊 编排能力矩阵

| 能力 | 脚本 | 自动化程度 |
|------|------|------------|
| **需求分析** | ros-planning/ | 半自动 |
| **任务规划** | ros-planning/ | 半自动 |
| **样本生成** | ros-16-sample-expansion.sh | ✅ 自动 |
| **规则生成** | ros-15-rule-expansion.sh | ✅ 自动 |
| **规则优化** | ros-01 ~ ros-05 | ✅ 自动 |
| **训练迭代** | ros-train*.sh | ✅ 自动 |
| **测试验证** | ros_test.py | ✅ 自动 |
| **Benchmark** | ros-benchmark.sh | ✅ 自动 |
| **健康监控** | ros-health-daemon.sh | ✅ 自动 |
| **容错处理** | ros-fault-tolerance.sh | ✅ 自动 |
| **自学习** | ros_self_learner.py | 🔄 开发中 |
| **自主优化** | ros_cycle.py | 🔄 开发中 |

---

## 📋 今日增强

### 新增脚本

| 脚本 | 用途 | 状态 |
|------|------|------|
| `scripts/progress_reporter.py` | 进度汇报 (每 5 分钟) | ✅ |
| `skills/clawhub-integration/sync_from_clawhub_cn.py` | ClawHub 同步 | ✅ |
| `skills/clawhub-integration/download_for_analysis.py` | 下载用于分析 | ✅ |
| `ros-planning/PLANNING_SYSTEM.md` | 规划系统文档 | ✅ |

### 新增能力

| 能力 | 说明 |
|------|------|
| **定时汇报** | 每 5 分钟自动汇报进度 |
| **外部技能集成** | ClawHub CN Mirror 同步 |
| **需求规划** | LLM 辅助需求分析 |
| **检测能力提升** | 学习→融合→自主架构 |

---

## 🎯 编排示例

### 示例 1: 完整优化流程

```bash
#!/bin/bash
# 完整优化流程

# 1. 规则优化
./ros-01-rule-optimization.sh

# 2. 精细调优
./ros-02-fine-tune.sh

# 3. 白名单优化
./ros-03-whitelist-optimize.sh

# 4. Benchmark 验证
./ros-orchestrator/ros-benchmark.sh

# 5. 生成报告
python3 scripts/progress_reporter.py
```

### 示例 2: 快速响应流程

```bash
#!/bin/bash
# 2 小时快速优化

# 1. 快速优化
./ros-05-rapid-optimize.sh

# 2. 验证扫描
python3 scanner-master/ros-scanner-v2.py samples/malicious/

# 3. 生成报告
python3 scripts/progress_reporter.py
```

### 示例 3: 自主循环流程

```bash
#!/bin/bash
# 自主循环 (守护进程)

# 1. 启动健康守护
./ros-orchestrator/ros-health-daemon.sh start

# 2. 启动任务调度
./ros-orchestrator/ros-taskmaster.sh start

# 3. 启动自学习
python3 ros_self_learner.py &

# 4. 启动循环引擎
python3 ros_cycle.py &
```

---

## 📁 文件组织

```
agent-security-skill-scanner-master/
├── ros-*.sh                      # ROS 脚本 (主目录)
├── ros-*.py                      # ROS Python 脚本
├── ros-planning/                 # 规划系统
│   └── PLANNING_SYSTEM.md
├── ros-orchestrator/             # 编排器脚本
│   ├── ros-benchmark.sh
│   ├── ros-deep-scan.sh
│   ├── ros-fault-tolerance.sh
│   ├── ros-health-daemon.sh
│   └── ros-taskmaster.sh
├── scanner-master/               # 扫描器
│   ├── ros-scanner.py
│   └── ros-scanner-v2.py
├── scripts/                      # 辅助脚本
│   ├── progress_reporter.py
│   ├── ros-15-rule-expansion.sh
│   └── ros-16-sample-expansion.sh
└── skills/                       # 技能
    ├── clawhub-integration/
    └── ...
```

---

## 🔧 使用指南

### 新手入门

```bash
# 1. 查看可用脚本
ls -la ros-*.sh ros-*.py

# 2. 运行快速优化
./ros-05-rapid-optimize.sh

# 3. 查看进度
cat reports/progress/LATEST.md

# 4. 运行 Benchmark
./ros-orchestrator/ros-benchmark.sh
```

### 高级使用

```bash
# 1. 自定义编排
vim my_custom_workflow.sh

# 2. 设置定时任务
crontab -e
# 添加：0 2 * * * ./ros-train.sh

# 3. 监控日志
tail -f logs/ros_*.log

# 4. 查看状态
./ros-orchestrator/ros-health-daemon.sh status
```

---

**系统状态**: ✅ 完整编排系统就绪  
**脚本总数**: 20+ 个  
**自动化程度**: 70% (目标 90%+)  
**详细文档**: `ROS_ORCHESTRATION_SYSTEM.md`
