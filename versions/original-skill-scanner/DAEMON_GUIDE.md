# 🧠 灵顺 V5 守护进程使用指南

## 快速开始

### 1. 启动守护进程

```bash
cd /home/cdy/.openclaw/workspace/skills/agent-security-skill-scanner/expert_mode

# 方式 1: 直接启动
python3 lingshun_daemon.py start

# 方式 2: 使用管理脚本
./lingshunctl.sh start

# 方式 3: 使用 systemd (需要 root)
sudo ./lingshunctl.sh install
sudo ./lingshunctl.sh enable
sudo systemctl start lingshun
```

### 2. 查看状态

```bash
# 查看运行状态
python3 lingshun_daemon.py status

# 或
./lingshunctl.sh status
```

输出示例:
```
✅ 灵顺 V5 正在运行
   PID: 12345
   启动时间：2026-03-17T08:00:00
   当前轮次：5 / ∞
   当前任务：规则研发
   状态：running
   样本探索：15
   规则生成：8
   测试通过：120
   测试失败：2
```

### 3. 查看日志

```bash
# 查看最近 50 行日志
python3 lingshun_daemon.py logs

# 查看最近 100 行日志
python3 lingshun_daemon.py logs --lines 100

# 实时跟踪日志
python3 lingshun_daemon.py logs --follow

# 或使用管理脚本
./lingshunctl.sh follow
```

### 4. 停止守护进程

```bash
# 优雅停止
python3 lingshun_daemon.py stop

# 或
./lingshunctl.sh stop

# systemd 方式
sudo systemctl stop lingshun
```

### 5. 重启守护进程

```bash
python3 lingshun_daemon.py restart
# 或
./lingshunctl.sh restart
```

---

## 配置选项

### 调整轮次间隔

默认每 5 分钟 (300 秒) 执行一轮迭代，可以自定义：

```bash
# 设置为 10 分钟一轮
python3 lingshun_daemon.py start --round-interval 600

# 或编辑 lingshun_daemon.py 修改默认值
```

### 日志轮转

日志文件自动轮转，配置：
- 单个文件最大：10MB
- 保留备份数：5 个
- 日志位置：`logs/lingshun_daemon.log`

---

## 状态文件

守护进程状态保存在以下文件：

| 文件 | 说明 |
|------|------|
| `.lingshun_daemon.pid` | 进程 ID |
| `.lingshun_daemon_state.json` | 运行状态 |
| `logs/lingshun_daemon.log` | 日志文件 |

### 状态文件结构

```json
{
  "started_at": "2026-03-17T08:00:00",
  "last_heartbeat": "2026-03-17T08:30:00",
  "round": 5,
  "total_rounds": 0,
  "current_task": "规则研发",
  "status": "running",
  "last_error": null,
  "metrics": {
    "samples_explored": 15,
    "rules_generated": 8,
    "tests_passed": 120,
    "tests_failed": 2
  }
}
```

---

## systemd 服务管理

### 安装服务

```bash
# 安装 systemd 服务文件
sudo ./lingshunctl.sh install

# 启用开机自启
sudo ./lingshunctl.sh enable

# 启动服务
sudo systemctl start lingshun

# 查看状态
sudo systemctl status lingshun
```

### 常用命令

```bash
sudo systemctl start lingshun      # 启动
sudo systemctl stop lingshun       # 停止
sudo systemctl restart lingshun    # 重启
sudo systemctl status lingshun     # 状态
sudo systemctl enable lingshun     # 启用自启
sudo systemctl disable lingshun    # 禁用自启
sudo journalctl -u lingshun -f     # 查看日志
```

### 卸载服务

```bash
sudo ./lingshunctl.sh disable
sudo ./lingshunctl.sh uninstall
```

---

## 监控与告警

### 检查进程是否存活

```bash
# 方法 1: 检查 PID 文件
cat .lingshun_daemon.pid | xargs ps -p

# 方法 2: 使用状态命令
python3 lingshun_daemon.py status

# 方法 3: systemd
sudo systemctl is-active lingshun
```

### 健康检查脚本

创建 `healthcheck.sh`:

```bash
#!/bin/bash
cd /home/cdy/.openclaw/workspace/skills/agent-security-skill-scanner/expert_mode

if python3 lingshun_daemon.py status | grep -q "正在运行"; then
    echo "✅ 灵顺 V5 健康"
    exit 0
else
    echo "❌ 灵顺 V5 异常，尝试重启..."
    python3 lingshun_daemon.py start
    exit 1
fi
```

添加到 crontab 每分钟检查：

```bash
* * * * * /path/to/healthcheck.sh
```

---

## 故障排查

### 问题 1: 无法启动

```bash
# 检查是否已在运行
python3 lingshun_daemon.py status

# 检查端口占用
lsof -i :<端口>

# 查看错误日志
tail -100 logs/lingshun_daemon.log
```

### 问题 2: 进程消失

```bash
# 检查系统日志
journalctl -xe

# 检查资源限制
ulimit -a

# 查看 OOM 记录
dmesg | grep -i "killed process"
```

### 问题 3: 日志不更新

```bash
# 检查磁盘空间
df -h

# 检查文件权限
ls -la logs/

# 手动写入测试
echo "test" >> logs/lingshun_daemon.log
```

---

## 最佳实践

### 1. 使用 systemd 管理

推荐生产环境使用 systemd：
- 自动重启
- 日志集成
- 资源限制
- 依赖管理

### 2. 定期备份状态

```bash
# 每天备份状态文件
0 0 * * * cp .lingshun_daemon_state.json /backup/$(date +\%Y\%m\%d)_state.json
```

### 3. 日志分析

```bash
# 统计错误数量
grep "ERROR" logs/lingshun_daemon.log | wc -l

# 查看最近错误
grep "ERROR" logs/lingshun_daemon.log | tail -20

# 提取关键指标
grep "质量评估" logs/lingshun_daemon.log | tail -10
```

### 4. 资源监控

```bash
# 监控 CPU/内存
top -p $(cat .lingshun_daemon.pid)

# 监控文件描述符
lsof -p $(cat .lingshun_daemon.pid) | wc -l
```

---

## API 集成 (可选)

可以通过读取状态文件集成到监控系统：

```python
import json
from pathlib import Path

state_file = Path(".lingshun_daemon_state.json")
if state_file.exists():
    state = json.load(open(state_file))
    print(f"状态：{state['status']}")
    print(f"轮次：{state['round']}")
    print(f"任务：{state['current_task']}")
```

---

## 安全注意事项

1. **权限控制**: 守护进程以当前用户运行，不要使用 root
2. **文件权限**: 确保状态文件和日志文件权限正确 (600)
3. **网络安全**: 如需远程访问，建议通过 SSH 隧道
4. **日志审计**: 定期检查日志，发现异常行为

---

## 更新与升级

```bash
# 停止当前版本
python3 lingshun_daemon.py stop

# 更新代码
git pull

# 启动新版本
python3 lingshun_daemon.py start

# 验证状态
python3 lingshun_daemon.py status
```

---

## 支持

遇到问题？

1. 查看日志：`logs/lingshun_daemon.log`
2. 检查状态：`.lingshun_daemon_state.json`
3. 查看系统日志：`journalctl -xe`
4. 联系支持：提供日志和状态文件
