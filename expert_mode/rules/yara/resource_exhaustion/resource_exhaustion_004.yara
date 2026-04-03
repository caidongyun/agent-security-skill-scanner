rule RE-YARA-004 {
    meta:
        description = "网络带宽耗尽 - RE004"
        category = "resource_exhaustion"
        severity = "high"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 95
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "flood network" nocase
        $s1 = "bandwidth exhaust" nocase
        $s2 = "ddos" nocase
    
    condition:
        any of them
}
