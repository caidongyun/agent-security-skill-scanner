# 🔄 HROS Framework

**Harness-Enhanced Research Orchestration System**

## 核心理念

**简单 · 可靠 · 可追踪 · 自动化**

---

## 快速开始

### 单次运行
```bash
python3 ros_cycle.py
```

### 持续循环
```bash
python3 ros_cycle.py --loop --interval 60
```

---

## 核心组件

### 1. ros_cycle.py
ROS 核心循环脚本：分析→规划→执行→验证→反思

### 2. benchmark/benchmark_v3.py
基准测试工具

### 3. rules/scanner_v3/yara/
YARA 规则目录

---

## 输出

- **日志**: `ros_logs/cycle_*.md`
- **历史**: `ros_meta/history.json`

---

**版本**: v1.0 (回归简化版)
**状态**: ✅ 稳定可靠
