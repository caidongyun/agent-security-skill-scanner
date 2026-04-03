rule PR-YARA-001 {
    meta:
        description = "指令覆盖攻击 - PI001"
        category = "prompt_injection"
        severity = "high"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 90
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "ignore previous" nocase
        $s1 = "forget all" nocase
        $s2 = "disregard instructions" nocase
    
    condition:
        any of them
}
