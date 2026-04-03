rule ME-YARA-004 {
    meta:
        description = "会话劫持 - MP004"
        category = "memory_pollution"
        severity = "high"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 90
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "session hijack" nocase
        $s1 = "token steal" nocase
        $s2 = "cookie theft" nocase
    
    condition:
        any of them
}
