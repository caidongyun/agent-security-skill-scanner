# Scanner V3 Web Dashboard - 配置说明

## 📋 目录结构

```
web-dashboard/
├── server_v3.py          # Web 服务（支持本地/远程模式）
├── start.sh              # 启动脚本（推荐）
├── systemd-manager.sh    # systemd 管理脚本
├── scanner-web.service   # systemd 服务配置
├── dashboard_data.json   # 数据文件
├── auto_scan.py          # 自动化扫描
└── test_dashboard.py     # 自动化测试
```

---

## 🚀 快速开始

### 默认启动（本地模式）

```bash
cd ~/.openclaw/workspace/agent-security-skill-scanner-V3/web-dashboard
./start.sh
```

**访问**: http://localhost:8080（仅本机）

---

### 远程模式（需要时开启）

```bash
./start.sh remote
```

**访问**: 
- 本机：http://localhost:8080
- 远程：http://192.168.0.103:8080

---

## 📖 命令说明

### start.sh - 启动脚本

```bash
# 本地模式（默认）
./start.sh

# 远程模式
./start.sh remote

# 停止服务
./start.sh local stop

# 重启
./start.sh local restart

# 查看状态
./start.sh status
```

### systemd-manager.sh - 系统服务管理

```bash
# 安装 systemd 服务
./systemd-manager.sh install

# 启动本地模式
./systemd-manager.sh local

# 启动远程模式
./systemd-manager.sh remote

# 查看状态
./systemd-manager.sh status

# 停止服务
./systemd-manager.sh stop

# 重启服务
./systemd-manager.sh restart
```

---

## 🔧 systemd 配置

### 安装为系统服务

```bash
cd ~/.openclaw/workspace/agent-security-skill-scanner-V3/web-dashboard
./systemd-manager.sh install
```

### 开机自启动

```bash
sudo systemctl enable scanner-web
```

### 查看日志

```bash
journalctl -u scanner-web -f
```

---

## 📊 模式对比

| 模式 | 监听地址 | 访问范围 | 安全性 | 使用场景 |
|------|----------|----------|--------|----------|
| **本地** | 127.0.0.1:8080 | 仅本机 | 🔒 高 | 日常使用 |
| **远程** | 0.0.0.0:8080 | 局域网 | ⚠️ 中 | 需要共享时 |

---

## 🔄 切换模式

### 从本地切换到远程

```bash
# 1. 停止当前服务
./start.sh local stop

# 2. 启动远程模式
./start.sh remote
```

### 从远程切换到本地

```bash
# 1. 停止当前服务
./start.sh remote stop

# 2. 启动本地模式
./start.sh local
```

---

## 🔍 故障排查

### 查看服务状态

```bash
./start.sh status
```

### 查看日志

```bash
tail -f /tmp/scanner-web.log
```

### 检查端口占用

```bash
ss -tlnp | grep 8080
```

### 强制重启

```bash
# 停止所有相关进程
pkill -9 -f "server_v3.py"

# 重新启动
./start.sh
```

---

## 🛡️ 安全建议

1. **默认使用本地模式** - 仅本机访问
2. **需要时开启远程** - 用完即关闭
3. **防火墙配置** - 远程模式时限制访问 IP
4. **定期更新** - 保持服务最新

### 防火墙配置（远程模式时）

```bash
# 仅允许特定 IP 访问
sudo ufw allow from 192.168.0.0/24 to any port 8080

# 或仅允许特定机器
sudo ufw allow from 192.168.0.100 to any port 8080
```

---

## 📝 示例场景

### 场景 1: 日常开发（本地模式）

```bash
# 启动
./start.sh

# 访问
http://localhost:8080
```

### 场景 2: 团队协作（远程模式）

```bash
# 启动远程模式
./start.sh remote

# 告诉团队成员访问地址
# http://192.168.0.103:8080

# 用完关闭
./start.sh local stop
```

### 场景 3: 生产部署（systemd）

```bash
# 安装服务
./systemd-manager.sh install

# 启动本地模式
./systemd-manager.sh local

# 开机自启
sudo systemctl enable scanner-web
```

---

## 🎯 最佳实践

1. ✅ **默认本地** - 安全优先
2. ✅ **按需远程** - 用完即关
3. ✅ **systemd 管理** - 自动重启
4. ✅ **定期扫描** - 更新数据
5. ✅ **监控日志** - 及时发现问题

---

**建议**: 日常使用本地模式，需要分享时再开启远程模式！🔒
