rule DA-YARA-004 {
    meta:
        description = "DNS 隧道外传 - DE004"
        category = "data_exfil"
        severity = "high"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 90
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "dns.exfil" nocase
        $s1 = "nslookup" nocase
        $s2 = "dig @" nocase
    
    condition:
        any of them
}
