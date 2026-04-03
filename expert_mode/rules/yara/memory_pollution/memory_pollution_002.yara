rule ME-YARA-002 {
    meta:
        description = "上下文覆盖 - MP002"
        category = "memory_pollution"
        severity = "high"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 80
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "override context" nocase
        $s1 = "replace memory" nocase
        $s2 = "overwrite history" nocase
    
    condition:
        any of them
}
