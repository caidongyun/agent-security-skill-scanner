# 推送保护指南 - Push Protection Guide

> **目的**: 避免大文件和敏感信息推送到 GitHub  
> **适用范围**: 所有贡献者  
> **最后更新**: 2026-03-14

---

## ⚠️ 禁止推送的内容

### 1. 大文件 (>100MB)

```bash
# ❌ 禁止推送
*.json > 50MB
*.log > 10MB
*.tar.gz > 50MB
release/v*/full-scan-*
release/v*/*.log
tests/samples/ (大规模样本库)
```

### 2. 敏感信息

```bash
# ❌ 禁止推送
*.env (环境变量)
*.key (私钥文件)
*.pem (证书文件)
*token* (Token)
*password* (密码)
*secret* (密钥)
*credential* (凭据)
```

### 3. 临时文件

```bash
# ❌ 禁止推送
__pycache__/
*.pyc
*.log
*.tmp
*.bak
```

---

## ✅ 推送前检查清单

### 1. 检查大文件

```bash
# 检查暂存区大文件
git diff --cached --numstat | awk '$1 > 1000 {print "⚠️ 大文件:", $3}'

# 检查历史大文件
git log --all --pretty=format: --name-only | sort -u | xargs -I {} git ls-files -s {} | awk '$2 > 50000 {print "⚠️ 历史大文件:", $4}'
```

### 2. 检查敏感信息

```bash
# 扫描敏感关键词
git diff --cached | grep -iE "(token|password|secret|credential|api_key)" && echo "⚠️ 发现敏感信息!"

# 使用 git-secrets (推荐安装)
git secrets --scan
```

### 3. 检查 .gitignore

```bash
# 确保 .gitignore 包含所有应忽略的文件
cat .gitignore
```

---

## 🛡️ 预防措施

### 1. 使用 .gitignore

```gitignore
# 大文件
*.json > 50MB
*.log
*.tar.gz
release/v*/full-scan-*
tests/samples/

# 敏感文件
*.env
*.key
*.pem
*token*
*password*
*secret*

# 临时文件
__pycache__/
*.pyc
*.tmp
*.bak

# IDE
.vscode/
.idea/
*.swp
*.swo
```

### 2. 使用 Git LFS (可选)

```bash
# 安装 Git LFS
git lfs install

# 跟踪大文件 (如果必须版本控制)
git lfs track "*.json"
git lfs track "*.log"
```

### 3. 使用 Pre-commit Hook

创建 `.git/hooks/pre-commit`:

```bash
#!/bin/bash

# 检查大文件
large_files=$(git diff --cached --numstat | awk '$1 > 1000 {print $3}')
if [ -n "$large_files" ]; then
    echo "❌ 错误：发现大文件 (>1000 行)"
    echo "$large_files"
    exit 1
fi

# 检查敏感信息
if git diff --cached | grep -qiE "(token|password|secret|api_key)"; then
    echo "❌ 错误：发现敏感信息"
    exit 1
fi

echo "✅ 推送检查通过"
exit 0
```

---

## 🚨 问题处理流程

### 发现大文件/敏感信息已推送

1. **立即删除敏感信息** (如果在 GitHub)
   - 访问 GitHub 仓库 Settings → Security
   - 删除泄露的 Token

2. **清理 Git 历史**
   ```bash
   # 清理特定文件
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch <file-path>' \
     --prune-empty --tag-name-filter cat -- --all
   
   # 清理引用
   git for-each-ref --format="%(refname)" refs/original/ | xargs -n 1 git update-ref -d
   
   # 清理历史
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   
   # 强制推送
   git push -f origin master
   ```

3. **通知团队成员**
   - 如果有敏感信息泄露，立即通知团队
   - 更新所有相关凭据

---

## 📋 发布流程规范

### 发布前检查

```bash
# 1. 检查暂存区
git status

# 2. 只添加必要文件
git add README*.md clawhub.yaml *.py detectors/ reporters/ data/ *.json *.yaml *.sh LICENSE

# 3. 再次检查
git status

# 4. 提交
git commit -m "vx.x.x: 发布说明"

# 5. 推送前最后检查
git log -1 --stat

# 6. 推送
git push origin master
git push origin vx.x.x
```

### ClawHub 发布

```bash
# 确保 clawhub.yaml 配置正确
cat clawhub.yaml

# 发布
clawhub publish . --no-input
```

---

## 🔧 自动化检查 (推荐)

### GitHub Actions 配置

创建 `.github/workflows/check-secrets.yml`:

```yaml
name: Check Secrets

on: [push, pull_request]

jobs:
  check-secrets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Check for secrets
        run: |
          if git diff HEAD~1 | grep -qiE "(token|password|secret|api_key)"; then
            echo "❌ 发现敏感信息!"
            exit 1
          fi
      
      - name: Check file sizes
        run: |
          large_files=$(find . -type f -size +50M)
          if [ -n "$large_files" ]; then
            echo "❌ 发现大文件 (>50MB):"
            echo "$large_files"
            exit 1
          fi
```

---

## 📞 联系方式

如遇到问题，请：
1. 查看本指南
2. 提交 Issue: https://github.com/caidongyun/agent-security-skill-scanner/issues
3. 联系维护者

---

*最后更新：2026-03-14 | 版本：v2.0.1*
