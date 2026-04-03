# 🚀 快速开始指南

**5 分钟上手 Agent Security Skill Scanner**

---

## 前置要求

- Python 3.10+
- Linux/macOS (Windows 需 WSL)
- 可选：systemd (用于守护进程)

---

## 安装 (3 分钟)

### 1. 克隆/进入项目

```bash
cd ~/.openclaw/workspace/skills/agent-security-skill-scanner/expert_mode
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 验证安装

```bash
python3 -c "import yaml, requests, fastapi; print('✅ 依赖安装成功')"
```

---

## 使用 (2 分钟)

### 方式一：单次扫描

```bash
# 扫描单个文件
python3 round30/autonomous_security.py scan ./your_code.py

# 扫描目录
python3 round30/autonomous_security.py scan ./your_project/

# 输出示例：
# 🔍 扫描中...
# 📊 发现 3 个可疑项
# 🚨 高危：2 个
# ⚠️  中危：1 个
```

### 方式二：实时监控

```bash
# 监控目录变化
python3 round30/autonomous_security.py watch ./your_project/

# 输出示例：
# 👁️  监控中：./your_project/
# 📁 文件变化：new_file.py
# 🔍 扫描结果：安全 ✅
```

### 方式三：自治系统 (7x24)

```bash
# 启动自治系统
python3 round30/autonomous_security.py run

# 输出示例：
# 🚀 自治安全系统启动
# 🔍 执行自动扫描...
# ✅ 扫描完成
# ⚙️  执行规则优化...
# ✅ 优化完成
```

### 方式四：守护进程 (生产环境)

```bash
# 安装 systemd 服务
sudo bash round14/install_daemon.sh

# 查看状态
systemctl status lingshun

# 查看日志
journalctl -u lingshun -f
```

---

## Web 仪表板

```bash
# 启动仪表板
cd round24/dashboard
python3 main.py

# 访问 http://localhost:8000/dashboard
```

仪表板功能：
- 📊 实时检测流量
- 🚨 告警管理
- 📈 统计分析
- ⚙️ 规则配置

---

## 配置

### 编辑配置文件

```bash
# 自治系统配置
vim autonomous_config.json
```

### 关键配置项

```json
{
  "auto_scan": true,           // 自动扫描
  "auto_optimize": true,       // 自动优化规则
  "auto_intel_update": true,   // 自动更新情报
  "scan_interval": 300,        // 扫描间隔 (秒)
  "alert_webhook": "https://..."  // 告警 webhook
}
```

---

## 验证质量

```bash
# 运行质量验证
python3 quality_validator.py --round auto

# 查看报告
cat round_quality/quality_report.md
```

---

## 常见问题

### Q: 扫描速度慢？

A: 使用 Rust 引擎 (round26/) 或开启分布式扫描 (round25/)

### Q: 误报太多？

A: 调整规则阈值或添加白名单

### Q: 如何添加新规则？

A: 使用 AI 辅助生成：
```bash
python3 round28/rule_optimizer_ai.py add --attack-type tool_poisoning
```

### Q: 如何查看日志？

A: 
```bash
# 守护进程日志
journalctl -u lingshun -f

# 应用日志
tail -f logs/lingshun_daemon.log
```

---

## 下一步

- 📖 阅读 [README.md](README.md) 了解完整功能
- 📚 查看 [DAEMON_GUIDE.md](DAEMON_GUIDE.md) 部署守护进程
- 🔧 参考 [docs/](docs/) 深入配置

---

**🎉 开始使用吧！**
