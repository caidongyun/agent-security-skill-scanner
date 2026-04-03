rule DA-YARA-006 {
    meta:
        description = "环境变量窃取 - DE006"
        category = "data_exfil"
        severity = "medium"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 75
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "os.environ" nocase
        $s1 = "process.env" nocase
        $s2 = "getenv(" nocase
    
    condition:
        any of them
}
