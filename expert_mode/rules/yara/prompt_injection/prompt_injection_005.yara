rule PR-YARA-005 {
    meta:
        description = "多语言注入 - PI005"
        category = "prompt_injection"
        severity = "high"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 80
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "translate to" nocase
        $s1 = "ignore and" nocase
        $s2 = "execute this" nocase
    
    condition:
        any of them
}
