# Agent Security Skill Scanner - 发布流程与规范

> **版本**: v2.0.1-beta  
> **创建日期**: 2026-03-14  
> **维护者**: Security Team

---

## 📋 发布前检查清单

### 代码准备
- [ ] 所有测试通过
- [ ] 代码审查完成
- [ ] CHANGELOG.md 更新
- [ ] 版本号更新 (所有配置文件)
- [ ] README.md 更新

### 文档准备
- [ ] README.md 中英文完整
- [ ] API 文档更新
- [ ] 使用示例验证
- [ ] 已知问题记录

### 配置文件
- [ ] clawhub.yaml 版本号
- [ ] setup.py 版本号 (PyPI)
- [ ] package.json 版本号 (npm)
- [ ] Git 标签准备

---

## 🚀 发布流程

### 阶段 1: 代码托管平台 (必做)

#### 1.1 GitHub (国际)
```bash
# 1. 创建版本标签
git tag v2.0.1-beta
git push origin v2.0.1-beta

# 2. 创建 Release
gh release create v2.0.1-beta \
  --title "v2.0.1-beta" \
  --notes "Release notes" \
  --draft=false
```

**链接**: https://github.com/caidongyun/agent-security-skill-scanner  
**状态**: ✅ 已完成

#### 1.2 Gitee (中国)
```bash
# 推送标签
git push origin v2.0.1-beta

# 网页创建 Release
# 访问：https://gitee.com/caidongyun/agent-security-skill-scanner/releases
```

**链接**: https://gitee.com/caidongyun/agent-security-skill-scanner  
**状态**: ✅ 已完成

---

### 阶段 2: 包管理平台 (推荐)

#### 2.1 PyPI (Python 包)
**工作量**: 1 小时  
**优先级**: ⭐⭐⭐

**准备工作**:
```bash
# 1. 安装工具
pip install setuptools wheel twine

# 2. 注册 PyPI 账号
# 访问：https://pypi.org/account/register/

# 3. 创建 .pypirc 配置文件
cat > ~/.pypirc << EOF
[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJ...
EOF
```

**创建 setup.py**:
```python
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agent-security-scanner",
    version="2.0.1-beta",
    author="Security Team",
    description="AI Agent Skill Security Scanner - Beta",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/caidongyun/agent-security-skill-scanner",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "agent-security-scanner=cli:main",
        ],
    },
)
```

**发布命令**:
```bash
# 1. 构建
python setup.py sdist bdist_wheel

# 2. 发布到 TestPyPI (测试)
twine upload --repository testpypi dist/*

# 3. 发布到 PyPI (正式)
twine upload dist/*

# 4. 验证安装
pip install agent-security-scanner
```

**维护**:
- 更新版本号 → 重新构建 → twine upload
- 查看统计：https://pypistats.org/packages/agent-security-scanner

---

#### 2.2 npm 规则库 (前端开发者)
**工作量**: 30 分钟  
**优先级**: ⭐⭐⭐

**准备工作**:
```bash
# 1. 创建发布目录
mkdir -p npm-rules
cp detection_rules.json public.json README.md LICENSE npm-rules/

# 2. 注册 npm 账号
# 访问：https://www.npmjs.com/signup
```

**创建 package.json**:
```json
{
  "name": "agent-security-rules",
  "version": "2.0.1-beta",
  "description": "AI Agent Security Detection Rules - Beta Version",
  "main": "detection_rules.json",
  "files": [
    "detection_rules.json",
    "public.json",
    "README.md",
    "LICENSE"
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
    "malware",
    "ai-security",
    "beta"
  ],
  "author": "Security Team",
  "license": "MIT",
  "bugs": {
    "url": "https://github.com/caidongyun/agent-security-skill-scanner/issues"
  },
  "homepage": "https://github.com/caidongyun/agent-security-skill-scanner#readme"
}
```

**发布命令**:
```bash
cd npm-rules

# 1. 登录
npm login

# 2. 发布
npm publish --access public

# 3. 验证
npm view agent-security-rules
npm install agent-security-rules
```

**维护**:
- 更新版本号 → npm version → npm publish
- 查看统计：https://www.npmjs.com/package/agent-security-rules

---

### 阶段 3: AI/ML 平台 (推荐)

#### 3.1 Hugging Face
**工作量**: 1 小时  
**优先级**: ⭐⭐⭐

**发布命令**:
```bash
# 1. 安装工具
pip install huggingface_hub

# 2. 登录
huggingface-cli login

# 3. 创建仓库
huggingface-cli repo create agent-security-scanner

# 4. 上传文件
huggingface-cli upload caidongyun/agent-security-scanner ./

# 5. 创建 README.md (包含模型卡片)
```

**链接**: https://huggingface.co/caidongyun/agent-security-scanner

---

#### 3.2 ModelScope (魔搭)
**工作量**: 1 小时  
**优先级**: ⭐⭐

**发布步骤**:
1. 注册：https://modelscope.cn
2. 创建模型/数据集
3. 上传文件
4. 填写说明文档

**链接**: https://modelscope.cn

---

### 阶段 4: Skill 市场 (必做)

#### 4.1 ClawHub / OpenClaw Market
**工作量**: 已完成配置  
**优先级**: ⭐⭐⭐

**发布命令**:
```bash
cd ~/.openclaw/workspace/skills/agent-security-skill-scanner

# 登录
clawhub auth login

# 发布
clawhub publish . --no-input

# 验证
clawhub inspect agent-security-skill-scanner
```

**状态**: ⏳ 等待 API 限流解除

---

## 📝 版本规范

### 版本号格式
```
主版本。次版本。修订版本-预发布标识
例如：2.0.1-beta
```

### 预发布标识
- `-beta` - 公开测试版 (推荐对外使用)
- `-rc1` - 候选版本 1
- `-alpha` - 内部测试版

### 版本更新流程
```bash
# 1. 更新版本号 (所有配置文件)
# clawhub.yaml, setup.py, package.json

# 2. 提交更改
git add .
git commit -m "v2.0.2-beta: 新功能描述"

# 3. 创建标签
git tag v2.0.2-beta
git push origin v2.0.2-beta

# 4. 发布到各平台
# 参考上方各平台发布命令
```

---

## 🔧 自动化发布脚本

创建 `scripts/publish.sh`:
```bash
#!/bin/bash
set -e

VERSION="2.0.1-beta"

echo "🚀 发布 v$VERSION 到全平台..."

# 1. Git 标签
git tag v$VERSION
git push origin v$VERSION

# 2. GitHub Releases
gh release create v$VERSION --title "v$VERSION" --notes "Release v$VERSION"

# 3. PyPI
python setup.py sdist bdist_wheel
twine upload dist/*

# 4. npm 规则库
cd npm-rules
npm version $VERSION
npm publish
cd ..

# 5. Hugging Face
huggingface-cli upload caidongyun/agent-security-scanner ./

# 6. ClawHub
clawhub publish . --no-input

echo "✅ 发布完成！"
echo "📊 查看统计:"
echo "  - GitHub: https://github.com/caidongyun/agent-security-skill-scanner/releases"
echo "  - PyPI: https://pypi.org/project/agent-security-scanner/"
echo "  - npm: https://www.npmjs.com/package/agent-security-rules"
echo "  - HuggingFace: https://huggingface.co/caidongyun/agent-security-scanner"
```

---

## 📊 发布后验证

### 功能验证
```bash
# PyPI 安装测试
pip install agent-security-scanner
agent-security-scanner --version

# npm 安装测试
npm install agent-security-rules
node -e "console.log(require('agent-security-rules'))"

# ClawHub 安装测试
clawhub install agent-security-skill-scanner
```

### 文档验证
- [ ] 所有链接有效
- [ ] 安装说明准确
- [ ] 使用示例可运行
- [ ] API 文档完整

---

## ⚠️ 注意事项

### 1. Beta 版本说明
**所有对外文档必须标注**:
- README.md 标题
- 包描述
- 发布说明
- 文档首页

**示例**:
```markdown
# Agent Security Skill Scanner (Beta)

> ⚠️ **Beta Version**: 此版本为公开测试版，可能存在未知问题。
```

### 2. 敏感信息
**禁止包含**:
- API Keys
- Token
- 密码
- 个人邮箱
- 内部服务器地址

### 3. 版本同步
所有平台保持相同版本号，避免混淆。

### 4. 更新频率
- Beta 阶段：每 1-2 周
- 稳定阶段：每月或按需

---

## 📈 统计与监控

### 各平台统计链接

| 平台 | 统计链接 |
|------|---------|
| **GitHub** | Insights → Traffic |
| **Gitee** | 统计 → 访问统计 |
| **PyPI** | https://pypistats.org/packages/agent-security-scanner |
| **npm** | https://www.npmjs.com/package/agent-security-rules?activeTab=versions |
| **Hugging Face** | 仓库页面 → Downloads |
| **ClawHub** | 后台管理面板 |

### 月度报告模板
```markdown
## 月度发布报告 (YYYY-MM)

### 新版本
- v2.x.x-beta (发布日期)

### 下载统计
- GitHub: xxx 次
- PyPI: xxx 次
- npm: xxx 次
- 总计：xxx 次

### 问题反馈
- Issues: x 个
- 已解决：x 个

### 下月计划
- ...
```

---

## 🔗 相关链接

| 资源 | 链接 |
|------|------|
| **GitHub** | https://github.com/caidongyun/agent-security-skill-scanner |
| **Gitee** | https://gitee.com/caidongyun/agent-security-skill-scanner |
| **PyPI** | https://pypi.org/project/agent-security-scanner/ |
| **npm** | https://www.npmjs.com/package/agent-security-rules |
| **Hugging Face** | https://huggingface.co/caidongyun/agent-security-scanner |
| **ClawHub** | https://clawhub.com |

---

*最后更新：2026-03-14 | 版本：v2.0.1-beta*
