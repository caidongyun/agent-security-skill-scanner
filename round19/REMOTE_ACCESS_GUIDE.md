# Web 仪表板 - 远程访问指南

## 🚀 启动服务

### 方式 1: 默认绑定 (推荐)
```bash
cd ~/.openclaw/workspace/agent-security-skill-scanner-V3
python3 round19/web_dashboard.py 8080
```
自动绑定 `0.0.0.0:8080`，支持本地和远程访问。

### 方式 2: 仅本地
```bash
python3 round19/web_dashboard.py 8080 127.0.0.1
```

### 方式 3: 自定义端口
```bash
python3 round19/web_dashboard.py 9000 0.0.0.0
```

---

## 🌐 访问地址

### 本机访问
```
http://localhost:8080
```

### 其他机器访问
```
http://<本机 IP>:8080
```

**获取本机 IP**:
```bash
hostname -I | awk '{print $1}'
# 例如：192.168.1.100
```

---

## 🔥 防火墙配置

### Ubuntu/Debian (UFW)
```bash
# 查看状态
sudo ufw status

# 开放 8080 端口
sudo ufw allow 8080/tcp

# 重新加载
sudo ufw reload

# 验证
sudo ufw status | grep 8080
```

### CentOS/RHEL (firewalld)
```bash
# 开放端口
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload

# 验证
sudo firewall-cmd --list-ports | grep 8080
```

### 直接使用 iptables
```bash
# 添加规则
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT

# 保存规则 (Ubuntu)
sudo netfilter-persistent save

# 保存规则 (CentOS)
sudo service iptables save
```

---

## ✅ 验证连接

### 本机测试
```bash
curl http://localhost:8080
```

### 远程测试 (从隔壁机器)
```bash
curl http://<本机 IP>:8080
```

### 浏览器访问
在其他机器浏览器打开：
```
http://<本机 IP>:8080
```

---

## 🐳 Docker 部署

如果使用 Docker Compose：

```yaml
# round20/docker-compose.yml
services:
  scanner-web:
    ports:
      - "8080:8080"  # 主机端口：容器端口
```

启动后，其他机器访问：
```
http://<Docker 主机 IP>:8080
```

---

## 🔒 安全建议

### 1. 限制访问 IP
```bash
# UFW 只允许特定 IP
sudo ufw allow from 192.168.1.0/24 to any port 8080
```

### 2. 使用反向代理 (Nginx)
```nginx
server {
    listen 80;
    server_name scanner.local;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # 只允许内网
        allow 192.168.0.0/16;
        deny all;
    }
}
```

### 3. 添加认证
修改 `web_dashboard.py` 添加基础认证：
```python
def do_GET(self):
    # 检查认证
    auth = self.headers.get('Authorization')
    if not self.check_auth(auth):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="Scanner"')
        self.end_headers()
        return
```

---

## 📊 完整示例

### 启动服务
```bash
cd ~/.openclaw/workspace/agent-security-skill-scanner-V3

# 启动 (绑定 0.0.0.0:8080)
python3 round19/web_dashboard.py

# 输出:
# 🌐 Web 仪表板运行中:
#   本地访问：http://localhost:8080
#   远程访问：http://192.168.1.100:8080
#   绑定地址：0.0.0.0:8080
# 💡 其他机器访问：http://<本机 IP>:8080
# ⚠️  确保防火墙开放端口 8080
```

### 开放防火墙
```bash
sudo ufw allow 8080/tcp
sudo ufw reload
```

### 从隔壁机器访问
```bash
# 在隔壁机器执行
curl http://192.168.1.100:8080

# 或浏览器访问
http://192.168.1.100:8080
```

---

## ❓ 故障排查

### 问题 1: 无法远程访问
```bash
# 检查服务是否运行
ps aux | grep web_dashboard

# 检查端口监听
netstat -tlnp | grep 8080
# 应该看到 0.0.0.0:8080 而不是 127.0.0.1:8080

# 检查防火墙
sudo ufw status | grep 8080
```

### 问题 2: 端口被占用
```bash
# 查看占用端口的进程
sudo lsof -i :8080

# 杀死进程
sudo kill -9 <PID>

# 或使用其他端口
python3 round19/web_dashboard.py 9000
```

### 问题 3: 网络不通
```bash
# 测试网络连通性
ping <本机 IP>

# 测试端口连通性
telnet <本机 IP> 8080
# 或
nc -zv <本机 IP> 8080
```

---

## 📝 总结

1. **启动服务**: `python3 round19/web_dashboard.py 8080`
2. **开放防火墙**: `sudo ufw allow 8080/tcp`
3. **获取 IP**: `hostname -I | awk '{print $1}'`
4. **远程访问**: `http://<本机 IP>:8080`

完成！隔壁机器可以访问了！🎉
