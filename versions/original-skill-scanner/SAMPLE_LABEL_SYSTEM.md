# 🏷️ 样本标签系统 - Sample Label System

## 概述

标签系统为每个测试样本提供多维度元数据标注，支持:
- 快速分类与检索
- 检测规则匹配
- 误报分析
- 覆盖率统计

---

## 标签维度

### 1. 攻击类型 (attack_type)

| 类型 | 代码 | 描述 | 示例 |
|------|------|------|------|
| **工具投毒** | `tool_poisoning` | 恶意 npm/pip 包 | postinstall 脚本 |
| **远程加载** | `remote_load` | 远程代码执行 | curl\|bash |
| **数据窃取** | `data_exfil` | 敏感数据外泄 | SSH 密钥窃取 |
| **提示词注入** | `prompt_injection` | LLM 指令覆盖 | jailbreak 攻击 |
| **资源耗尽** | `resource_exhaustion` | DoS 攻击 | CPU/内存耗尽 |
| **记忆污染** | `memory_pollution` | 上下文投毒 | 虚假信息注入 |
| **供应链攻击** | `supply_chain` | 依赖投毒 | typosquatting |
| **凭证窃取** | `credential_theft` | 密码捕获 | 钓鱼认证 |
| **持久化** | `persistence` | 后门驻留 | cron/crc 修改 |
| **绕过检测** | `evasion` | 混淆反检测 | Base64 混淆 |

### 白样本类型

| 类型 | 代码 | 描述 | 用途 |
|------|------|------|------|
| **正常脚本** | `normal_script` | 合法数据处理 | 测试漏报率 |
| **常见模式** | `common_pattern` | 系统交互 | 测试误报率 |
| **易误报模式** | `false_prone` | 疑似行为 | 优化检测规则 |

---

### 2. 严重程度 (severity)

| 级别 | 代码 | 描述 | 响应 |
|------|------|------|------|
| **严重** | `critical` | 数据泄露/RCE | 立即阻断 |
| **高** | `high` | 凭证窃取/持久化 | 告警 + 调查 |
| **中** | `medium` | 资源耗尽 | 告警 |
| **低** | `low` | 可疑行为 | 记录日志 |
| **无** | `none` | 白样本 | 放行 |

---

### 3. 行为特征 (behaviors)

| 行为 | 描述 | 检测指标 |
|------|------|----------|
| `file_execution` | 文件执行 | exec, eval, system |
| `network_request` | 网络请求 | curl, wget, requests |
| `data_exfiltration` | 数据外泄 | 外部 POST, base64 |
| `file_access` | 文件访问 | 敏感路径读取 |
| `subprocess_execution` | 子进程执行 | subprocess, child_process |
| `infinite_loop` | 无限循环 | while True |
| `obfuscation` | 代码混淆 | base64, eval |
| `dynamic_import` | 动态导入 | __import__, importlib |
| `password_capture` | 密码捕获 | getpass, input |
| `startup_persistence` | 启动持久化 | .bashrc, cron |

---

### 4. 检测指标 (indicators)

| 指标类型 | 示例 | 规则类型 |
|----------|------|----------|
| **命令模式** | `curl | bash`, `wget | bash` | Runtime |
| **文件路径** | `~/.ssh/id_rsa`, `/etc/passwd` | DLP |
| **函数调用** | `child_process.exec`, `subprocess.run` | Runtime |
| **字符串模式** | `ignore previous instructions` | DLP |
| **编码特征** | `base64.b64decode`, `atob` | YARA |
| **网络 IOC** | `evil.com`, `http://` | IOC |
| **包名** | `lodahs`, `reqeusts` | Sigma |

---

### 5. 置信度 (confidence)

| 范围 | 描述 | 处理 |
|------|------|------|
| `0.95-1.0` | 高置信度 | 自动阻断 |
| `0.85-0.94` | 中置信度 | 告警 + 人工审核 |
| `0.70-0.84` | 低置信度 | 记录日志 |
| `<0.70` | 疑似 | 忽略 |

---

### 6. 标签 (tags)

用于快速分类和检索的关键词:

| 标签 | 描述 |
|------|------|
| `npm`, `pip` | 包管理器 |
| `nodejs`, `python`, `shell` | 编程语言 |
| `ssh`, `credential` | 目标类型 |
| `install_hook`, `typosquatting` | 攻击手法 |
| `benign`, `false_positive` | 白样本标记 |

---

## 样本 ID 格式

```
{类型}-{攻击类型简写}-{时间戳}
```

- **恶意样本**: `MAL-TPA-a3f2b1` (MAL-TOO-a3f2b1)
- **白样本**: `BEN-NOR-c4d5e6` (BEN-NORMAL-c4d5e6)

示例:
- `MAL-TOO-a3f2b1` - 工具投毒恶意样本
- `MAL-RLO-b4c3d2` - 远程加载恶意样本
- `BEN-NOR-c4d5e6` - 正常脚本白样本
- `BEN-FAL-d5e6f7` - 易误报白样本

---

## 样本目录结构

```
samples/
├── samples_index.json          # 总索引
├── malicious/                   # 恶意样本
│   ├── MAL-TOO-a3f2b1/
│   │   ├── metadata.json       # 样本元数据 (标签)
│   │   ├── package.json        # 样本文件
│   │   └── postinstall.js
│   └── ...
└── benign/                      # 白样本
    ├── BEN-NOR-c4d5e6/
    │   ├── metadata.json
    │   └── process_data.py
    └── ...
```

---

## 元数据格式 (metadata.json)

```json
{
  "sample_id": "MAL-TOO-a3f2b1",
  "attack_type": "tool_poisoning",
  "severity": "high",
  "language": "JavaScript",
  "behaviors": ["file_execution", "network_request", "data_exfiltration"],
  "indicators": ["postinstall script", "child_process.exec", "curl | bash"],
  "confidence": 0.95,
  "tags": ["npm", "nodejs", "install_hook"],
  "created_at": "2026-03-20T21:00:00",
  "name": "恶意 NPM 包 - postinstall 脚本",
  "description": "伪装成正常 npm 包，在 postinstall 阶段执行恶意代码",
  "files": {
    "package.json": "...",
    "postinstall.js": "..."
  },
  "test_cases": ["TP-F01", "TP-A01", "TP-B01"],
  "detection_rules": [],
  "status": "ready"
}
```

---

## 使用方法

### 生成样本

```bash
# 生成所有样本
python3 enhanced_sample_generator.py --all --summary

# 只生成恶意样本
python3 enhanced_sample_generator.py --malicious --summary

# 只生成白样本
python3 enhanced_sample_generator.py --benign --summary

# 指定输出目录
python3 enhanced_sample_generator.py --all -o custom_samples
```

### 查询样本

```python
import json

with open('samples/samples_index.json') as f:
    index = json.load(f)

# 按攻击类型过滤
tool_poisoning = [s for s in index['samples'] 
                  if s['attack_type'] == 'tool_poisoning']

# 按严重程度过滤
critical = [s for s in index['samples'] 
            if s['severity'] == 'critical']

# 白样本
benign = [s for s in index['samples'] 
          if s['severity'] == 'none']
```

---

## 覆盖率统计

### 威胁类型覆盖

| 类型 | 样本数 | 规则数 | 检测率 |
|------|--------|--------|--------|
| tool_poisoning | 1 | 3 | - |
| remote_load | 1 | 3 | - |
| data_exfil | 1 | 3 | - |
| prompt_injection | 1 | 2 | - |
| resource_exhaustion | 1 | 2 | - |
| memory_pollution | 1 | 2 | - |
| supply_chain | 1 | 2 | - |
| credential_theft | 1 | 3 | - |
| persistence | 1 | 3 | - |
| evasion | 1 | 2 | - |
| **恶意样本合计** | **10** | **25** | - |

### 白样本覆盖

| 类型 | 样本数 | 用途 |
|------|--------|------|
| normal_script | 1 | 测试漏报率 |
| common_pattern | 1 | 测试误报率 |
| false_prone | 1 | 优化规则 |
| **白样本合计** | **3** | - |

---

## 与检测规则关联

每个样本的 `test_cases` 字段关联对应的检测规则:

```json
{
  "sample_id": "MAL-TOO-a3f2b1",
  "test_cases": ["TP-F01", "TP-A01", "TP-B01"]
}
```

规则文件命名:
- `rule_tool_poisoning_functional.json` (TP-F*)
- `rule_tool_poisoning_anomaly.json` (TP-A*)
- `rule_tool_poisoning_behavior.json` (TP-B*)

---

## 更新记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-03-20 | v2.0 | 新增 10 威胁类型 +3 白样本类型 |
| 2026-03-20 | v2.0 | 完善标签系统 (6 维度) |
| 2026-03-20 | v2.0 | 样本 ID 规范化 |

---

**位置**: `~/.openclaw/workspace/skills/agent-security-skill-scanner/expert_mode/`
