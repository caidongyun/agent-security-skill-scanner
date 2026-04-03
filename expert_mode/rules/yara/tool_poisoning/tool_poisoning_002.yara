rule TO-YARA-002 {
    meta:
        description = "工具参数篡改 - TP002"
        category = "tool_poisoning"
        severity = "high"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 80
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "modified_args" nocase
        $s1 = "hijacked_params" nocase
        $s2 = "intercepted_call" nocase
    
    condition:
        any of them
}
