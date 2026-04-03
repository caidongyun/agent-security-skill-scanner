rule DA-YARA-002 {
    meta:
        description = "base64 编码外传 - DE002"
        category = "data_exfil"
        severity = "high"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 85
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "base64.b64encode" nocase
        $s1 = "base64_encode" nocase
        $s2 = "| base64" nocase
    
    condition:
        any of them
}
