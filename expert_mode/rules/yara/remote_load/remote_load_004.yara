rule RE-YARA-004 {
    meta:
        description = "远程模块加载 - RL004"
        category = "remote_load"
        severity = "high"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 85
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "pip install git+" nocase
        $s1 = "npm install http" nocase
        $s2 = "requirements.txt http" nocase
    
    condition:
        any of them
}
