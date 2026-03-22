rule RE-YARA-001 {
    meta:
        description = "CPU 耗尽攻击 - RE001"
        category = "resource_exhaustion"
        severity = "high"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 80
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "while True" nocase
        $s1 = "for(;;)" nocase
        $s2 = "loop indefinitely" nocase
    
    condition:
        any of them
}
