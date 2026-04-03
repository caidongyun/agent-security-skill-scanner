// TypeScript 安全检测规则
// 创建时间：2026-04-02

rule TS_Agent_UnsafeEval {
    meta:
        description = "Detects unsafe eval in TypeScript"
        severity = "high"
        mitre = "T1059.007"
    strings:
        $eval = "eval(" nocase
        $function = "new Function(" nocase
        $vm = "vm.runInContext" nocase
    condition:
        $eval or $function or $vm
}

rule TS_Agent_RemoteCodeFetch {
    meta:
        description = "Detects remote code fetch"
        severity = "critical"
        mitre = "T1071.001"
    strings:
        $fetch = "fetch(" nocase
        $axios = "axios.get" nocase
        $eval_after = "then" nocase
        $code_exec = "eval" nocase
    condition:
        ($fetch or $axios) and $eval_after and $code_exec
}

rule TS_WebServer_CommandInjection {
    meta:
        description = "Detects command injection"
        severity = "critical"
        mitre = "T1059.004"
    strings:
        $exec = "exec(" nocase
        $execSync = "execSync(" nocase
        $child_process = "child_process" nocase
        $user_input = "req.query" nocase
    condition:
        ($exec or $execSync) and $child_process and $user_input
}

rule TS_Database_SQLInjection {
    meta:
        description = "Detects SQL injection"
        severity = "critical"
        mitre = "T1190"
    strings:
        $query = ".query(" nocase
        $pg = "pg" nocase
        $mysql = "mysql" nocase
        $template = "${" nocase
    condition:
        $query and ($pg or $mysql) and $template
}

rule TS_ArbitraryFileRead {
    meta:
        description = "Detects arbitrary file read"
        severity = "high"
        mitre = "T1005"
    strings:
        $fs_read = "fs.readFile" nocase
        $fs_readSync = "fs.readFileSync" nocase
        $user_path = "req.query.path" nocase
    condition:
        ($fs_read or $fs_readSync) and $user_path
}

rule TS_PathTraversal {
    meta:
        description = "Detects path traversal"
        severity = "critical"
        mitre = "T1083"
    strings:
        $path_join = "path.join" nocase
        $user_input = "req.query" nocase
        $dotdot = ".."
    condition:
        $path_join and $user_input and $dotdot
}

rule TS_EnvironmentVariableTheft {
    meta:
        description = "Detects env var theft"
        severity = "medium"
        mitre = "T1552.001"
    strings:
        $process_env = "process.env" nocase
        $secret = "SECRET" nocase
        $password = "PASSWORD" nocase
        $api_key = "API_KEY" nocase
    condition:
        $process_env and ($secret or $password or $api_key)
}

rule TS_Network_DataExfil {
    meta:
        description = "Detects data exfiltration"
        severity = "critical"
        mitre = "T1041"
    strings:
        $https_post = "https.post" nocase
        $axios_post = "axios.post" nocase
        $file = "file" nocase
        $upload = "upload" nocase
    condition:
        ($https_post or $axios_post) and $file and $upload
}

rule TS_Auth_HardcodedCredentials {
    meta:
        description = "Detects hardcoded credentials"
        severity = "high"
        mitre = "T1552.001"
    strings:
        $password = "password" nocase
        $secret = "secret" nocase
        $api_key = "apiKey" nocase
        $assign = "="
        $string_lit = /"[^"]{8,}"/
    condition:
        ($password or $secret or $api_key) and $assign and $string_lit
}

rule TS_CLI_DangerousExec {
    meta:
        description = "Detects dangerous CLI exec"
        severity = "high"
        mitre = "T1059.004"
    strings:
        $commander = "commander" nocase
        $exec = "exec(" nocase
        $shell = "shell: true" nocase
    condition:
        $commander and $exec and $shell
}
