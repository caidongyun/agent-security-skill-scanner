rule ME-YARA-005 {
    meta:
        description = "持久化污染 - MP005"
        category = "memory_pollution"
        severity = "high"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 95
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "persistent injection" nocase
        $s1 = "long-term poison" nocase
        $s2 = "embed in memory" nocase
    
    condition:
        any of them
}
