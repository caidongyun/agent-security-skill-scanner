# 缺失数据下载清单

**日期**: 2026-04-14  
**目的**: 补充 Scanner 所需的规则和工具

---

## 📦 缺失的工具/数据

### 1. Gitleaks (敏感信息扫描器)

**状态**: ❌ 未安装  
**用途**: 密钥、密码、Token 检测  
**下载地址**: https://github.com/gitleaks/gitleaks/releases

**安装命令**:
```bash
# Ubuntu/Debian
sudo apt-get install gitleaks

# 或从 GitHub 下载
wget https://github.com/gitleaks/gitleaks/releases/download/v8.18.3/gitleaks_8.18.3_linux_x64.tar.gz
tar -xzf gitleaks_8.18.3_linux_x64.tar.gz
sudo mv gitleaks /usr/local/bin/

# 验证
gitleaks version
```

**可获取数据**:
- ✅ 敏感信息检测规则 (正则)
- ✅ 密钥格式库 (AWS, GitHub, Slack 等)
- ✅ Git 历史扫描能力

---

### 2. tree-sitter (AST 解析器)

**状态**: ❌ 未安装  
**用途**: AST 语法树解析  
**下载地址**: https://github.com/tree-sitter/tree-sitter

**安装命令**:
```bash
# Python 绑定
pip install tree-sitter

# 或从源码编译
git clone https://github.com/tree-sitter/tree-sitter
cd tree-sitter
python setup.py install
```

**可获取数据**:
- ✅ Python AST 解析
- ✅ JavaScript AST 解析
- ✅ Go AST 解析
- ✅ 多语言支持架构

---

### 3. Semgrep 规则库

**状态**: ❌ 未下载  
**用途**: 学习规则 DSL 和 AST 检测  
**下载地址**: https://github.com/returntocorp/semgrep-rules

**下载命令**:
```bash
git clone https://github.com/returntocorp/semgrep-rules.git ~/Desktop/security-benchmark/external-rules/semgrep-rules
```

**可获取数据**:
- ✅ 1000+ 公开规则
- ✅ 规则 DSL 示例
- ✅ AST 检测规则
- ✅ AI/LLM 安全规则

**重点规则**:
```
semgrep-rules/python/
  - dangerous-eval.yaml
  - prompt-injection.yaml
  - data-exfiltration.yaml
  
semgrep-rules/javascript/
  - eval-use.yaml
  - xss.yaml
```

---

### 4. Bandit 规则库

**状态**: ❌ 未下载  
**用途**: Python AST 安全规则  
**下载地址**: https://github.com/PyCQA/bandit

**下载命令**:
```bash
git clone https://github.com/PyCQA/bandit.git ~/Desktop/security-benchmark/external-tools/bandit
```

**可获取数据**:
- ✅ 60+ Python 安全规则
- ✅ Plugin 架构示例
- ✅ AST 遍历器实现
- ✅ 测试框架

**重点规则**:
```
bandit/bandit/plugins/
  - eval_used.py (B307)
  - exec_used.py (B308)
  - hardcoded_password_string.py (B105)
  - hardcoded_tmp_directory.py (B108)
```

---

### 5. Gitleaks 规则库

**状态**: ❌ 未下载  
**用途**: 敏感信息检测规则  
**下载地址**: https://github.com/gitleaks/gitleaks/blob/master/config/gitleaks.toml

**下载命令**:
```bash
wget https://raw.githubusercontent.com/gitleaks/gitleaks/master/config/gitleaks.toml -O ~/Desktop/security-benchmark/external-rules/gitleaks.toml
```

**可获取数据**:
- ✅ 50+ 敏感信息检测规则
- ✅ 密钥格式定义
- ✅ 正则规则库

**重点规则**:
```toml
[[rules]]
id = "aws-access-key"
regex = '''AKIA[0-9A-Z]{16}'''

[[rules]]
id = "github-token"
regex = '''gh[pousr]_[A-Za-z0-9_]{36}'''

[[rules]]
id = "slack-token"
regex = '''xox[baprs]-[0-9a-zA-Z]{10,48}'''
```

---

### 6. Trivy 规则库 (可选)

**状态**: ⏳ 安装中  
**用途**: 漏洞数据库、报告格式  
**下载地址**: https://github.com/aquasecurity/trivy

**下载命令**:
```bash
# 已安装的跳过
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
```

**可获取数据**:
- ✅ CVE 漏洞数据库
- ✅ 报告模板
- ✅ 多扫描器编排

---

### 7. AI/LLM 安全规则 (重点)

**状态**: ❌ 未收集  
**用途**: AI Skill 专用规则  
**来源**: 多个开源项目

**下载命令**:
```bash
# OWASP AI Security
git clone https://github.com/OWASP/www-project-top-10-for-llm-applications.git ~/Desktop/security-benchmark/external-rules/owasp-ai-top10

# ML Commons Security
git clone https://github.com/mlcommons/security-guidelines.git ~/Desktop/security-benchmark/external-rules/ml-security

# LLM Security
git clone https://github.com/llm-security/awesome-llm-security.git ~/Desktop/security-benchmark/external-rules/llm-security
```

**可获取数据**:
- ✅ OWASP LLM Top 10 规则
- ✅ Prompt Injection 检测规则
- ✅ Data Poisoning 检测规则
- ✅ Model Theft 检测规则

---

## 📋 下载脚本

### 一键下载所有资源

```bash
#!/bin/bash
# download_all.sh

BASE=~/Desktop/security-benchmark

echo "📦 下载外部工具和规则..."

# 创建目录
mkdir -p $BASE/external-tools
mkdir -p $BASE/external-rules

# 1. Gitleaks
echo "⬇️  Gitleaks..."
wget -q https://github.com/gitleaks/gitleaks/releases/download/v8.18.3/gitleaks_8.18.3_linux_x64.tar.gz -P $BASE/external-tools/
tar -xzf $BASE/external-tools/gitleaks_8.18.3_linux_x64.tar.gz -C $BASE/external-tools/
rm $BASE/external-tools/gitleaks_8.18.3_linux_x64.tar.gz

# 2. tree-sitter
echo "⬇️  tree-sitter..."
pip install tree-sitter -q

# 3. Semgrep 规则
echo "⬇️  Semgrep 规则..."
git clone --depth 1 https://github.com/returntocorp/semgrep-rules.git $BASE/external-rules/semgrep-rules

# 4. Bandit
echo "⬇️  Bandit..."
git clone --depth 1 https://github.com/PyCQA/bandit.git $BASE/external-tools/bandit

# 5. Gitleaks 规则
echo "⬇️  Gitleaks 规则..."
wget -q https://raw.githubusercontent.com/gitleaks/gitleaks/master/config/gitleaks.toml -O $BASE/external-rules/gitleaks.toml

# 6. AI 安全规则
echo "⬇️  AI 安全规则..."
git clone --depth 1 https://github.com/OWASP/www-project-top-10-for-llm-applications.git $BASE/external-rules/owasp-ai-top10

echo "✅ 下载完成!"
echo ""
echo "📁 文件位置:"
echo "  工具：$BASE/external-tools/"
echo "  规则：$BASE/external-rules/"
```

---

## 📊 下载优先级

| 资源 | 大小 | 优先级 | 用途 |
|------|------|--------|------|
| **Gitleaks** | 50MB | ⭐⭐⭐⭐⭐ | 敏感信息检测 |
| **tree-sitter** | 10MB | ⭐⭐⭐⭐⭐ | AST 解析 |
| **Gitleaks 规则** | 50KB | ⭐⭐⭐⭐⭐ | 密钥检测规则 |
| **Bandit** | 20MB | ⭐⭐⭐⭐ | Python AST 规则 |
| **Semgrep 规则** | 100MB | ⭐⭐⭐⭐ | 规则 DSL 学习 |
| **AI 安全规则** | 10MB | ⭐⭐⭐⭐⭐ | AI Skill 专用 |
| **Trivy** | 500MB | ⭐⭐ | 漏洞数据库 |

---

## 🎯 下一步行动

### 立即执行 (P0)
```bash
# 1. 安装 Gitleaks
wget https://github.com/gitleaks/gitleaks/releases/download/v8.18.3/gitleaks_8.18.3_linux_x64.tar.gz
tar -xzf gitleaks_8.18.3_linux_x64.tar.gz
sudo mv gitleaks /usr/local/bin/

# 2. 安装 tree-sitter
pip install tree-sitter

# 3. 下载 Gitleaks 规则
wget https://raw.githubusercontent.com/gitleaks/gitleaks/master/config/gitleaks.toml -O ~/Desktop/security-benchmark/external-rules/gitleaks.toml

# 4. 下载 AI 安全规则
git clone https://github.com/OWASP/www-project-top-10-for-llm-applications.git ~/Desktop/security-benchmark/external-rules/owasp-ai-top10
```

### 短期执行 (P1)
```bash
# 5. 下载 Bandit
git clone https://github.com/PyCQA/bandit.git ~/Desktop/security-benchmark/external-tools/bandit

# 6. 下载 Semgrep 规则
git clone https://github.com/returntocorp/semgrep-rules.git ~/Desktop/security-benchmark/external-rules/semgrep-rules
```

---

## 📁 下载后的文件结构

```
~/Desktop/security-benchmark/
├── external-tools/
│   ├── gitleaks/           # Gitleaks 二进制
│   ├── bandit/             # Bandit 源码
│   └── tree-sitter/        # tree-sitter Python 绑定
├── external-rules/
│   ├── gitleaks.toml       # Gitleaks 规则
│   ├── semgrep-rules/      # Semgrep 规则库
│   └── owasp-ai-top10/     # AI 安全规则
└── samples/                # 现有样本
```

---

*缺失数据下载清单*
*最后更新：2026-04-14*
