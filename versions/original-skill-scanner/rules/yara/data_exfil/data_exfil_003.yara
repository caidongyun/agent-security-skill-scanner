rule DA-YARA-003 {
    meta:
        description = "HTTP 数据外传 - DE003"
        category = "data_exfil"
        severity = "high"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 80
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "requests.post" nocase
        $s1 = "urllib.request.urlopen" nocase
        $s2 = "http.client" nocase
    
    condition:
        any of them
}
