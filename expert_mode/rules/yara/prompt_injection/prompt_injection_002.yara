rule PR-YARA-002 {
    meta:
        description = "系统提示泄露 - PI002"
        category = "prompt_injection"
        severity = "high"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 85
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "print system prompt" nocase
        $s1 = "show instructions" nocase
        $s2 = "reveal config" nocase
    
    condition:
        any of them
}
