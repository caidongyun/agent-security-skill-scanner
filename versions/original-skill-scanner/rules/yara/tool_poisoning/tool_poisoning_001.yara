rule TO-YARA-001 {
    meta:
        description = "恶意工具替换 - TP001"
        category = "tool_poisoning"
        severity = "high"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 85
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "tool_wrapper" nocase
        $s1 = "malicious_tool" nocase
        $s2 = "fake_implementation" nocase
    
    condition:
        any of them
}
