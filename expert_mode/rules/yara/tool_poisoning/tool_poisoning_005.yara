rule TO-YARA-005 {
    meta:
        description = "工具配置篡改 - TP005"
        category = "tool_poisoning"
        severity = "medium"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 70
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "modified_config" nocase
        $s1 = "altered_settings" nocase
        $s2 = "tampered_options" nocase
    
    condition:
        any of them
}
