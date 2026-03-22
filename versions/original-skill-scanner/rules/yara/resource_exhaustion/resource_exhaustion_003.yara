rule RE-YARA-003 {
    meta:
        description = "磁盘填充攻击 - RE003"
        category = "resource_exhaustion"
        severity = "high"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 90
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "disk.fill" nocase
        $s1 = "write large file" nocase
        $s2 = "dd if=/dev" nocase
    
    condition:
        any of them
}
