# NPM 发布方案

> **版本**: v2.0.1  
> **分析日期**: 2026-03-14  
> **状态**: 方案评估

---

## 📊 可行性分析

### ✅ 可以发布到 npm

**原因**:
1. Node.js 已安装 (v22.22.0)
2. npm 已安装 (10.9.4)
3. 项目包含 JavaScript/CLI 组件
4. 可以创建 npm 包包装器

### 📦 发布内容

| 内容 | 说明 | 优先级 |
|------|------|--------|
| **CLI 工具** | `agent-security-scanner` 命令行工具 | ⭐⭐⭐ |
| **规则库** | `detection-rules` 检测规则包 | ⭐⭐⭐ |
| **文档包** | `agent-security-docs` 文档和配置 | ⭐⭐ |
| **Python 包** | 通过 PyPI 发布 (更合适) | ⭐⭐⭐ |

---

## 🚀 方案对比

### 方案 1: 发布 CLI 工具到 npm (推荐)

**包名**: `agent-security-scanner`

**优势**:
- ✅ 全球开发者可访问
- ✅ 易于安装 (`npm install -g agent-security-scanner`)
- ✅ 自动版本管理
- ✅ 与 ClawHub 互补

**劣势**:
- ⚠️ 需要创建 Node.js 包装器
- ⚠️ Python 核心功能需要额外配置

**工作量**: 2-3 小时

---

### 方案 2: 发布规则库到 npm

**包名**: `agent-security-rules`

**内容**:
```json
{
  "malware-detection": {...},
  "permission-abuse": {...},
  "data-leakage": {...}
}
```

**优势**:
- ✅ 纯 JSON 文件，易于发布
- ✅ 可被其他项目复用
- ✅ 独立于编程语言

**劣势**:
- ⚠️ 需要定期同步更新

**工作量**: 30 分钟

---

### 方案 3: 发布 Python 包到 PyPI (最推荐)

**包名**: `agent-security-scanner`

**优势**:
- ✅ Python 原生支持
- ✅ 无需包装器
- ✅ 直接调用核心功能
- ✅ 符合项目技术栈

**劣势**:
- ⚠️ 需要配置 setup.py
- ⚠️ PyPI 账号注册

**工作量**: 1 小时

---

### 方案 4: 多平台发布 (完整方案)

| 平台 | 包名 | 用途 |
|------|------|------|
| **npm** | `agent-security-scanner` | CLI 工具 + 规则库 |
| **PyPI** | `agent-security-scanner` | Python 核心库 |
| **ClawHub** | `agent-security-skill-scanner` | OpenClaw Skill |
| **GitHub Releases** | v2.0.1.tar.gz | 完整发布包 |

**优势**:
- ✅ 覆盖所有用户群体
- ✅ 最大化可访问性
- ✅ 多语言支持

**工作量**: 4-6 小时

---

## 📋 推荐方案：多平台发布

### 第一阶段：PyPI (1 小时)

```bash
# 1. 创建 setup.py
# 2. 注册 PyPI 账号
# 3. 发布
python setup.py sdist bdist_wheel
twine upload dist/*
```

### 第二阶段：npm 规则库 (30 分钟)

```bash
# 1. 创建 package.json
# 2. 只包含规则文件
npm publish
```

### 第三阶段：npm CLI 工具 (2-3 小时)

```bash
# 1. 创建 Node.js 包装器
# 2. 调用 Python 核心
# 3. 发布
npm publish
```

---

## 🔧 实施步骤

### 1. PyPI 发布配置

创建 `setup.py`:

```python
from setuptools import setup, find_packages

setup(
    name='agent-security-scanner',
    version='2.0.1',
    description='AI Agent Skill Security Scanner',
    author='Security Team',
    packages=find_packages(),
    install_requires=[],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'agent-security-scanner=cli:main',
        ],
    },
)
```

创建 `.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-xxxxxxxxxxxx
```

发布:

```bash
pip install setuptools wheel twine
python setup.py sdist bdist_wheel
twine upload dist/*
```

---

### 2. npm 规则库配置

创建 `package.json`:

```json
{
  "name": "agent-security-rules",
  "version": "2.0.1",
  "description": "AI Agent Security Detection Rules",
  "main": "detection_rules.json",
  "files": [
    "detection_rules.json",
    "public.json"
  ],
  "repository": {
    "type": "git",
    "url": "https://github.com/caidongyun/agent-security-skill-scanner"
  },
  "keywords": [
    "security",
    "agent",
    "rules",
    "detection",
    "malware"
  ],
  "author": "Security Team",
  "license": "MIT"
}
```

发布:

```bash
npm login
npm publish
```

---

### 3. npm CLI 工具配置

创建 `cli.js`:

```javascript
#!/usr/bin/env node

const { execSync } = require('child_process');
const path = require('path');

const pythonScript = path.join(__dirname, 'python', 'cli.py');

try {
  execSync(`python3 ${pythonScript} ${process.argv.slice(2).join(' ')}`, {
    stdio: 'inherit'
  });
} catch (error) {
  process.exit(error.status);
}
```

创建 `package.json`:

```json
{
  "name": "agent-security-scanner",
  "version": "2.0.1",
  "description": "AI Agent Skill Security Scanner CLI",
  "bin": {
    "agent-security-scanner": "./cli.js"
  },
  "files": [
    "cli.js",
    "python/"
  ],
  "scripts": {
    "postinstall": "python3 -m pip install -r python/requirements.txt"
  },
  "repository": {
    "type": "git",
    "url": "https://github.com/caidongyun/agent-security-skill-scanner"
  },
  "keywords": [
    "security",
    "agent",
    "scanner",
    "malware-detection",
    "cli"
  ],
  "author": "Security Team",
  "license": "MIT"
}
```

---

## 📊 平台对比

| 平台 | 用户群体 | 安装方式 | 优势 |
|------|---------|---------|------|
| **PyPI** | Python 开发者 | `pip install` | 原生支持，直接调用 |
| **npm** | Node.js/前端开发者 | `npm install` | 用户基数大，易传播 |
| **ClawHub** | OpenClaw 用户 | `clawhub install` | 平台集成，自动更新 |
| **GitHub** | 所有开发者 | Download/Clone | 源代码，完整控制 |

---

## 🎯 推荐发布顺序

1. **PyPI** (1 小时) - Python 核心
2. **npm 规则库** (30 分钟) - 纯 JSON
3. **npm CLI** (2-3 小时) - Node.js 包装器
4. **ClawHub** (等待 API 限流) - OpenClaw Skill
5. **GitHub Releases** (已完成) - 完整包

---

## ⚠️ 注意事项

### 1. 版本同步

所有平台保持相同版本号：
```
v2.0.1 (所有平台)
```

### 2. 更新流程

```bash
# 1. 更新代码
git commit -m "v2.0.2: 新功能"

# 2. 更新标签
git tag v2.0.2
git push origin v2.0.2

# 3. 发布到各平台
# PyPI
python setup.py sdist bdist_wheel
twine upload dist/*

# npm
npm version 2.0.2
npm publish

# ClawHub
clawhub publish . --no-input

# GitHub Releases
gh release create v2.0.2
```

### 3. 敏感信息

**不要包含**:
- API Keys
- Token
- 密码
- 个人邮箱

---

## 📈 预期效果

| 平台 | 预计下载量/月 | 覆盖用户 |
|------|-------------|---------|
| **PyPI** | 100-500 | Python 开发者 |
| **npm** | 500-2000 | Node.js/前端开发者 |
| **ClawHub** | 50-200 | OpenClaw 用户 |
| **GitHub** | 100-300 | 所有开发者 |

**总计**: 750-3000 次/月

---

## 🔗 相关资源

| 资源 | 链接 |
|------|------|
| PyPI | https://pypi.org |
| npm | https://npmjs.com |
| PyPI 发布指南 | https://packaging.python.org |
| npm 发布指南 | https://docs.npmjs.com |

---

*创建日期：2026-03-14*
*版本：v2.0.1*
