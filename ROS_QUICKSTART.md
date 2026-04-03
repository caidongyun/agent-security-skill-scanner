# 🚀 ROS 快速开始指南

## 5 分钟上手

### 1. 运行第一轮

```bash
cd /home/cdy/.openclaw/workspace/agent-security-skill-scanner-master
python3 ros_cycle.py
```

**输出示例**:
```
🔄 ROS 循环 #1 - 2026-03-28 23:04
📊 步骤 1: 分析当前状态
  检测率：95.8%
  误报率：0.0%
  F1 Score: 97.8%

📋 步骤 2: 规划本轮任务
  📝 优化 persistence (90.0% → 95%)
  📝 优化 data_exfil (90.0% → 95%)

🔧 步骤 3: 执行任务
  ✅ persistence_rules.yar (+3 rules)
  ✅ data_exfil_rules.yar (+3 rules)

📈 步骤 4: 验证效果
  检测率：95.8% → 96.3% (+0.5%)

💡 步骤 5: 反思总结
  ✅ 成功！检测率提升 +0.5%
```

---

### 2. 启动持续循环

```bash
# 每 60 分钟自动运行一轮
python3 ros_cycle.py --loop --interval 60
```

**后台运行** (推荐):
```bash
nohup python3 ros_cycle.py --loop --interval 60 > ros_logs/loop.log 2>&1 &
```

---

### 3. 查看进展

```bash
# 查看最新日志
tail ros_logs/cycle_001.md

# 查看历史记录
cat ros_meta/history.json | python3 -m json.tool

# 查看目标追踪
cat ros_meta/targets.md
```

---

## 核心命令

| 命令 | 说明 |
|------|------|
| `python3 ros_cycle.py` | 运行单轮 |
| `python3 ros_cycle.py --loop` | 持续循环 |
| `python3 ros_cycle.py --loop --interval 30` | 30 分钟一轮 |
| `tail ros_logs/cycle_*.md` | 查看日志 |

---

## 目录结构

```
agent-security-skill-scanner-master/
├── ros_cycle.py              # 核心脚本
├── ros_logs/                 # 循环日志 ← 每轮生成
│   ├── cycle_001.md
│   ├── cycle_002.md
│   └── ...
├── ros_meta/                 # 元数据 ← 自动维护
│   ├── history.json          # 历史记录
│   └── targets.md            # 目标追踪
└── rules/scanner_v3/yara/    # 规则文件 ← 持续优化
```

---

## 典型工作流

### 场景 1: 日常监控
```bash
# 早上查看昨晚进展
tail -20 ros_logs/*.md

# 启动白天循环
python3 ros_cycle.py --loop --interval 60 &

# 傍晚查看进展
cat ros_meta/history.json | python3 -c "
import sys, json
h = json.load(sys.stdin)
print(f\"今日运行：{len(h)} 轮\")
if h:
    print(f\"最新检测率：{h[-1]['after']['detection_rate']:.1f}%\")
"
```

---

### 场景 2: 集中优化
```bash
# 短时间内密集优化
python3 ros_cycle.py --loop --interval 15

# 每 15 分钟一轮，快速迭代
# 适合大版本发布前
```

---

### 场景 3: 问题排查
```bash
# 查看失败轮次
cat ros_meta/history.json | python3 -c "
import sys, json
h = json.load(sys.stdin)
failures = [x for x in h if not x['reflection']['success']]
print(f\"失败轮次：{len(failures)}\")
for f in failures[-3:]:
    print(f\"  Cycle #{f['cycle']}: {f['reflection']['improvement']:+.1f}%\")
"
```

---

## 配置调优

编辑 `ros_cycle.py` 开头的 `CONFIG`:

```python
CONFIG = {
    'target_detection_rate': 98.0,  # 目标检测率
    'min_improvement': 0.5,         # 最小提升阈值 (%)
    'loop_interval_minutes': 60,    # 循环间隔 (分钟)
}
```

---

## 质量保障

### 自动检查
- ✅ 每轮必须运行 benchmark
- ✅ 检测率提升 <0.5% → 标记"效果不佳"
- ✅ 误报率 >0% → 告警
- ✅ 连续 3 轮不佳 → 建议调整策略

### 经验积累
- 📝 每轮反思日志
- 📊 每日自动报告
- 📈 每周总结

---

## 常见问题

### Q: 如何停止循环？
```bash
# 前台运行：Ctrl+C
# 后台运行：kill $(pgrep -f ros_cycle.py)
```

### Q: 日志太多怎么办？
```bash
# 只保留最近 30 轮
ls -t ros_logs/cycle_*.md | tail -n +31 | xargs rm
```

### Q: 如何恢复历史版本？
```bash
# 回滚到 cycle_025 的版本
cp rules/scanner_v3/yara/all_rules_v25.yar \
   rules/scanner_v3/yara/all_rules_current.yar
```

---

## 成功指标

### 1 周后
- [ ] 运行 ≥10 轮
- [ ] 检测率提升至 97%+
- [ ] 积累 20+ 条经验

### 1 月后
- [ ] 运行 ≥50 轮
- [ ] 检测率提升至 98%+
- [ ] 经验库 100+ 条

---

**创建日期**: 2026-03-28  
**版本**: v1.0  
**维护**: ROS 研究循环框架

---

## 🔥 Harness Engineering 集成 (新增)

### 什么是 Harness Engineering?

Harness Engineering 是 2024-2025 年 AI Agent 领域的热门方向，专注于：
- ✅ Agent 自动化测试
- ✅ Agent 评估基准
- ✅ Agent 编排框架
- ✅ Agent 监控和可观测性
- ✅ 自动化工作流

### ROS + Harness 集成

**已创建文档**: `HARNESS_ENGINEERING_INTEGRATION.md`

**快速集成**:
```bash
# 1. 安装监控工具
pip install agentops

# 2. 配置监控
python3 -c "
import agentops
agentops.init(api_key='your-key')
"

# 3. 创建测试套件
python3 ros_test.py

# 4. 运行基准测试
python3 ros_eval.py
```

### 新增组件

| 组件 | 文件 | 功能 |
|------|------|------|
| 测试层 | `ros_test.py` | 单元/集成/回归/压力测试 |
| 评估层 | `ros_eval.py` | 基准测试 + 版本对比 |
| 编排层 | `ros_orchestrator.py` | 顺序/并行/条件/循环 |
| 监控层 | `ros_monitor.py` | 仪表盘 + 告警 |
| 工作流 | `ros_workflow.py` | 自动化工作流引擎 |

### GitHub Actions 集成

```yaml
# .github/workflows/ros-cycle.yml
name: ROS Auto Cycle
on:
  schedule:
    - cron: '0 * * * *'  # 每小时
jobs:
  run-ros:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python3 ros_cycle.py
```

详见：`HARNESS_ENGINEERING_INTEGRATION.md`
