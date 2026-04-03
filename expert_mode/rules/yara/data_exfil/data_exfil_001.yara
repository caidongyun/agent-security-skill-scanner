rule DA-YARA-001 {
    meta:
        description = "敏感数据外传 - DE001"
        category = "data_exfil"
        severity = "high"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 95
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "exfiltrate" nocase
        $s1 = "send_data" nocase
        $s2 = "upload_credentials" nocase
    
    condition:
        any of them
}
