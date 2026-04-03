# Scanner V3 Web Dashboard - 独立部署

## 📁 目录结构

```
web-dashboard/
├── server.py          # Web 服务器（独立运行）
├── dashboard_data.json # 数据文件（JSON）
├── sync_data.py       # 数据同步脚本
└── README.md          # 本文档
```

## 🚀 启动方法

### 1. 启动 Web 服务

```bash
cd ~/.openclaw/workspace/agent-security-skill-scanner-V3/web-dashboard
python3 server.py
```

### 2. 后台运行（推荐）

```bash
cd ~/.openclaw/workspace/agent-security-skill-scanner-V3/web-dashboard
nohup python3 server.py > /tmp/web-dashboard.log 2>&1 &
echo $! > /tmp/web-dashboard.pid
```

### 3. 停止服务

```bash
kill $(cat /tmp/web-dashboard.pid) 2>/dev/null || pkill -f "web-dashboard/server.py"
```

## 🔄 数据同步

### 手动同步

```bash
python3 web-dashboard/sync_data.py
```

### 自动同步（可选）

添加到 crontab（每 5 分钟同步一次）：

```bash
*/5 * * * * python3 /home/cdy/.openclaw/workspace/agent-security-skill-scanner-V3/web-dashboard/sync_data.py
```

## 🌐 访问地址

- **本机**: http://localhost:8080
- **远程**: http://192.168.0.103:8080

## ✅ 优势

1. **隔离性**: Web 服务与主扫描程序完全分离
2. **稳定性**: 主程序崩溃不影响 Web 仪表板
3. **独立性**: 可以独立重启/更新 Web 服务
4. **轻量**: 只读取 JSON 数据文件，无复杂依赖

## 📊 数据格式

`dashboard_data.json` 结构：

```json
{
  "round15": {"samples": 353, "detection_rate": "100%", "p99_latency": "0.01ms"},
  "round16": {"files": 353, "malicious": 353, "detection_rate": "100%"},
  "round17": {"agents": 4, "framework": "✅", "mode": "顺序/并行"},
  "round18": {"mode": "多进程", "improvement": "4-8x", "cache_hit": "90%+"},
  "summary": {
    "total_samples": 353,
    "detection_rate": "100%",
    "rules": 214,
    "false_positive": "0%",
    "performance": "4-8x"
  },
  "updated": "2026-03-24 17:08:00"
}
```

## 🔧 自定义

修改 `sync_data.py` 中的 `sync_data()` 函数，可以从主程序读取实际报告文件并更新数据。
