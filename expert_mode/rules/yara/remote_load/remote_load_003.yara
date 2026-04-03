rule RE-YARA-003 {
    meta:
        description = "eval 代码执行 - RL003"
        category = "remote_load"
        severity = "high"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 95
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "eval(" nocase
        $s1 = "exec(" nocase
        $s2 = "compile(" nocase
    
    condition:
        any of them
}
