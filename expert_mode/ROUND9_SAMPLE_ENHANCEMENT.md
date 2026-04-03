# 🔬 Round 9 - 测试样本能力增强

**日期**: 2026-03-20  
**目标**: 丰富测试样本技能，增加威胁类型覆盖，添加白样本生成，完善标签系统

---

## ✅ 完成内容

### 1. 增强样本生成器

**文件**: `enhanced_sample_generator.py`

#### 支持的威胁类型 (10 类恶意 +3 类白样本)

| # | 威胁类型 | 代码 | 严重程度 | 样本数 |
|---|----------|------|----------|--------|
| 1 | 工具投毒 | `tool_poisoning` | HIGH | 1 |
| 2 | 远程加载 | `remote_load` | CRITICAL | 1 |
| 3 | 数据窃取 | `data_exfil` | CRITICAL | 1 |
| 4 | 提示词注入 | `prompt_injection` | HIGH | 1 |
| 5 | 资源耗尽 | `resource_exhaustion` | MEDIUM | 1 |
| 6 | 记忆污染 | `memory_pollution` | MEDIUM | 1 |
| 7 | 供应链攻击 | `supply_chain` | CRITICAL | 1 |
| 8 | 凭证窃取 | `credential_theft` | CRITICAL | 1 |
| 9 | 持久化 | `persistence` | HIGH | 1 |
| 10 | 绕过检测 | `evasion` | HIGH | 1 |
| **-** | **恶意样本合计** | **-** | **-** | **10** |

| # | 白样本类型 | 代码 | 用途 | 样本数 |
|---|------------|------|------|--------|
| 1 | 正常脚本 | `normal_script` | 测试漏报率 | 1 |
| 2 | 常见模式 | `common_pattern` | 测试误报率 | 1 |
| 3 | 易误报模式 | `false_prone` | 优化规则 | 1 |
| **-** | **白样本合计** | **-** | **-** | **3** |

---

### 2. 完善标签系统

**文件**: `SAMPLE_LABEL_SYSTEM.md`

#### 6 维度标签体系

| 维度 | 字段 | 示例值 |
|------|------|--------|
| **攻击类型** | `attack_type` | `tool_poisoning`, `remote_load` |
| **严重程度** | `severity` | `critical`, `high`, `medium`, `none` |
| **编程语言** | `language` | `Python`, `JavaScript`, `Shell` |
| **行为特征** | `behaviors` | `file_execution`, `network_request` |
| **检测指标** | `indicators` | `curl \| bash`, `child_process.exec` |
| **置信度** | `confidence` | `0.95`, `0.88`, `1.0` |
| **关键词标签** | `tags` | `npm`, `ssh`, `benign` |

#### 样本 ID 规范

```
{类型}-{攻击类型简写}-{时间戳}
- MAL-TOO-a3f2b1 (恶意 - 工具投毒)
- BEN-NOR-c4d5e6 (白样本 - 正常脚本)
```

---

### 3. 样本元数据格式

每个样本包含完整元数据 (`metadata.json`):

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
  "name": "恶意 NPM 包 - postinstall 脚本",
  "description": "伪装成正常 npm 包，在 postinstall 阶段执行恶意代码",
  "test_cases": ["TP-F01", "TP-A01", "TP-B01"],
  "status": "ready"
}
```

---

### 4. 样本目录结构

```
samples/
├── samples_index.json          # 总索引 (13 个样本)
├── malicious/                   # 恶意样本目录
│   ├── MAL-TOO-*/              # 工具投毒
│   ├── MAL-RLO-*/              # 远程加载
│   ├── MAL-DEX-*/              # 数据窃取
│   ├── MAL-PIN-*/              # 提示词注入
│   ├── MAL-REX-*/              # 资源耗尽
│   ├── MAL-MPO-*/              # 记忆污染
│   ├── MAL-SUP-*/              # 供应链攻击
│   ├── MAL-CRT-*/              # 凭证窃取
│   ├── MAL-PER-*/              # 持久化
│   └── MAL-EVA-*/              # 绕过检测
└── benign/                      # 白样本目录
    ├── BEN-NOR-*/              # 正常脚本
    ├── BEN-COP-*/              # 常见模式
    └── BEN-FAP-*/              # 易误报模式
```

---

## 📊 生成结果

```
总样本数：13
恶意样本：10
白样本：3

威胁类型分布:
  credential_theft: 1
  data_exfil: 1
  evasion: 1
  false_prone: 1
  memory_pollution: 1
  normal_script: 1
  common_pattern: 1
  persistence: 1
  prompt_injection: 1
  remote_load: 1
  resource_exhaustion: 1
  supply_chain: 1
  tool_poisoning: 1
```

---

## 🎯 样本示例

### 恶意样本示例

#### 1. 工具投毒 (MAL-TOO-*)
- **文件**: `package.json` + `postinstall.js`
- **行为**: postinstall 钩子执行恶意代码
- **检测指标**: `child_process.exec`, `curl | bash`
- **测试用例**: TP-F01, TP-A01, TP-B01

#### 2. 远程加载 (MAL-RLO-*)
- **文件**: `install.sh`
- **行为**: curl 下载远程脚本并执行
- **检测指标**: `curl -fsSL ... | bash`
- **测试用例**: RL-F01, RL-A01, RL-B01

#### 3. 数据窃取 (MAL-DEX-*)
- **文件**: `exfil.py`
- **行为**: 窃取 SSH 密钥并外传
- **检测指标**: `~/.ssh/id_rsa`, `base64`, `requests.post`
- **测试用例**: DE-F01, DE-A01, DE-B01

### 白样本示例

#### 1. 正常脚本 (BEN-NOR-*)
- **文件**: `process_data.py`
- **行为**: CSV 转 JSON (合法数据处理)
- **用途**: 测试检测规则不误报正常脚本

#### 2. 常见模式 (BEN-COP-*)
- **文件**: `sysinfo.py`
- **行为**: 使用 subprocess 收集系统信息
- **用途**: 测试不误报合法系统交互

#### 3. 易误报模式 (BEN-FAP-*)
- **文件**: `encode_data.py`
- **行为**: Base64 编码/解码工具
- **用途**: 优化规则区分合法编码与恶意混淆

---

## 🔧 使用方法

### 生成样本

```bash
cd ~/.openclaw/workspace/skills/agent-security-skill-scanner/expert_mode

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

# 白样本 (用于误报测试)
benign = [s for s in index['samples'] 
          if s['severity'] == 'none']
```

---

## 📈 下一步计划 (Round 10)

### 1. 样本扩展
- [ ] 每类威胁类型增加到 3-5 个变体样本
- [ ] 增加更多白样本场景 (10+ 个)
- [ ] 支持多语言样本 (Go, Rust, PowerShell)

### 2. 自动化测试
- [ ] 样本 - 规则自动匹配测试
- [ ] 检测率/误报率自动统计
- [ ] CI/CD集成

### 3. 样本质量
- [ ] 样本行为验证 (沙箱执行)
- [ ] 检测规则有效性验证
- [ ] 误报根因分析

### 4. 知识库集成
- [ ] 样本 - 规则 - 攻击技术 (MITRE ATT&CK) 映射
- [ ] 威胁情报关联
- [ ] 检测规则推荐

---

## 📁 文件清单

| 文件 | 用途 | 状态 |
|------|------|------|
| `enhanced_sample_generator.py` | 增强样本生成器 | ✅ 完成 |
| `SAMPLE_LABEL_SYSTEM.md` | 标签系统文档 | ✅ 完成 |
| `ROUND9_SAMPLE_ENHANCEMENT.md` | 本报告 | ✅ 完成 |
| `samples/samples_index.json` | 样本总索引 | ✅ 生成 |
| `samples/malicious/*/` | 10 个恶意样本 | ✅ 生成 |
| `samples/benign/*/` | 3 个白样本 | ✅ 生成 |

---

## 🎉 成果总结

- ✅ **10 类威胁类型**样本生成能力
- ✅ **3 类白样本**生成能力 (误报测试)
- ✅ **6 维度标签系统** (攻击类型/严重程度/行为/指标/置信度/标签)
- ✅ **样本 ID 规范化** (MAL-*/BEN-* 格式)
- ✅ **完整元数据** (metadata.json)
- ✅ **统一索引** (samples_index.json)

**总样本数**: 13 (10 恶意 +3 白样本)  
**覆盖威胁类型**: 10 类  
**标签维度**: 6 个  
**检测规则关联**: 支持 test_cases 字段

---

**位置**: `~/.openclaw/workspace/skills/agent-security-skill-scanner/expert_mode/`  
**下一轮**: Round 10 - 样本扩展与自动化测试
