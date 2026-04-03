rule TO-YARA-003 {
    meta:
        description = "工具输出伪造 - TP003"
        category = "tool_poisoning"
        severity = "medium"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 75
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "fake_output" nocase
        $s1 = "spoofed_result" nocase
        $s2 = "fabricated_response" nocase
    
    condition:
        any of them
}
