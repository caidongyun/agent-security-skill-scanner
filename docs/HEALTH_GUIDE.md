# OpenClaw 健壮性指南 - 故障预防与处理

> **版本**: v1.0  
> **日期**: 2026-03-14  
> **目标**: 简洁实用，预防为主

---

## 📋 故障总览

| 故障类型 | 发生频率 | 影响 | 预防难度 |
|---------|---------|------|---------|
| **大文件问题** | ⭐⭐⭐ 高 | 推送失败 | ⭐ 简单 |
| **内存溢出** | ⭐⭐ 中 | 会话崩溃 | ⭐⭐ 中等 |
| **API 限流** | ⭐⭐ 中 | 功能不可用 | ⭐ 简单 |
| **配置损坏** | ⭐ 低 | 启动失败 | ⭐⭐ 中等 |
| **权限问题** | ⭐ 低 | 操作失败 | ⭐ 简单 |
| **网络超时** | ⭐⭐ 中 | 同步失败 | ⭐⭐ 中等 |

---

## 1️⃣ 大文件问题 (已遇到)

### 症状
```
remote: error: File xxx is 251MB; exceeds 100MB limit
error: 无法推送到 GitHub
```

### 原因
- 测试数据提交到 Git
- 日志文件未清理
- 样本库过大

### 预防方案 ⭐⭐⭐

```bash
# 1. 配置 .gitignore (必须)
cat > .gitignore << EOF
# 大文件
*.json > 50MB
*.log > 10MB
*.tar.gz > 50MB
tests/samples/
release/v*/

# 缓存
__pycache__/
*.pyc
EOF

# 2. 安装 pre-commit (推荐)
pip install pre-commit
pre-commit install

# 3. 定期检查
du -sh .git  # 检查 Git 大小
```

### 处理方案

```bash
# 已提交大文件？清理历史
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch path/to/large-file' \
  --prune-empty --tag-name-filter cat -- --all

git push -f origin master
```

---

## 2️⃣ 内存溢出

### 症状
```
Killed
Out of memory
会话突然终止
```

### 原因
- 会话历史过多
- Memory 文件累积
- 并发任务过多

### 预防方案 ⭐⭐⭐

```bash
# 1. 定期清理会话
find ~/.openclaw/sessions -mtime +7 -delete

# 2. 限制 Memory 大小
find ~/.openclaw/memory -name "*.md" -mtime +30 -delete

# 3. 监控内存
ps aux | grep openclaw | awk '{print $6}'  # 查看内存使用
```

### 处理方案

```bash
# 紧急清理
rm -rf ~/.openclaw/sessions/*
rm -rf ~/.openclaw/memory/*.md
git gc --prune=now  # 清理 Git
```

---

## 3️⃣ API 限流

### 症状
```
403 rate limit exceeded
GitHub API rate limit exceeded
```

### 原因
- 频繁调用 API
- 未认证访问
- 批量操作

### 预防方案 ⭐⭐⭐

```bash
# 1. 使用认证 Token
export GITHUB_TOKEN=ghp_xxx

# 2. 添加请求间隔
sleep 60  # 操作间隔 60 秒

# 3. 批量操作分批
for skill in skills/*/; do
  clawhub publish $skill
  sleep 300  # 5 分钟间隔
done
```

### 处理方案

```bash
# 等待限流解除 (通常 1 小时)
echo "等待 60 分钟后重试"
sleep 3600

# 或使用备用账号
export GITHUB_TOKEN=ghp_another_token
```

---

## 4️⃣ 配置损坏

### 症状
```
Config file corrupted
无法启动 OpenClaw
插件加载失败
```

### 原因
- 意外断电
- 磁盘空间满
- 手动修改错误

### 预防方案 ⭐⭐

```bash
# 1. 定期备份配置
cp -r ~/.openclaw/config ~/.openclaw/config.backup.$(date +%Y%m%d)

# 2. 使用版本控制
cd ~/.openclaw
git init
git add config.yaml
git commit -m "backup config"
```

### 处理方案

```bash
# 恢复备份
cp -r ~/.openclaw/config.backup.20260314 ~/.openclaw/config

# 或重置配置
rm ~/.openclaw/config.yaml
openclaw init  # 重新初始化
```

---

## 5️⃣ 权限问题

### 症状
```
Permission denied
Access denied
Token expired
```

### 原因
- Token 过期
- 文件权限错误
- 账号权限不足

### 预防方案 ⭐⭐

```bash
# 1. 定期检查 Token
clawhub whoami

# 2. 文件权限设置
chmod -R 755 ~/.openclaw/skills/
chmod 600 ~/.openclaw/*.token

# 3. Token 到期提醒
# 在日历中设置 Token 到期提醒 (GitHub Token 90 天)
```

### 处理方案

```bash
# 更新 Token
clawhub auth login

# 修复权限
chmod -R u+rw ~/.openclaw/
```

---

## 6️⃣ 网络超时

### 症状
```
Connection timeout
Request failed
Sync failed
```

### 原因
- 网络不稳定
- 服务器负载高
- 防火墙阻止

### 预防方案 ⭐⭐

```bash
# 1. 使用国内镜像
export GITEE_TOKEN=xxx  # 优先使用 Gitee

# 2. 设置超时
export GIT_TIMEOUT=300

# 3. 重试机制
retry() {
  for i in {1..3}; do
    $@ && return 0 || sleep 10
  done
  return 1
}
```

### 处理方案

```bash
# 切换网络
# 使用 Gitee 替代 GitHub
git remote set-url origin https://gitee.com/...

# 重试操作
retry git push origin master
```

---

## 🛡️ 综合预防方案 (推荐)

### 每日检查 (1 分钟)

```bash
#!/bin/bash
# ~/.openclaw/scripts/daily-check.sh

echo "=== OpenClaw 健康检查 ==="

# 1. 检查磁盘空间
df -h ~/.openclaw | awk 'NR==2 {print "磁盘使用:", $5}'

# 2. 检查 Git 大小
du -sh ~/.openclaw/.git | awk '{print "Git 大小:", $1}'

# 3. 检查内存
ps aux | grep openclaw | awk '{sum+=$6} END {print "内存使用:", sum/1024, "MB"}'

# 4. 检查 Token
clawhub whoami 2>/dev/null && echo "Token: ✅ 有效" || echo "Token: ❌ 过期"

echo "========================"
```

### 每周清理 (5 分钟)

```bash
#!/bin/bash
# ~/.openclaw/scripts/weekly-cleanup.sh

echo "=== 每周清理 ==="

# 1. 清理旧会话
find ~/.openclaw/sessions -mtime +7 -delete
echo "✓ 清理 7 天前的会话"

# 2. 清理旧日志
find ~/.openclaw/logs -mtime +7 -delete
echo "✓ 清理 7 天前的日志"

# 3. Git 清理
cd ~/.openclaw
git gc --prune=now
echo "✓ Git 垃圾回收"

# 4. 检查大文件
find . -size +50M -not -path "./.git/*" | head -5
echo "✓ 检查大文件"

echo "=================="
```

### 每月审计 (15 分钟)

```bash
#!/bin/bash
# ~/.openclaw/scripts/monthly-audit.sh

echo "=== 每月审计 ==="

# 1. 备份配置
cp -r ~/.openclaw/config ~/.openclaw/config.backup.$(date +%Y%m)
echo "✓ 备份配置"

# 2. 检查更新
openclaw status
echo "✓ 检查更新"

# 3. 安全扫描
python cli.py scan-all ~/.openclaw/skills/
echo "✓ 安全扫描"

# 4. 生成报告
echo "审计日期: $(date)"
echo "磁盘使用: $(df -h ~/.openclaw | awk 'NR==2 {print $5}')"
echo "Git 大小：$(du -sh ~/.openclaw/.git | awk '{print $1}')"

echo "=================="
```

---

## 📊 监控指标

| 指标 | 健康值 | 警告值 | 危险值 |
|------|--------|--------|--------|
| **磁盘使用** | <50% | 50-80% | >80% |
| **Git 大小** | <500MB | 500MB-1GB | >1GB |
| **内存使用** | <512MB | 512MB-1GB | >1GB |
| **会话数量** | <50 | 50-100 | >100 |
| **Token 有效期** | >30 天 | 7-30 天 | <7 天 |

---

## 🚨 紧急处理流程

```
发现问题
    ↓
查看日志 (~/.openclaw/logs/)
    ↓
搜索错误信息
    ↓
尝试标准解决方案
    ↓
未解决？提交 Issue
    ↓
等待支持
```

---

## 📞 支持渠道

| 渠道 | 适用场景 | 响应时间 |
|------|---------|---------|
| **Issues** | Bug 报告 | 1-3 天 |
| **Discussions** | 问题咨询 | 1-2 天 |
| **Email** | 紧急问题 | 24 小时 |
| **文档** | 自助查询 | 即时 |

---

## ✅ 最佳实践总结

### 必须做 ⭐⭐⭐
1. 配置 .gitignore
2. 安装 pre-commit
3. 定期清理会话
4. 备份配置文件

### 推荐做 ⭐⭐
1. 每周运行清理脚本
2. 监控磁盘/内存
3. Token 到期提醒

### 可选做 ⭐
1. 每月审计
2. 安全扫描
3. 性能优化

---

*最后更新：2026-03-14 | 版本：v1.0*
