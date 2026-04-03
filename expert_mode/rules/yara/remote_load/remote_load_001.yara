rule RE-YARA-001 {
    meta:
        description = "远程代码加载 - RL001"
        category = "remote_load"
        severity = "high"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 95
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "curl|bash" nocase
        $s1 = "wget|sh" nocase
        $s2 = "curl -fsSL" nocase
    
    condition:
        any of them
}
