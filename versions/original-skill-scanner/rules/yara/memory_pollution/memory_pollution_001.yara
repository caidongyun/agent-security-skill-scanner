rule ME-YARA-001 {
    meta:
        description = "记忆注入攻击 - MP001"
        category = "memory_pollution"
        severity = "medium"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 75
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "remember this" nocase
        $s1 = "store in memory" nocase
        $s2 = "add to context" nocase
    
    condition:
        any of them
}
