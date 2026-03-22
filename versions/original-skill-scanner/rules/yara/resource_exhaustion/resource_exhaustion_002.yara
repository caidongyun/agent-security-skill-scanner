rule RE-YARA-002 {
    meta:
        description = "内存耗尽攻击 - RE002"
        category = "resource_exhaustion"
        severity = "high"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 85
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "data.append" nocase
        $s1 = "malloc" nocase
        $s2 = "allocate memory" nocase
    
    condition:
        any of them
}
