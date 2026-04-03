rule Agent_Credential_Theft {
    meta:
        description = "检测凭证窃取"
        attack_type = "credential_theft"
    strings:
        $ssh = /id_rsa|id_ed25519|\.ssh\//
        $aws = /AWS_ACCESS_KEY|AWS_SECRET/
        $exfil = /(attacker|evil|collect|exfil)/ nocase
    condition:
        ($ssh or $aws) and $exfil
}

rule Agent_Curl_Remote_Exec {
    meta:
        description = "检测 curl 管道 bash 执行"
        attack_type = "remote_load"
        mitre_id = "ATLAS-T0005"
    strings:
        $curl = /curl\s+.*\|\s*(bash|sh)/
        $http = /https?:\/\/[^\s"']+/
    condition:
        $curl and $http
}

rule Agent_Data_Exfil {
    meta:
        description = "检测数据外传"
        attack_type = "data_exfiltration"
    strings:
        $sensitive = /(id_rsa|password|secret|token)/ nocase
        $c2 = /(attacker|evil|collect|exfil)/ nocase
        $post = /(curl.*POST|requests\.post)/ nocase
    condition:
        $sensitive and $c2 and $post
}

rule Agent_Data_Exfiltration {
    meta:
        description = "检测数据外传行为"
        attack_type = "data_exfiltration"
        mitre_id = "ATLAS-T0003"
    strings:
        $ssh = /id_rsa|\.ssh\/|private.*key/
        $http = /https?:\/\/[^\s"']+\/collect/
        $curl = /curl.*-X.*POST|requests\.post/
    condition:
        ($ssh or $http) and $curl
}

rule Agent_Memory_Pollution {
    meta:
        description = "检测记忆污染"
        attack_type = "memory_pollution"
    strings:
        $memory = /memory\.json|memdb\.json|context\.json/
        $inject = /(inject|poison|pollute|false)/ nocase
    condition:
        $memory and $inject
}

rule Agent_Persistence {
    meta:
        description = "检测持久化"
        attack_type = "persistence"
    strings:
        $systemd = /\.service|systemd|systemctl/
        $cron = /crontab|cron\.d|@reboot/
        $evil = /(evil|malicious|attacker)/ nocase
    condition:
        ($systemd or $cron) and $evil
}

rule Agent_Persistence_Systemd {
    meta:
        description = "检测 systemd 持久化"
        attack_type = "persistence"
        mitre_id = "ATLAS-T0009"
    strings:
        $systemd = /systemd|\.service|WantedBy=multi-user/
        $cron = /crontab|@reboot|cron\.d/
    condition:
        $systemd or $cron
}

rule Agent_Resource_Exhaustion {
    meta:
        description = "检测资源耗尽"
        attack_type = "resource_exhaustion"
    strings:
        $fork = /os\.fork\(\)/
        $infinite = /while\s+True:|while\s+\(1\):/
    condition:
        $fork and $infinite
}

rule Agent_SupplyChain {
    meta:
        description = "检测供应链攻击"
        attack_type = "supply_chain_attack"
    strings:
        $postinstall = /postinstall.*:/
        $curl_bash = /curl.*\|.*bash/ nocase
    condition:
        $postinstall and $curl_bash
}

rule Agent_SupplyChain_PostInstall {
    meta:
        description = "检测 NPM postinstall 恶意脚本"
        attack_type = "supply_chain_attack"
        mitre_id = "ATLAS-T0007"
    strings:
        $postinstall = /postinstall|preinstall|prepare\.script/
        $exec = /exec\(|child_process/
        $curl = /curl.*\|.*bash/
    condition:
        $postinstall and ($exec or $curl)
}

rule BASH_Base64Decode {
    meta:
        description = "Detects base64 decode execute"
        severity = "high"
        mitre = "T1027.001"
    strings:
        $b1 = "base64 -d"
        $b2 = "base64 --decode"
        $b3 = "| bash"
    condition:
        ($b1 or $b2) and $b3
}

rule BASH_DownloadExecute {
    meta:
        description = "Detects download and execute"
        severity = "critical"
        mitre = "T1059.004"
    strings:
        $d1 = "curl | bash"
        $d2 = "wget | bash"
        $d3 = "curl|sh"
        $d4 = "wget|sh"
    condition:
        $d1 or $d2 or $d3 or $d4
}

rule BASH_EvalInjection {
    meta:
        description = "Detects eval injection"
        severity = "critical"
        mitre = "T1059.004"
    strings:
        $e1 = "eval $"
        $e2 = "eval \""
        $e3 = "exec $"
    condition:
        $e1 or $e2 or $e3
}

rule BASH_ForkBomb {
    meta:
        description = "Detects fork bomb"
        severity = "critical"
        mitre = "T1499.003"
    strings:
        $f1 = ":(){:|:&};:"
        $f2 = "while true; do"
        $f3 = "done &"
    condition:
        $f1 or ($f2 and $f3)
}

rule BASH_ReverseShell_Netcat {
    meta:
        description = "Detects netcat reverse shell"
        severity = "critical"
        mitre = "T1059.004"
    strings:
        $n1 = "nc -e /bin/bash"
        $n2 = "nc -e /bin/sh"
        $n3 = "ncat --execute"
    condition:
        $n1 or $n2 or $n3
}

rule BASH_ReverseShell_TCP {
    meta:
        description = "Detects /dev/tcp reverse shell"
        severity = "critical"
        mitre = "T1059.004"
    strings:
        $t1 = "/dev/tcp/"
        $t2 = "0<&196"
    condition:
        $t1 or $t2
}

rule CRED_BrowserPassword {
    meta:
        description = "Detects browser creds"
        severity = "critical"
        mitre = "T1555.001"
    strings:
        $chrome = "Chrome/Default/Login Data"
        $decrypt = "ProtectedData.Unprotect"
    condition:
        $chrome and $decrypt
}

rule CRED_CloudCred {
    meta:
        description = "Detects cloud creds"
        severity = "critical"
        mitre = "T1552.005"
    strings:
        $aws = "aws/credentials"
        $gcp = "application_default_credentials"
    condition:
        $aws or $gcp
}

rule CRED_ConfigFileParsing {
    meta:
        description = "Detects config parsing"
        severity = "high"
        mitre = "T1552.001"
    strings:
        $env = ".env"
        $conf = "config.ini"
        $token = "token"
    condition:
        ($env or $conf) and $token
}

rule CRED_DatabaseCredential {
    meta:
        description = "Detects DB credentials"
        severity = "critical"
        mitre = "T1003"
    strings:
        $mysql = "mysql://"
        $postgres = "postgres://"
        $mongo = "mongodb://"
        $pass = "DB_PASSWORD"
    condition:
        $mysql or $postgres or $mongo or $pass
}

rule CRED_EnvVarTheft {
    meta:
        description = "Detects env var theft"
        severity = "critical"
        mitre = "T1552.001"
    strings:
        $aws = "AWS_SECRET"
        $azure = "AZURE_"
        $proc = "process.env"
        $osenv = "os.environ"
    condition:
        ($proc or $osenv) and ($aws or $azure)
}

rule CRED_MemoryDump {
    meta:
        description = "Detects memory dump"
        severity = "critical"
        mitre = "T1003"
    strings:
        $dump = "MiniDumpWriteDump"
        $lsass = "lsass"
    condition:
        $dump or $lsass
}

rule CRED_NetrcFile {
    meta:
        description = "Detects .netrc access"
        severity = "high"
        mitre = "T1552.001"
    strings:
        $n1 = ".netrc"
        $n2 = "password"
    condition:
        $n1 and $n2
}

rule CRED_RegistryCred {
    meta:
        description = "Detects registry creds"
        severity = "critical"
        mitre = "T1555.001"
    strings:
        $sam = "HKLM\\SAM"
        $pass = "DefaultPassword"
    condition:
        $sam or $pass
}

rule CRED_SSHKeyAccess {
    meta:
        description = "Detects SSH key access"
        severity = "critical"
        mitre = "T1552.004"
    strings:
        $ssh1 = ".ssh/id_rsa"
        $ssh2 = ".ssh/authorized_keys"
    condition:
        $ssh1 or $ssh2
}

rule CRED_ShadowFileAccess {
    meta:
        description = "Detects /etc/shadow access"
        severity = "critical"
        mitre = "T1003"
    strings:
        $s1 = "/etc/shadow"
        $s2 = "cat /etc/shadow"
    condition:
        $s1 or $s2
}

rule JS_Cloud_AWSMetadata {
    meta:
        description = "Detects AWS metadata access"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1552.005"
    strings:
        $aws1 = "http://169.254.169.254/latest/meta-data"
        $aws2 = "169.254.169.254"
        $aws3 = "aws-sdk"
    condition:
        $aws1 or ($aws2 and $aws3)
}

rule JS_Cloud_DockerSocket {
    meta:
        description = "Detects Docker socket access"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1552.005"
    strings:
        $docker = "/var/run/docker.sock"
        $dockerode = "dockerode"
        $modem = "docker-modem"
    condition:
        $docker or $dockerode or $modem
}

rule JS_CodeExecution_ChildProcess_Exec {
    meta:
        description = "Detects Node.js child_process exec usage"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.007"
    strings:
        $require1 = "require('child_process')"
        $require2 = "require(\"child_process\")"
        $import1 = "import { exec } from 'child_process'"
        $import2 = "import { exec } from \"child_process\""
    condition:
        $require1 or $require2 or $import1 or $import2
}

rule JS_CodeExecution_ExecMethods {
    meta:
        description = "Detects child_process exec method calls"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.007"
    strings:
        $exec = ".exec("
        $execSync = ".execSync("
        $spawn = ".spawn("
        $spawnSync = ".spawnSync("
        $fork = ".fork("
    condition:
        $exec or $execSync or $spawn or $spawnSync or $fork
}

rule JS_CodeExecution_ShellCommand {
    meta:
        description = "Detects shell command execution patterns in JavaScript"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.007"
    strings:
        $shell1 = "\"/bin/sh\""
        $shell2 = "\"/bin/bash\""
        $shell3 = "'/bin/sh'"
        $shell4 = "'/bin/bash'"
        $shell5 = "\"cmd.exe\""
        $shell6 = "'cmd.exe'"
        $shell7 = "\"powershell\""
        $shell8 = "'powershell'"
        $shell_true = "shell:\\s*true"
        $shell_true2 = "shell: true"
        $exec = "exec("
        $spawn = "spawn("
        $child_process = "child_process"
    condition:
        ($shell1 or $shell2 or $shell3 or $shell4 or $shell5 or $shell6 or $shell7 or $shell8) and ($exec or $spawn or $child_process)
        or $shell_true or $shell_true2
}

rule JS_CodeInjection_Constructor {
    meta:
        description = "Detects constructor-based code injection"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1059.007"
    strings:
        $constructor = ".constructor("
        $prototype = ".prototype"
        $apply = ".apply("
        $call = ".call("
    condition:
        $constructor or $prototype or $apply or $call
}

rule JS_CodeInjection_Eval {
    meta:
        description = "Detects JavaScript eval injection"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.007"
    strings:
        $eval = "eval("
        $function = "new Function("
        $function2 = "Function("
        $vm = "vm.runInContext("
        $vm2 = "vm.runInNewContext("
        $vm3 = "vm.runInThisContext("
    condition:
        $eval or $function or $function2 or $vm or $vm2 or $vm3
}

rule JS_CommandInjection_TemplateLiteral {
    meta:
        description = "Detects command injection via template literal"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.007"
    strings:
        $template = "`"
        $dollar = "$"
        $exec = "exec("
        $spawn = "spawn("
    condition:
        $template and $dollar and ($exec or $spawn)
}

rule JS_CommandInjection_UserInput {
    meta:
        description = "Detects command injection via user input"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.007"
    strings:
        $req = "req.query"
        $req2 = "req.params"
        $req3 = "req.body"
        $exec = "exec("
        $concat = "+"
    condition:
        ($req or $req2 or $req3) and $exec and $concat
}

rule JS_Cred_BrowserData {
    meta:
        description = "Detects browser credential access"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1555.001"
    strings:
        $chrome1 = "AppData/Local/Google/Chrome"
        $chrome2 = "Library/Application Support/Google/Chrome"
        $cookies = "Cookies"
        $localstorage = "Local Storage"
    condition:
        ($chrome1 or $chrome2) and ($cookies or $localstorage)
}

rule JS_Cred_NPMToken {
    meta:
        description = "Detects NPM token theft"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1552.001"
    strings:
        $npmrc = ".npmrc"
        $npmtoken = "//registry.npmjs.org/:_authToken"
        $yarnrc = ".yarnrc"
    condition:
        $npmrc or $npmtoken or $yarnrc
}

rule JS_Cred_PasswordManager {
    meta:
        description = "Detects password manager access"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1555.001"
    strings:
        $keychain = "security find-generic-password"
        $chrome = "Chrome/Default/Login Data"
        $firefox = "Firefox/Profiles/signons.sqlite"
    condition:
        $keychain or $chrome or $firefox
}

rule JS_Deserialization {
    meta:
        description = "Detects unsafe deserialization"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.007"
    strings:
        $unserialize1 = "unserialize("
        $unserialize2 = "JSON.parse("
        $prototype = "__proto__"
    condition:
        $unserialize1 or ($unserialize2 and $prototype)
}

rule JS_Exfil_Clipboard {
    meta:
        description = "Detects clipboard access"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1113"
    strings:
        $clipboard1 = "navigator.clipboard.readText"
        $clipboard2 = "clipboard.readText"
        $clipboard3 = "electron.clipboard"
    condition:
        $clipboard1 or $clipboard2 or $clipboard3
}

rule JS_Exfil_EnvVars {
    meta:
        description = "Detects environment variable theft"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1057"
    strings:
        $process = "process.env"
        $aws = "AWS_SECRET"
        $azure = "AZURE_"
        $gcp = "GOOGLE_"
        $api = "API_KEY"
    condition:
        $process and ($aws or $azure or $gcp or $api)
}

rule JS_Exfil_FileRead {
    meta:
        description = "Detects sensitive file read for exfiltration"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1005"
    strings:
        $readFile = "readFileSync("
        $readFile2 = "readFile("
        $passwd = "/etc/passwd"
        $shadow = "/etc/shadow"
        $ssh = ".ssh/id_rsa"
        $env = ".env"
        $bashrc = ".bashrc"
    condition:
        ($readFile or $readFile2) and ($passwd or $shadow or $ssh or $env or $bashrc)
}

rule JS_Exfil_Screenshot {
    meta:
        description = "Detects screenshot capture"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1113"
    strings:
        $screenshot1 = "robotjs"
        $screenshot2 = "screenshots"
        $screenshot3 = "captureScreen"
    condition:
        $screenshot1 or $screenshot2 or $screenshot3
}

rule JS_FileInclude {
    meta:
        description = "Detects dynamic file inclusion"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1059.007"
    strings:
        $include1 = "require(req."
        $include2 = "import(req."
        $include3 = "require(req.query"
        $include4 = "include("
    condition:
        $include1 or $include2 or $include3 or $include4
}

rule JS_Obfuscation_Base64 {
    meta:
        description = "Detects Base64 obfuscation"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1027.001"
    strings:
        $b64_1 = "Buffer.from("
        $b64_2 = ".toString('base64')"
        $b64_3 = "atob("
        $b64_4 = "btoa("
    condition:
        $b64_1 or $b64_2 or $b64_3 or $b64_4
}

rule JS_Obfuscation_DynamicEval {
    meta:
        description = "Detects dynamic eval construction"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1027.001"
    strings:
        $dynamic1 = "[].constructor"
        $dynamic2 = "''['constructor"
        $dynamic3 = "Function("
    condition:
        $dynamic1 or $dynamic2 or $dynamic3
}

rule JS_Obfuscation_FunctionArray {
    meta:
        description = "Detects function array obfuscation"
        author = "Scanner V3 - Round22"
        severity = "medium"
        mitre = "T1027.001"
    strings:
        $arr = "['"
        $arr2 = "']['"
        $call = "()"
        $fromCharCode = "fromCharCode"
    condition:
        $arr and $arr2 and ($call or $fromCharCode)
}

rule JS_Obfuscation_StringDecoding {
    meta:
        description = "Detects string decoding obfuscation"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1027.001"
    strings:
        $hex = "Buffer.from("
        $hex2 = "'hex')"
        $unescape = "unescape("
        $decode = "decodeURI("
    condition:
        ($hex and $hex2) or $unescape or $decode
}

rule JS_PathTraversal {
    meta:
        description = "Detects path traversal attack"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1083"
    strings:
        $traversal1 = "../"
        $traversal2 = "..\\\\"
        $traversal3 = "....//....//...."
        $readFile = "readFileSync("
    condition:
        ($traversal1 or $traversal2 or $traversal3) and $readFile
}

rule JS_Persist_FileWrite {
    meta:
        description = "Detects file write for persistence"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1055"
    strings:
        $writeFile = "writeFileSync("
        $writeFile2 = "writeFile("
        $appendFile = "appendFileSync("
        $bashrc = ".bashrc"
        $profile = ".profile"
    condition:
        ($writeFile or $writeFile2 or $appendFile) and ($bashrc or $profile)
}

rule JS_Persist_SpawnAtBoot {
    meta:
        description = "Detects spawn at boot persistence"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1547"
    strings:
        $spawn = "child_process.spawn"
        $detached = "detached: true"
        $unref = "unref()"
    condition:
        $spawn and $detached and $unref
}

rule JS_Persist_StartupScript {
    meta:
        description = "Detects startup script modification"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1037"
    strings:
        $startup1 = "process.platform"
        $startup2 = "win32"
        $registry = "HKEY_CURRENT_USER"
        $startup = "Startup"
    condition:
        $startup1 and ($startup2 or $registry or $startup)
}

rule JS_PrototypePollution {
    meta:
        description = "Detects prototype pollution attempt"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.007"
    strings:
        $proto1 = "__proto__"
        $proto2 = "constructor.prototype"
        $proto3 = "Object.defineProperty"
        $proto4 = "_.merge("
    condition:
        $proto1 or $proto2 or $proto3 or $proto4
}

rule JS_ReDoS {
    meta:
        description = "Detects potential ReDoS pattern"
        author = "Scanner V3 - Round22"
        severity = "medium"
        mitre = "T1499.003"
    strings:
        $regex = "RegExp("
        $regex2 = "/(.+)+"
        $regex3 = "/(a+)+"
        $match = ".match("
    condition:
        ($regex or $regex2 or $regex3) and $match
}

rule JS_RemoteCodeExecution_DynamicImport {
    meta:
        description = "Detects dynamic import from remote URL"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.007"
    strings:
        $import1 = "import('http"
        $import2 = "import(\"http"
        $import3 = "import('https"
        $import4 = "import(\"https"
        $require = "require('http"
        $require2 = "require(\"http"
    condition:
        $import1 or $import2 or $import3 or $import4 or $require or $require2
}

rule JS_RemoteCodeExecution_HttpEval {
    meta:
        description = "Detects remote code execution via HTTP + eval"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.007"
    strings:
        $http = "http.get("
        $https = "https.get("
        $fetch = "fetch("
        $axios = "axios.get("
        $request = "request("
        $eval = "eval("
        $then = ".then("
    condition:
        ($http or $https or $fetch or $axios or $request) and ($eval or $then)
}

rule JS_RemoteCodeExecution_ScriptInjection {
    meta:
        description = "Detects script tag injection"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.007"
    strings:
        $script1 = "document.createElement('script'"
        $script2 = "document.createElement(\"script\""
        $src = ".src = "
        $body = "document.body.appendChild"
        $head = "document.head.appendChild"
    condition:
        ($script1 or $script2) and $src and ($body or $head)
}

rule JS_SSRF {
    meta:
        description = "Detects Server-Side Request Forgery"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1190"
    strings:
        $ssrf1 = "http://169.254.169.254"
        $ssrf2 = "http://localhost"
        $ssrf3 = "http://127.0.0.1"
        $ssrf4 = "http://192.168."
        $fetch = "fetch("
        $request = "request("
    condition:
        ($ssrf1 or $ssrf2 or $ssrf3 or $ssrf4) and ($fetch or $request)
}

rule PS_BrowserCredentialTheft {
    meta:
        description = "Detects PowerShell browser credential theft"
        severity = "critical"
        mitre = "T1555.001"
    strings:
        $chrome = "Chrome/Default/Login Data"
        $firefox = "Firefox/Profiles/logins.json"
        $decrypt = "ProtectedData.Unprotect"
        $dpapi = "CryptUnprotectData"
    condition:
        ($chrome or $firefox) and ($decrypt or $dpapi)
}

rule PS_CredentialDump {
    meta:
        description = "Detects PowerShell credential dumping"
        severity = "critical"
        mitre = "T1003"
    strings:
        $dump1 = "Get-LSASecret"
        $dump2 = "Get-RegistryHive"
        $dump3 = "Invoke-NinjaCopy"
        $dump4 = "VolumeShadowCopy"
        $sam = "SAM hive"
        $system = "SYSTEM hive"
    condition:
        any of them
}

rule PS_CredentialTheft {
    meta:
        description = "Detects PowerShell credential theft"
        severity = "critical"
        mitre = "T1003"
    strings:
        $cred1 = "Get-Credential"
        $cred2 = "SecureString"
        $cred3 = "ConvertFrom-SecureString"
        $keylog = "Get-Keystrokes"
        $mimi = "Invoke-Mimikatz"
    condition:
        any of them
}

rule PS_DataExfiltration {
    meta:
        description = "Detects PowerShell data exfiltration"
        severity = "high"
        mitre = "T1041"
    strings:
        $exfil1 = "Invoke-WebRequest -Uri"
        $exfil2 = "Invoke-RestMethod -Uri"
        $exfil3 = "[System.Convert]::ToBase64String"
        $exfil4 = "Compress-Archive"
    condition:
        any of them
}

rule PS_DownloadCradle {
    meta:
        description = "Detects PowerShell download and execute patterns"
        severity = "critical"
        mitre = "T1059.001"
    strings:
        $iex = "IEX"
        $iex2 = "Invoke-Expression"
        $iwr = "Invoke-WebRequest"
        $iwr2 = "iwr"
        $irm = "Invoke-RestMethod"
        $wc = "New-Object Net.WebClient"
        $download = "DownloadString"
        $download2 = "DownloadFile"
    condition:
        ($iex or $iex2) and ($iwr or $iwr2 or $irm or $wc or $download or $download2)
}

rule PS_EncodedCommand {
    meta:
        description = "Detects Base64 encoded PowerShell commands"
        severity = "critical"
        mitre = "T1059.001"
    strings:
        $enc1 = "-e "
        $enc2 = "-E "
        $enc3 = "-EncodedCommand"
        $enc4 = "-encodedcommand"
    condition:
        any of them
}

rule PS_Keylogger {
    meta:
        description = "Detects PowerShell keylogger"
        severity = "critical"
        mitre = "T1056"
    strings:
        $keylog1 = "Get-WindowsKey"
        $keylog2 = "Add-Type -AssemblyName System.Windows.Forms"
        $keylog3 = "[System.Windows.Forms.SendKeys]::SendWait"
    condition:
        any of them
}

rule PS_LateralMovement {
    meta:
        description = "Detects PowerShell lateral movement"
        severity = "critical"
        mitre = "T1021"
    strings:
        $lateral1 = "Invoke-Command -ComputerName"
        $lateral2 = "Enter-PSSession"
        $lateral3 = "New-PSSession"
        $lateral4 = "Invoke-WmiMethod"
    condition:
        any of them
}

rule PS_Obfuscation {
    meta:
        description = "Detects PowerShell obfuscation"
        severity = "high"
        mitre = "T1027"
    strings:
        $obfus1 = "-join"
        $obfus2 = "[char]"
        $obfus3 = "-bxor"
        $obfus4 = "0x"
    condition:
        $obfus1 and $obfus2 or $obfus3 or $obfus4
}

rule PS_Persistence {
    meta:
        description = "Detects PowerShell persistence"
        severity = "high"
        mitre = "T1547"
    strings:
        $persist1 = "New-Item -Path HKLM"
        $persist2 = "Set-ItemProperty -Path HK"
        $persist3 = "Register-ScheduledTask"
        $persist4 = "schtasks /create"
    condition:
        any of them
}

rule PS_PrivilegeEscalation {
    meta:
        description = "Detects PowerShell privilege escalation"
        severity = "critical"
        mitre = "T1548"
    strings:
        $bypass1 = "-ExecutionPolicy Bypass"
        $bypass2 = "ExecutionPolicy Unrestricted"
        $bypass3 = "Bypass -NoProfile"
        $bypass4 = "-windowstyle hidden"
        $bypass5 = "-WindowStyle Hidden"
    condition:
        any of them
}

rule PS_ReverseShell {
    meta:
        description = "Detects PowerShell reverse shell"
        severity = "critical"
        mitre = "T1059.001"
    strings:
        $shell1 = "New-Object System.Net.Sockets.TCPClient"
        $shell2 = "Get-Process -Id $PID"
        $shell3 = "$client = New-Object System.Net.Sockets.TCPClient"
        $shell4 = "$stream = $client.GetStream()"
    condition:
        any of them
}