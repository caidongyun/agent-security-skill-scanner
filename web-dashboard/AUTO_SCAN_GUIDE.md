# Scanner V3 - 自动化扫描与数据同步指南

## 📋 问题说明

之前 Web 仪表板显示的是**静态数据**，需要运行实际扫描才能生成**真实数据**。

---

## 🚀 快速开始

### 1️⃣ 运行自动化扫描

```bash
cd ~/.openclaw/workspace/agent-security-skill-scanner-V3/web-dashboard
python3 auto_scan.py
```

**功能**:
- 扫描 `samples/high_fidelity/` 目录
- 检测恶意样本
- 生成真实统计数据
- 自动更新仪表板数据

---

### 2️⃣ 查看仪表板

访问：http://192.168.0.103:8080

现在显示的是**真实扫描数据**！

---

## 📁 文件说明

| 文件 | 功能 |
|------|------|
| `auto_scan.py` | 自动化扫描脚本 |
| `server_v2.py` | Web 服务（优化版） |
| `test_dashboard.py` | 自动化测试套件 |
| `dashboard_data.json` | 数据文件（由扫描生成） |

---

## 🔄 数据同步流程

```
运行扫描 → 检测样本 → 生成数据 → 更新 JSON → 仪表板显示
```

### 手动同步

```bash
python3 auto_scan.py
```

### 自动同步（可选）

添加到 crontab（每小时同步一次）：

```bash
0 * * * * python3 /home/cdy/.openclaw/workspace/agent-security-skill-scanner-V3/web-dashboard/auto_scan.py
```

---

## 📊 仪表板数据

扫描后生成的数据包括：

| 指标 | 说明 |
|------|------|
| **总样本** | 实际扫描的样本数量 |
| **检测率** | 检出的恶意样本比例 |
| **P99 延迟** | 检测性能指标 |
| **恶意样本** | 被标记为恶意的数量 |
| **更新时间** | 最后扫描时间 |

---

## 🧪 运行测试

```bash
cd ~/.openclaw/workspace/agent-security-skill-scanner-V3/web-dashboard
python3 test_dashboard.py
```

测试项目：
- ✅ 服务状态
- ✅ HTML 内容
- ✅ 响应时间
- ✅ 并发请求
- ✅ 稳定性

---

## 🔧 故障排查

### 仪表板不显示数据

1. 检查服务是否运行：
   ```bash
   ps aux | grep server_v2
   ```

2. 检查数据文件：
   ```bash
   cat web-dashboard/dashboard_data.json
   ```

3. 重新运行扫描：
   ```bash
   python3 auto_scan.py
   ```

4. 重启服务：
   ```bash
   kill $(cat /tmp/web-dashboard.pid)
   python3 server_v2.py &
   ```

---

## 📝 示例输出

```
============================================================
🚀 自动化扫描 + 数据同步
============================================================

🔍 运行快速扫描测试...
   找到 353 个样本
   检测完成：353/353
   耗时：0.15s

📊 生成仪表板数据...

💾 保存数据...
✅ 数据已保存到 dashboard_data.json

============================================================
✅ 完成！
============================================================

📈 扫描结果:
   总样本：353
   检测率：100.0%
   P99 延迟：0.43ms

🌐 访问仪表板：http://localhost:8080
============================================================
```

---

**现在访问** http://192.168.0.103:8080 **查看真实数据！** 🎉
