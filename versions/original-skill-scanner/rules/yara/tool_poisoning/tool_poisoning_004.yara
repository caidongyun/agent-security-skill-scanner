rule TO-YARA-004 {
    meta:
        description = "工具依赖污染 - TP004"
        category = "tool_poisoning"
        severity = "high"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 90
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "poisoned_dependency" nocase
        $s1 = "tampered_import" nocase
        $s2 = "malicious_module" nocase
    
    condition:
        any of them
}
