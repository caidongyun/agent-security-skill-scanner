# OpenClaw 用户指南 - 规则迭代与加白

> **版本**: v2.0.1-beta  
> **适用场景**: OpenClaw + Agent Security Skill Scanner  
> **创建日期**: 2026-03-14

---

## 📋 目录

1. [快速开始](#1-快速开始)
2. [规则迭代](#2-规则迭代)
3. [添加白名单](#3-添加白名单)
4. [常见问题](#4-常见问题)
5. [最佳实践](#5-最佳实践)

---

## 1. 快速开始

### 1.1 安装

```bash
# OpenClaw 用户
clawhub install agent-security-skill-scanner

# 或手动安装
git clone https://gitee.com/caidongyun/agent-security-skill-scanner.git
cd agent-security-skill-scanner
./install.sh
```

### 1.2 基础使用

```bash
# 扫描单个技能
python cli.py scan skills/my-skill/

# 批量扫描
python cli.py scan-all skills/

# 查看帮助
python cli.py --help
```

### 1.3 输出示例

```
======================================================================
Agent Security Skill Scanner - Report
======================================================================

Skill: skills/my-skill/
----------------------------------------------------------------------

🦠 Malware Detection:
  [HIGH] EVAL_USAGE
    main.py:42
    → 建议：使用 ast.literal_eval 替代

======================================================================
Overall Assessment:
======================================================================
  Risk Score: 65/100
  Risk Level: HIGH
  Verdict: REVIEW
======================================================================
```

---

## 2. 规则迭代

### 2.1 规则文件位置

```
agent-security-skill-scanner/
├── detection_rules.json    # 主规则文件
├── rules/
│   ├── malware.json        # 恶意代码规则
│   ├── backdoor.json       # 后门检测规则
│   └── ...
```

### 2.2 添加自定义规则

**步骤 1**: 编辑 `detection_rules.json`

```json
{
  "version": "2.0.1",
  "updated": "2026-03-14",
  "total_rules": 111,
  "categories": [
    {
      "id": "custom",
      "name": "自定义规则",
      "weight": 20,
      "rules": [
        {
          "id": "CUSTOM-001",
          "name": "检测我的自定义模式",
          "severity": "HIGH",
          "patterns": [
            "my_custom_pattern\\s*\\([^)]+\\)"
          ],
          "description": "检测特定的自定义代码模式",
          "recommendation": "建议使用替代方案 XYZ"
        }
      ]
    }
  ]
}
```

**步骤 2**: 验证规则

```bash
# 测试规则
python cli.py scan skills/test-skill/ --rules detection_rules.json

# 查看规则统计
python -c "import json; d=json.load(open('detection_rules.json')); print(f'总规则数：{d[\"total_rules\"]}')"
```

**步骤 3**: 提交规则 (可选)

```bash
# 提交到项目
git add detection_rules.json
git commit -m "feat: 添加自定义规则 CUSTOM-001"
git push origin master
```

### 2.3 规则语法

#### 正则表达式模式

```json
{
  "id": "EXAMPLE-001",
  "name": "示例规则",
  "severity": "HIGH",
  "patterns": [
    "\\beval\\s*\\([^)]+\\)",    // 匹配 eval() 调用
    "requests\\.post\\s*\\(",    // 匹配 requests.post()
    "os\\.environ\\[.*PASSWORD"  // 匹配密码环境变量
  ],
  "whitelist": [
    "eval\\s*\\(\\s*['\"]1\\+1['\"]"  // 白名单：安全的 eval 使用
  ]
}
```

#### 严重性级别

| 级别 | 说明 | 处置建议 |
|------|------|---------|
| **CRITICAL** | 严重风险 | 立即拒绝 |
| **HIGH** | 高风险 | 人工审查 |
| **MEDIUM** | 中等风险 | 标记观察 |
| **LOW** | 低风险 | 记录日志 |

### 2.4 规则测试

**创建测试样本**:

```bash
# 创建测试技能目录
mkdir -p tests/samples/test-custom

# 创建测试文件
cat > tests/samples/test-custom/test.py << EOF
# 测试自定义规则
eval(user_input)  # 应该被检测
EOF

# 运行测试
python cli.py scan tests/samples/test-custom/
```

**预期输出**:

```
[HIGH] CUSTOM-001: 检测我的自定义模式
  test.py:2
```

---

## 3. 添加白名单

### 3.1 白名单文件位置

```
agent-security-skill-scanner/
├── data/
│   └── whitelist/
│       ├── local.json      # 本地白名单 (用户自定义)
│       ├── public.json     # 公共白名单 (官方维护)
│       └── patterns.json   # 模式白名单
```

### 3.2 添加本地白名单

**步骤 1**: 编辑 `data/whitelist/local.json`

```json
{
  "version": "1.0.0",
  "updated": "2026-03-14",
  "files": [
    "tests/samples/safe-skill/main.py",
    "vendor/trusted-lib/utils.py"
  ],
  "patterns": [
    {
      "rule_id": "MALWARE-001",
      "pattern": "eval\\s*\\(\\s*['\"]test['\"]\\s*\\)",
      "reason": "测试用例中的安全 eval 使用"
    }
  ],
  "hashes": [
    {
      "file": "trusted-lib.py",
      "sha256": "abc123...",
      "reason": "可信第三方库"
    }
  ]
}
```

**步骤 2**: 验证白名单

```bash
# 扫描已加白的技能
python cli.py scan tests/samples/safe-skill/

# 预期输出：无警告
✅ No issues found
```

### 3.3 加白方式

#### 方式 1: 文件加白

```json
{
  "files": [
    "skills/trusted-skill/",
    "vendor/official-lib/",
    "tests/samples/benign/"
  ]
}
```

**适用场景**: 完全可信的目录或文件

---

#### 方式 2: 模式加白

```json
{
  "patterns": [
    {
      "rule_id": "MALWARE-001",
      "pattern": "eval\\s*\\(\\s*['\"]1\\+1['\"]\\s*\\)",
      "reason": "教学示例中的安全用法"
    },
    {
      "rule_id": "CRED-001",
      "pattern": "API_KEY\\s*=\\s*['\"]test['\"]",
      "reason": "测试用的假 API Key"
    }
  ]
}
```

**适用场景**: 特定代码模式需要豁免

---

#### 方式 3: 哈希加白

```json
{
  "hashes": [
    {
      "file": "requests-2.28.0.py",
      "sha256": "abc123def456...",
      "reason": "官方发布的 requests 库"
    }
  ]
}
```

**适用场景**: 已知安全的第三方库

---

### 3.4 OpenClaw 集成

#### 在 OpenClaw 中使用白名单

**步骤 1**: 配置 `clawhub.yaml`

```yaml
name: my-secure-skill
version: 1.0.0

# 安全扫描配置
security:
  scanner: agent-security-skill-scanner
  whitelist:
    - data/whitelist/local.json
  rules:
    - detection_rules.json
```

**步骤 2**: 在 Skill 中引用

```python
# skills/my-skill/cli.py
from agent_security_scanner import scan_skill

def before_publish():
    """发布前安全检查"""
    result = scan_skill('.')
    if result['overall']['verdict'] == 'REJECT':
        raise Exception("安全检查未通过")
    return True
```

---

## 4. 常见问题

### Q1: 误报太多怎么办？

**解决方案**:

1. **添加白名单**
   ```bash
   # 编辑本地白名单
   vim data/whitelist/local.json
   
   # 添加误报文件
   {
     "files": ["path/to/false-positive.py"]
   }
   ```

2. **调整规则**
   ```json
   {
     "id": "MALWARE-001",
     "patterns": ["更精确的正则"],
     "whitelist": ["添加例外模式"]
   }
   ```

3. **降低严重性**
   ```json
   {
     "id": "EXAMPLE-001",
     "severity": "MEDIUM"  // HIGH → MEDIUM
   }
   ```

---

### Q2: 如何更新规则库？

**方案 1: 自动更新**

```bash
# 启用自动更新 (在配置文件中)
{
  "auto_update": true,
  "update_interval": "7d"  // 每 7 天更新
}
```

**方案 2: 手动更新**

```bash
# 拉取最新规则
git pull origin master

# 或下载规则文件
curl -O https://gitee.com/caidongyun/agent-security-skill-scanner/raw/master/detection_rules.json
```

---

### Q3: 如何分享我的规则？

**步骤**:

1. **Fork 项目**
   ```bash
   git clone https://gitee.com/caidongyun/agent-security-skill-scanner.git
   ```

2. **添加规则**
   ```bash
   # 编辑 detection_rules.json
   # 添加你的自定义规则
   ```

3. **提交 PR**
   ```bash
   git add detection_rules.json
   git commit -m "feat: 添加新规则 XXX-001"
   git push origin feature/new-rule
   # 在 Gitee/GitHub 创建 Pull Request
   ```

---

### Q4: 如何禁用某些规则？

**方案 1: 临时禁用**

```bash
# 扫描时排除特定规则
python cli.py scan skills/my-skill/ --exclude-rules MALWARE-001,CRED-001
```

**方案 2: 配置文件禁用**

```json
// config.json
{
  "disabled_rules": [
    "MALWARE-001",
    "CRED-001"
  ]
}
```

---

## 5. 最佳实践

### 5.1 规则迭代流程

```
1. 发现新威胁
   ↓
2. 编写检测规则
   ↓
3. 创建测试样本
   ↓
4. 验证规则有效性
   ↓
5. 添加到规则库
   ↓
6. 更新版本号
   ↓
7. 提交/分享
```

### 5.2 白名单管理

| 类型 | 更新频率 | 维护者 | 审核 |
|------|---------|--------|------|
| **本地白名单** | 按需 | 用户自己 | 无需审核 |
| **公共白名单** | 每周 | 官方团队 | 需要审核 |
| **哈希白名单** | 每日 | 自动同步 | 自动验证 |

### 5.3 版本控制

```bash
# 规则版本格式
{
  "version": "2.0.1",  // 主版本。次版本。修订版本
  "updated": "2026-03-14"
}

# 更新规则时
git tag rules-v2.0.2
git push origin rules-v2.0.2
```

### 5.4 CI/CD 集成

```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Scanner
        run: pip install agent-security-scanner
      
      - name: Run Scan
        run: agent-security-scanner scan ./skills/
      
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: security-report
          path: report.json
```

---

## 📚 相关资源

| 资源 | 链接 |
|------|------|
| **Gitee 仓库** | https://gitee.com/caidongyun/agent-security-skill-scanner |
| **GitHub 仓库** | https://github.com/caidongyun/agent-security-skill-scanner |
| **规则文档** | docs/detection_rules.json |
| **白名单示例** | data/whitelist/local.json |
| **问题反馈** | Issues 页面 |

---

*最后更新：2026-03-14 | 版本：v2.0.1-beta*
