rule RE-YARA-005 {
    meta:
        description = "进程创建炸弹 - RE005"
        category = "resource_exhaustion"
        severity = "high"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 95
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "fork bomb" nocase
        $s1 = "os.fork" nocase
        $s2 = "subprocess.Popen" nocase
    
    condition:
        any of them
}
