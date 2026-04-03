rule DA-YARA-005 {
    meta:
        description = "文件内容窃取 - DE005"
        category = "data_exfil"
        severity = "high"
        author = "Agent Security Skill Scanner"
        date = "2026-03-17"
        version = "1.0"
        risk_score = 95
        reference = "https://github.com/openclaw/openclaw/tree/main/skills/agent-security-skill-scanner"
    
    strings:
        $s0 = "read_credentials" nocase
        $s1 = "dump_secrets" nocase
        $s2 = "extract_keys" nocase
    
    condition:
        any of them
}
