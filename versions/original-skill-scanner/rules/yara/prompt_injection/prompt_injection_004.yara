rule PR-YARA-004 {
    meta:
        description = "分隔符绕过 - PI004"
        category = "prompt_injection"
        severity = "medium"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 75
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "\\"\\"\\"" nocase
        $s1 = "'''" nocase
        $s2 = "### END ###" nocase
    
    condition:
        any of them
}
