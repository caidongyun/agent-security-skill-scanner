// Go 语言安全检测规则
// 创建时间：2026-04-02

rule Go_CommandInjection {
    meta:
        description = "Detects command injection in Go"
        severity = "critical"
        mitre = "T1059.004"
    strings:
        $os_exec = "os/exec" nocase
        $exec = "exec.Command" nocase
        $user_input = "r.URL.Query" nocase
        $form = "r.FormValue" nocase
    condition:
        $os_exec and $exec and ($user_input or $form)
}

rule Go_SQLInjection {
    meta:
        description = "Detects SQL injection in Go"
        severity = "critical"
        mitre = "T1190"
    strings:
        $database_sql = "database/sql" nocase
        $query = ".Query(" nocase
        $queryf = ".Queryf(" nocase
        $sprintf = "fmt.Sprintf" nocase
        $concat = "+"
    condition:
        $database_sql and ($query or $queryf) and ($sprintf or $concat)
}

rule Go_ArbitraryFileRead {
    meta:
        description = "Detects arbitrary file read in Go"
        severity = "high"
        mitre = "T1005"
    strings:
        $os_open = "os.Open" nocase
        $ioutil = "ioutil.ReadFile" nocase
        $user_input = "r.URL.Query" nocase
    condition:
        ($os_open or $ioutil) and $user_input
}

rule Go_PathTraversal {
    meta:
        description = "Detects path traversal in Go"
        severity = "critical"
        mitre = "T1083"
    strings:
        $filepath = "filepath.Join" nocase
        $user_input = "r.URL.Query" nocase
        $dotdot = ".."
    condition:
        $filepath and $user_input and $dotdot
}

rule Go_NetworkScan {
    meta:
        description = "Detects network scanning in Go"
        severity = "high"
        mitre = "T1046"
    strings:
        $net_dial = "net.Dial" nocase
        $net_dialTimeout = "net.DialTimeout" nocase
        $for_loop = "for" nocase
        $port = "port" nocase
    condition:
        ($net_dial or $net_dialTimeout) and $for_loop and $port
}

rule Go_DataExfil {
    meta:
        description = "Detects data exfiltration in Go"
        severity = "critical"
        mitre = "T1041"
    strings:
        $http_post = "http.Post" nocase
        $http_client = "http.Client" nocase
        $do = ".Do(" nocase
        $file = "file" nocase
    condition:
        ($http_post or $http_client) and $do and $file
}

rule Go_EnvVariableTheft {
    meta:
        description = "Detects env variable theft in Go"
        severity = "medium"
        mitre = "T1552.001"
    strings:
        $os_getenv = "os.Getenv" nocase
        $secret = "SECRET" nocase
        $password = "PASSWORD" nocase
        $api_key = "API_KEY" nocase
    condition:
        $os_getenv and ($secret or $password or $api_key)
}

rule Go_HardcodedCredentials {
    meta:
        description = "Detects hardcoded credentials in Go"
        severity = "high"
        mitre = "T1552.001"
    strings:
        $password = "password" nocase
        $secret = "secret" nocase
        $api_key = "apiKey" nocase
        $assign = ":="
        $string_lit = /"[^"]{8,}"/
    condition:
        ($password or $secret or $api_key) and $assign and $string_lit
}

rule Go_RemoteCodeFetch {
    meta:
        description = "Detects remote code fetch in Go"
        severity = "critical"
        mitre = "T1071.001"
    strings:
        $http_get = "http.Get" nocase
        $https_get = "https.Get" nocase
        $eval = "eval" nocase
        $exec = "exec" nocase
    condition:
        ($http_get or $https_get) and ($eval or $exec)
}

rule Go_CryptoWeak {
    meta:
        description = "Detects weak crypto in Go"
        severity = "medium"
        mitre = "T1553.001"
    strings:
        $md5 = "md5" nocase
        $sha1 = "sha1" nocase
        $crypto = "crypto/" nocase
        $new = "New" nocase
    condition:
        $crypto and ($md5 or $sha1) and $new
}
