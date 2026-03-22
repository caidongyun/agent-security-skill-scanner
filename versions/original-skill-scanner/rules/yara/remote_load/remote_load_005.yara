rule RE-YARA-005 {
    meta:
        description = "CDN 资源加载 - RL005"
        category = "remote_load"
        severity = "medium"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 75
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "cdn.jsdelivr.net" nocase
        $s1 = "unpkg.com" nocase
        $s2 = "raw.githubusercontent.com" nocase
    
    condition:
        any of them
}
