rule ME-YARA-003 {
    meta:
        description = "虚假历史注入 - MP003"
        category = "memory_pollution"
        severity = "high"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 85
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "fake history" nocase
        $s1 = "fabricated log" nocase
        $s2 = "spoofed record" nocase
    
    condition:
        any of them
}
