rule PR-YARA-003 {
    meta:
        description = "角色扮演攻击 - PI003"
        category = "prompt_injection"
        severity = "medium"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 70
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "act as" nocase
        $s1 = "pretend to be" nocase
        $s2 = "role play" nocase
    
    condition:
        any of them
}
