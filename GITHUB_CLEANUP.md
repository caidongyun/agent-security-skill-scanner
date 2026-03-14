# GitHub 仓库清理指南

## 问题说明

GitHub 仓库历史中存在大文件 (`release/v2.0.0/full-scan-result.json`, 251MB)，超过了 GitHub 100MB 的限制。

## 解决方案

### 方案 1: 重建 GitHub 仓库 (推荐，5 分钟)

1. **在 GitHub 网页上删除仓库**:
   - 访问：https://github.com/caidongyun/agent-security-skill-scanner/settings
   - 滚动到底部 → "Delete this repository"
   - 输入仓库名确认删除

2. **重新创建空仓库**:
   - 访问：https://github.com/new
   - 仓库名：`agent-security-skill-scanner`
   - 不要初始化 README/.gitignore

3. **从 Gitee 推送**:
   ```bash
   cd ~/.openclaw/workspace/skills/agent-security-skill-scanner
   git remote set-url github https://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@github.com/caidongyun/agent-security-skill-scanner.git
   git push -u github master
   git push github v2.0.1
   git push github v2.0.1-final
   ```

### 方案 2: 使用 BFG Repo-Cleaner (10 分钟)

```bash
# 1. 下载 BFG
wget https://repo.maven.apache.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar

# 2. 清理大文件 (>100MB)
java -jar bfg-1.14.0.jar --delete-files '*.{json}' --no-blob-protection .

# 3. 清理历史
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. 强制推送
git push github master --force
git push github v2.0.1 --force
git push github v2.0.1-final --force
```

### 方案 3: 使用 git-filter-branch (30 分钟)

```bash
# 1. 清理大文件
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch release/v2.0.0/*.json release/v2.0.0/*.txt' \
  --prune-empty --tag-name-filter cat -- --all

# 2. 清理引用
git for-each-ref --format="%(refname)" refs/original/ | xargs -n 1 git update-ref -d

# 3. 清理历史
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. 强制推送
git push github master --force
git push github v2.0.1 --force
git push github v2.0.1-final --force
```

## 预防措施

### 1. 添加 .gitignore

```gitignore
# 大文件
*.json > 50MB
*.log > 10MB
*.tar.gz > 50MB

# 测试文件
tests/samples/
release/v*/full-scan-*
release/v*/*.log

# 缓存
__pycache__/
*.pyc
```

### 2. 使用 Git LFS (可选)

```bash
# 安装 Git LFS
git lfs install

# 跟踪大文件
git lfs track "*.json"
git lfs track "*.log"
```

### 3. 发布流程规范

```bash
# 发布前检查
git diff --cached --numstat | awk '$1 > 1000 {print $3}'

# 发布时只包含必要文件
git add README*.md clawhub.yaml *.py detectors/ reporters/ data/ *.json *.yaml *.sh LICENSE
```

## 当前状态

- ✅ Gitee: 已完成，无大文件问题
- ⏳ GitHub: 等待清理后推送
- ✅ clawhub.yaml: 已配置，包含丰富搜索关键词

## 推荐操作

**立即执行方案 1** (重建 GitHub 仓库)，因为：
1. 最快 (5 分钟)
2. 最彻底 (完全清除历史记录)
3. 最简单 (无需额外工具)

---

*创建日期：2026-03-14*
*版本：v2.0.1*
