# 📋 t14g2-v1 → V3 迁移指南

**版本**: v3.0.0  
**日期**: 2026-03-22  
**兼容性**: 向后兼容 t14g2-v1

---

## 🎯 迁移概述

V3 在 t14g2-v1 的基础上增加了 Multi-Agent 架构，保持了 100% 的功能兼容性。

### 核心变化

| 特性 | t14g2-v1 | V3 | 兼容性 |
|------|----------|-----|--------|
| **架构** | 单体 | Multi-Agent | ✅ 兼容层提供 |
| **检测引擎** | Rust+Python | Rust+Python | ✅ 完全相同 |
| **规则库** | 350+ 条 | 350+ 条 | ✅ 完全相同 |
| **样本库** | 850+ 个 | 850+ 个 | ✅ 完全相同 |
| **API** | 直接调用 | Agent 协调 | ✅ 兼容层提供 |
| **新增** | - | 6 个 Agent | 🆕 Multi-Agent |
| **新增** | - | research-dev-agent | 🆕 智能研发 |

---

## 📦 升级步骤

### 步骤 1: 备份原有配置

```bash
# 备份 t14g2-v1 配置
cd ~/.openclaw/workspace/skills/agent-security-skill-scanner/expert_mode
cp config.yaml config.yaml.backup
cp rules/optimized/*.yaml backup_rules/
```

### 步骤 2: 下载 V3

```bash
cd ~/.openclaw/workspace
git clone https://gitee.com/caidongyun/agent-security-skill-scanner-master.git agent-security-skill-scanner-V3
```

### 步骤 3: 迁移配置 (可选)

```bash
# V3 会自动使用 versions/t14g2-v1 的配置
# 如果有自定义配置，手动复制

cd ~/.openclaw/workspace/agent-security-skill-scanner-V3
cp /path/to/old/config.yaml ./config.yaml
```

### 步骤 4: 安装依赖

```bash
cd ~/.openclaw/workspace/agent-security-skill-scanner-V3
pip install -r requirements.txt
```

### 步骤 5: 测试验证

```bash
# 方式 1: 使用兼容层 API (推荐)
python3 -c "
from compat import Scanner
scanner = Scanner()
result = scanner.scan_file('./samples/malicious/test1.py')
print(result)
"

# 方式 2: 使用 Multi-Agent API
python3 -c "
import asyncio
from agents.orchestrator import OrchestratorAgent
from agents.base_agent import Task

async def test():
    orch = OrchestratorAgent()
    task = Task(type='scan', parameters={'target': './samples/malicious/'})
    result = await orch.execute(task)
    print(result.data)

asyncio.run(test())
"

# 方式 3: 使用 CLI
python3 main.py --scan ./samples/malicious/
```

### 步骤 6: 切换流量

确认测试通过后，将生产流量切换到 V3:

```bash
# 停止 t14g2-v1 守护进程
sudo systemctl stop lingshun

# 启动 V3 守护进程
cd ~/.openclaw/workspace/agent-security-skill-scanner-V3
sudo cp daemon/lingshun.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start lingshun
sudo systemctl enable lingshun
```

---

## 🔧 API 迁移

### 方式 1: 使用兼容层 (推荐) ⭐

**无需修改代码**, 直接替换导入:

```python
# t14g2-v1 原代码
from engine.scanner import Scanner
scanner = Scanner()
result = scanner.scan_file("./target.py")

# V3 新代码 (完全兼容)
from compat import Scanner
scanner = Scanner()
result = scanner.scan_file("./target.py")
```

### 方式 2: 使用 Multi-Agent API (新功能)

```python
import asyncio
from agents.orchestrator import OrchestratorAgent
from agents.base_agent import Task

async def scan_with_agents():
    orchestrator = OrchestratorAgent()
    
    # 创建扫描任务
    task = Task(
        type="scan",
        parameters={"target": "./target.py"}
    )
    
    # 执行任务
    result = await orchestrator.execute(task)
    
    if result.success:
        print(f"检测完成：{result.data}")
    else:
        print(f"检测失败：{result.error}")

asyncio.run(scan_with_agents())
```

### 方式 3: 使用 CLI

```bash
# 扫描文件
python3 main.py --scan ./target.py

# 扫描目录
python3 main.py --scan ./project/

# 查看统计
python3 main.py --stats

# 启动守护进程
python3 main.py --daemon
```

---

## 📊 功能对比

### 检测能力

| 功能 | t14g2-v1 | V3 | 说明 |
|------|----------|-----|------|
| 文件扫描 | ✅ | ✅ | 完全相同 |
| 目录扫描 | ✅ | ✅ | 完全相同 |
| 内容检测 | ✅ | ✅ | 完全相同 |
| L1 快速匹配 | ✅ | ✅ | 完全相同 |
| L2 指标分析 | ✅ | ✅ | 完全相同 |
| L3 深度检测 | ✅ | ✅ | 完全相同 |
| 规则数量 | 350+ | 350+ | 完全相同 |
| 样本数量 | 850+ | 850+ | 完全相同 |

### 新增功能 (V3 独有)

| 功能 | 说明 |
|------|------|
| **Multi-Agent** | 6 个 Agent 协作 |
| **智能研发** | research-dev-agent 集成 |
| **任务编排** | 自动任务分解和分发 |
| **结果聚合** | 多 Agent 结果自动汇总 |
| **扩展性** | 支持水平扩展 |

---

## ⚠️ 注意事项

### 1. 性能差异

由于 Multi-Agent 架构有额外的协调开销:

| 指标 | t14g2-v1 | V3 | 说明 |
|------|----------|-----|------|
| p99 延迟 | <1ms | <5ms | Multi-Agent 开销 |
| 吞吐量 | 1000+/s | 800+/s | 略降但仍达标 |
| 内存占用 | 500MB | 800MB | Agent 额外开销 |

**建议**: 
- 高性能场景使用兼容层 API
- 复杂任务使用 Multi-Agent API

### 2. 配置文件

V3 支持两种配置格式:

```yaml
# V3 新格式 (推荐)
version: "3.0"
mode: "multi-agent"
agents:
  orchestrator:
    enabled: true
  detector:
    enabled: true

# t14g2-v1 格式 (兼容)
version: "2.0"
mode: "monolithic"
engine:
  rules_path: "./rules/optimized/"
  samples_path: "./samples/"
```

### 3. 守护进程

V3 的守护进程同时支持两种模式:

```bash
# 单用户模式 (兼容 t14g2-v1)
python3 daemon/lingshun_daemon.py --mode monolithic

# Multi-Agent 模式 (默认)
python3 daemon/lingshun_daemon.py --mode multi-agent
```

---

## 🧪 测试验证

### 回归测试

```bash
cd ~/.openclaw/workspace/agent-security-skill-scanner-V3

# 运行 t14g2-v1 的测试用例
python3 versions/t14g2-v1/round10/auto_test.py

# 运行 V3 的测试
python3 tests/regression_test.py

# 性能基准测试
python3 tests/benchmark.py
```

### 验收标准

- [ ] 检测率 ≥99.5% (与 t14g2-v1 一致)
- [ ] 误报率 ≤0.3% (与 t14g2-v1 一致)
- [ ] 所有历史测试用例通过
- [ ] 性能在可接受范围内

---

## 🔄 回滚方案

如果 V3 出现问题，可以快速回滚到 t14g2-v1:

```bash
# 停止 V3 守护进程
sudo systemctl stop lingshun

# 恢复 t14g2-v1 守护进程
cd ~/.openclaw/workspace/skills/agent-security-skill-scanner/expert_mode
sudo cp round14/lingshun.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start lingshun

# 验证恢复
python3 -c "from engine.scanner import Scanner; print(Scanner().scan_file('./test.py'))"
```

---

## 📞 常见问题

### Q1: V3 和 t14g2-v1 能共存吗？

**A**: 可以。两个版本在不同目录，互不影响。

### Q2: 必须使用 Multi-Agent 吗？

**A**: 不必须。可以使用兼容层 API，体验和 t14g2-v1 完全相同。

### Q3: 规则库需要重新编写吗？

**A**: 不需要。V3 完全兼容 t14g2-v1 的规则格式。

### Q4: 样本库需要迁移吗？

**A**: 不需要。V3 已包含完整的样本库。

### Q5: 如何发挥 V3 的最大优势？

**A**: 逐步将复杂任务迁移到 Multi-Agent API，简单任务继续使用兼容层。

---

## 📚 相关文档

- [README.md](README.md) - 项目说明
- [ARCHITECTURE.md](ARCHITECTURE.md) - 架构设计
- [QUICKSTART.md](QUICKSTART.md) - 快速开始
- [VERSION_MERGE_REPORT.md](VERSION_MERGE_REPORT.md) - 版本整合报告

---

**🎉 迁移完成！开始使用 V3 的 Multi-Agent 能力！**
