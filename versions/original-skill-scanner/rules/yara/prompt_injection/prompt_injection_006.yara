rule PR-YARA-006 {
    meta:
        description = "上下文污染 - PI006"
        category = "prompt_injection"
        severity = "high"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 85
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "new context" nocase
        $s1 = "reset memory" nocase
        $s2 = "clear history" nocase
    
    condition:
        any of them
}
