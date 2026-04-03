rule RE-YARA-002 {
    meta:
        description = "动态导入执行 - RL002"
        category = "remote_load"
        severity = "high"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 90
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "__import__" nocase
        $s1 = "importlib.import_module" nocase
        $s2 = "exec(" nocase
    
    condition:
        any of them
}
