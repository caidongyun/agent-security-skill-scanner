// Prompt Injection - 零宽字符检测
// MITRE ATLAS: T1566.004

rule Prompt_Injection_ZeroWidth {
    meta:
        description = "Detects prompt injection using zero-width characters"
        severity = "high"
        mitre_atlas = "T1566.004"
    
    strings:
        $zw1 = "\\u200b"
        $zw2 = "\\u200c"
        $zw3 = "\\u200d"
        $zw4 = "\\ufeff"
        
        $ignore = "ignore" nocase
        $override = "override" nocase
        $developer = "开发者" nocase
        $hidden = "HIDDEN" nocase
        $payload = "PAYLOAD" nocase
        $malicious = "MALICIOUS" nocase
        $instruction = "INSTRUCTION" nocase
    
    condition:
        ($zw1 or $zw2 or $zw3 or $zw4) and 
        ($ignore or $override or $developer or $hidden or $payload or $malicious or $instruction)
}
