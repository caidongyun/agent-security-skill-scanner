# 快速指南 - 规则迭代与误报处理

> **版本**: v2.0.1-beta  
> **场景**: OpenClaw + LLM  
> **日期**: 2026-03-14

---

## 1️⃣ 规则迭代流程 (7 步)

### 步骤 1: 发现新威胁
```bash
# 扫描发现未知威胁
python cli.py scan skills/suspicious-skill/
```

### 步骤 2: LLM 分析威胁
```python
# 使用 OpenClaw LLM 分析
from openclaw import llm

threat = llm.analyze("""
分析这段代码的安全威胁:
- 代码内容：{code}
- 扫描结果：{scan_result}
- 威胁类型：?
- 风险等级：?
""")
```

### 步骤 3: LLM 生成规则
```python
# 让 LLM 生成检测规则
rule = llm.generate_rule("""
根据以下威胁特征生成检测规则:
- 威胁类型：{threat_type}
- 代码特征：{code_pattern}
- 严重性：{severity}

输出 JSON 格式的规则配置。
""")
```

### 步骤 4: 创建测试样本
```bash
# 创建测试文件
mkdir -p tests/samples/new-threat
cat > tests/samples/new-threat/test.py << EOF
# 测试新规则
{suspicious_code}
EOF
```

### 步骤 5: 验证规则
```bash
# 测试规则有效性
python cli.py scan tests/samples/new-threat/ --rules detection_rules.json

# 预期：检测到威胁
[HIGH] NEW-001: 新威胁检测
```

### 步骤 6: 添加到规则库
```bash
# 编辑规则文件
vim detection_rules.json

# 添加新规则
{
  "id": "NEW-001",
  "name": "新威胁检测",
  "severity": "HIGH",
  "patterns": ["{pattern}"]
}

# 更新版本号
"version": "2.0.2"
```

### 步骤 7: 提交分享
```bash
# 提交到 Git
git add detection_rules.json
git commit -m "feat: 添加新规则 NEW-001"
git push origin master

# 或分享到 ClawHub
clawhub publish . --no-input
```

---

## 2️⃣ 误报处理指南

### 场景：扫描发现误报

```
[HIGH] EVAL_USAGE
  main.py:42
  → eval(user_input)
```

### 解决方案 (3 选 1)

#### 方案 1: 文件加白 (最简单 ⭐)

```bash
# 编辑白名单文件
vim data/whitelist/local.json

# 添加误报文件
{
  "files": [
    "skills/my-skill/main.py"
  ]
}

# 重新扫描
python cli.py scan skills/my-skill/
# ✅ 无警告
```

---

#### 方案 2: 模式加白 (精确控制)

```bash
# 编辑白名单文件
vim data/whitelist/local.json

# 添加误报模式
{
  "patterns": [
    {
      "rule_id": "MALWARE-001",
      "pattern": "eval\\s*\\(\\s*['\"]test['\"]\\s*\\)",
      "reason": "测试用例中的安全 eval 使用"
    }
  ]
}

# 重新扫描
python cli.py scan skills/my-skill/
# ✅ 该模式不再警告
```

---

#### 方案 3: LLM 辅助加白 (推荐 ⭐⭐⭐)

```python
# 使用 OpenClaw LLM 分析误报
from openclaw import llm

whitelist = llm.generate("""
分析以下扫描结果是否为误报:
- 规则：{rule_id}
- 代码：{code_snippet}
- 文件：{file_path}

如果是误报，生成白名单配置 (JSON 格式)。
如果不是误报，说明真实风险。
""")

# 输出示例
{
  "is_false_positive": true,
  "whitelist_entry": {
    "rule_id": "MALWARE-001",
    "pattern": "eval\\s*\\(\\s*['\"]safe['\"]\\s*\\)",
    "reason": "安全的测试用例"
  }
}
```

---

## 📋 快速参考

### 白名单文件位置

```
data/whitelist/local.json  # 本地白名单 (用户自定义)
```

### 白名单格式

```json
{
  "files": ["path/to/safe/file.py"],
  "patterns": [
    {
      "rule_id": "MALWARE-001",
      "pattern": "safe_pattern",
      "reason": "说明原因"
    }
  ],
  "hashes": [
    {
      "file": "trusted-lib.py",
      "sha256": "abc123...",
      "reason": "可信库"
    }
  ]
}
```

### 验证加白

```bash
# 扫描已加白的文件
python cli.py scan path/to/whitelisted/

# 预期输出
✅ No issues found
```

---

## 🔗 相关文档

| 文档 | 说明 |
|------|------|
| [USER_GUIDE.md](USER_GUIDE.md) | 完整用户指南 |
| [detection_rules.json](../detection_rules.json) | 规则文件 |
| [local.json](../data/whitelist/local.json) | 白名单文件 |

---

*最后更新：2026-03-14 | 版本：v2.0.1-beta*
