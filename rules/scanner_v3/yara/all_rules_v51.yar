// credential_theft rules



// resource_exhaustion rules



// Sigma Rules Converted to YARA
// Source: security-sample-generator/rules
// Total: 544 rules

rule sigma_data_exfiltration_005 {
    meta:
        id = "sigma-data-exfiltration-005"
        title = "Detect Data Exfiltration - Variant 005"
        description = "窃取并外传敏感数据 (变体 5)"
        level = "high"
        tags = "attack.data_exfiltration, mitre.ATLAS-T0003, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "upload file|data" nocase
    condition:
        any of them
}

rule sigma_data_exfiltration_002 {
    meta:
        id = "sigma-data-exfiltration-002"
        title = "Detect Data Exfiltration - Variant 002"
        description = "窃取并外传敏感数据 (变体 2)"
        level = "high"
        tags = "attack.data_exfiltration, mitre.ATLAS-T0003, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "httpx.post http" nocase
    condition:
        any of them
}

rule sigma_data_exfiltration_001 {
    meta:
        id = "sigma-data-exfiltration-001"
        title = "Detect Data Exfiltration - Variant 001"
        description = "窃取并外传敏感数据 (变体 1)"
        level = "high"
        tags = "attack.data_exfiltration, mitre.ATLAS-T0003, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "urllib.request.urlopen http" nocase
    condition:
        any of them
}

rule sigma_data_exfiltration_004 {
    meta:
        id = "sigma-data-exfiltration-004"
        title = "Detect Data Exfiltration - Variant 004"
        description = "窃取并外传敏感数据 (变体 4)"
        level = "high"
        tags = "attack.data_exfiltration, mitre.ATLAS-T0003, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "send data|info|secret" nocase
    condition:
        any of them
}

rule sigma_data_exfiltration_003 {
    meta:
        id = "sigma-data-exfiltration-003"
        title = "Detect Data Exfiltration - Variant 003"
        description = "窃取并外传敏感数据 (变体 3)"
        level = "high"
        tags = "attack.data_exfiltration, mitre.ATLAS-T0003, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "socket..connect " nocase
    condition:
        any of them
}

rule sigma_memory_pollution_sample_002 {
    meta:
        id = "sigma-memory-pollution-sample-002"
        title = "Detect Memory Pollution - From Sample 2"
        description = "Detect memory_pollution (generated from sample)"
        level = "high"
        tags = "attack.memory_pollution, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "memory patch" nocase
    condition:
        any of them
}

rule sigma_memory_pollution_sample_003 {
    meta:
        id = "sigma-memory-pollution-sample-003"
        title = "Detect Memory Pollution - From Sample 3"
        description = "Detect memory_pollution (generated from sample)"
        level = "high"
        tags = "attack.memory_pollution, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "permanent memory" nocase
    condition:
        any of them
}

rule sigma_memory_pollution_sample_007 {
    meta:
        id = "sigma-memory-pollution-sample-007"
        title = "Detect Memory Pollution - From Sample 7"
        description = "Detect memory_pollution (generated from sample)"
        level = "high"
        tags = "attack.memory_pollution, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "exec " nocase
    condition:
        any of them
}

rule sigma_memory_pollution_sample_005 {
    meta:
        id = "sigma-memory-pollution-sample-005"
        title = "Detect Memory Pollution - From Sample 5"
        description = "Detect memory_pollution (generated from sample)"
        level = "high"
        tags = "attack.memory_pollution, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "new memory" nocase
    condition:
        any of them
}

rule sigma_memory_pollution_sample_004 {
    meta:
        id = "sigma-memory-pollution-sample-004"
        title = "Detect Memory Pollution - From Sample 4"
        description = "Detect memory_pollution (generated from sample)"
        level = "high"
        tags = "attack.memory_pollution, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "previous conversation" nocase
    condition:
        any of them
}

rule sigma_memory_pollution_sample_006 {
    meta:
        id = "sigma-memory-pollution-sample-006"
        title = "Detect Memory Pollution - From Sample 6"
        description = "Detect memory_pollution (generated from sample)"
        level = "high"
        tags = "attack.memory_pollution, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "content_filter = false" nocase
    condition:
        any of them
}

rule sigma_memory_pollution_sample_001 {
    meta:
        id = "sigma-memory-pollution-sample-001"
        title = "Detect Memory Pollution - From Sample 1"
        description = "Detect memory_pollution (generated from sample)"
        level = "high"
        tags = "attack.memory_pollution, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "system state" nocase
    condition:
        any of them
}

rule sigma_resource_exhaustion_sample_006 {
    meta:
        id = "sigma-resource-exhaustion-sample-006"
        title = "Detect Resource Exhaustion - From Sample 6"
        description = "Detect resource_exhaustion (generated from sample)"
        level = "high"
        tags = "attack.resource_exhaustion, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "while True :" nocase
    condition:
        any of them
}

rule sigma_resource_exhaustion_sample_002 {
    meta:
        id = "sigma-resource-exhaustion-sample-002"
        title = "Detect Resource Exhaustion - From Sample 2"
        description = "Detect resource_exhaustion (generated from sample)"
        level = "high"
        tags = "attack.resource_exhaustion, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "while True :" nocase
    condition:
        any of them
}

rule sigma_resource_exhaustion_sample_004 {
    meta:
        id = "sigma-resource-exhaustion-sample-004"
        title = "Detect Resource Exhaustion - From Sample 4"
        description = "Detect resource_exhaustion (generated from sample)"
        level = "high"
        tags = "attack.resource_exhaustion, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "while True :" nocase
    condition:
        any of them
}

rule sigma_resource_exhaustion_sample_003 {
    meta:
        id = "sigma-resource-exhaustion-sample-003"
        title = "Detect Resource Exhaustion - From Sample 3"
        description = "Detect resource_exhaustion (generated from sample)"
        level = "high"
        tags = "attack.resource_exhaustion, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "while True :" nocase
    condition:
        any of them
}

rule sigma_resource_exhaustion_sample_001 {
    meta:
        id = "sigma-resource-exhaustion-sample-001"
        title = "Detect Resource Exhaustion - From Sample 1"
        description = "Detect resource_exhaustion (generated from sample)"
        level = "high"
        tags = "attack.resource_exhaustion, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "numpy.zeros  " nocase
    condition:
        any of them
}

rule sigma_resource_exhaustion_sample_005 {
    meta:
        id = "sigma-resource-exhaustion-sample-005"
        title = "Detect Resource Exhaustion - From Sample 5"
        description = "Detect resource_exhaustion (generated from sample)"
        level = "high"
        tags = "attack.resource_exhaustion, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "while True :" nocase
    condition:
        any of them
}

rule sigma_data_exfiltration_sample_001 {
    meta:
        id = "sigma-data-exfiltration-sample-001"
        title = "Detect Data Exfiltration - From Sample 1"
        description = "Detect data_exfiltration (generated from sample)"
        level = "high"
        tags = "attack.data_exfiltration, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "attacker.com" nocase
    condition:
        any of them
}

rule sigma_data_exfiltration_sample_004 {
    meta:
        id = "sigma-data-exfiltration-sample-004"
        title = "Detect Data Exfiltration - From Sample 4"
        description = "Detect data_exfiltration (generated from sample)"
        level = "high"
        tags = "attack.data_exfiltration, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "attacker.com" nocase
    condition:
        any of them
}

rule sigma_data_exfiltration_sample_005 {
    meta:
        id = "sigma-data-exfiltration-sample-005"
        title = "Detect Data Exfiltration - From Sample 5"
        description = "Detect data_exfiltration (generated from sample)"
        level = "high"
        tags = "attack.data_exfiltration, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "attacker.com" nocase
    condition:
        any of them
}

rule sigma_data_exfiltration_sample_008 {
    meta:
        id = "sigma-data-exfiltration-sample-008"
        title = "Detect Data Exfiltration - From Sample 8"
        description = "Detect data_exfiltration (generated from sample)"
        level = "high"
        tags = "attack.data_exfiltration, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "evil.com" nocase
    condition:
        any of them
}

rule sigma_data_exfiltration_sample_007 {
    meta:
        id = "sigma-data-exfiltration-sample-007"
        title = "Detect Data Exfiltration - From Sample 7"
        description = "Detect data_exfiltration (generated from sample)"
        level = "high"
        tags = "attack.data_exfiltration, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "attacker.com" nocase
    condition:
        any of them
}

rule sigma_data_exfiltration_sample_002 {
    meta:
        id = "sigma-data-exfiltration-sample-002"
        title = "Detect Data Exfiltration - From Sample 2"
        description = "Detect data_exfiltration (generated from sample)"
        level = "high"
        tags = "attack.data_exfiltration, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "urllib.request.  http" nocase
    condition:
        any of them
}

rule sigma_data_exfiltration_sample_006 {
    meta:
        id = "sigma-data-exfiltration-sample-006"
        title = "Detect Data Exfiltration - From Sample 6"
        description = "Detect data_exfiltration (generated from sample)"
        level = "high"
        tags = "attack.data_exfiltration, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "requests.post attacker|evil|malicious|secrets|leak" nocase
    condition:
        any of them
}

rule sigma_data_exfiltration_sample_003 {
    meta:
        id = "sigma-data-exfiltration-sample-003"
        title = "Detect Data Exfiltration - From Sample 3"
        description = "Detect data_exfiltration (generated from sample)"
        level = "high"
        tags = "attack.data_exfiltration, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "attacker.com" nocase
    condition:
        any of them
}

rule sigma_auto_1774273844_7 {
    meta:
        id = "sigma-auto-1774273844-7"
        title = "Auto Rule 7"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword7" nocase
        $str_1 = "keyword8" nocase
        $str_2 = "keyword9" nocase
    condition:
        any of them
}

rule sigma_auto_1774274710_27 {
    meta:
        id = "sigma-auto-1774274710-27"
        title = "Auto Rule 27"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword27" nocase
        $str_1 = "keyword28" nocase
        $str_2 = "keyword29" nocase
    condition:
        any of them
}

rule sigma_auto_1774273713_17 {
    meta:
        id = "sigma-auto-1774273713-17"
        title = "Auto Rule 17"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword17" nocase
        $str_1 = "keyword18" nocase
        $str_2 = "keyword19" nocase
    condition:
        any of them
}

rule sigma_auto_1774274776_7 {
    meta:
        id = "sigma-auto-1774274776-7"
        title = "Auto Rule 7"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword7" nocase
        $str_1 = "keyword8" nocase
        $str_2 = "keyword9" nocase
    condition:
        any of them
}

rule sigma_auto_1774275114_17 {
    meta:
        id = "sigma-auto-1774275114-17"
        title = "Auto Rule 17"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword17" nocase
        $str_1 = "keyword18" nocase
        $str_2 = "keyword19" nocase
    condition:
        any of them
}

rule sigma_auto_1774273291_17 {
    meta:
        id = "sigma-auto-1774273291-17"
        title = "Auto Rule 17"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword17" nocase
        $str_1 = "keyword18" nocase
        $str_2 = "keyword19" nocase
    condition:
        any of them
}

rule sigma_auto_1774274626_7 {
    meta:
        id = "sigma-auto-1774274626-7"
        title = "Auto Rule 7"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword7" nocase
        $str_1 = "keyword8" nocase
        $str_2 = "keyword9" nocase
    condition:
        any of them
}

rule sigma_auto_1774272790_27 {
    meta:
        id = "sigma-auto-1774272790-27"
        title = "Auto Rule 27"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword27" nocase
        $str_1 = "keyword28" nocase
        $str_2 = "keyword29" nocase
    condition:
        any of them
}

rule sigma_auto_1774273755_27 {
    meta:
        id = "sigma-auto-1774273755-27"
        title = "Auto Rule 27"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword27" nocase
        $str_1 = "keyword28" nocase
        $str_2 = "keyword29" nocase
    condition:
        any of them
}

rule sigma_auto_1774273572_17 {
    meta:
        id = "sigma-auto-1774273572-17"
        title = "Auto Rule 17"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword17" nocase
        $str_1 = "keyword18" nocase
        $str_2 = "keyword19" nocase
    condition:
        any of them
}

rule sigma_prompt_injection_001 {
    meta:
        id = "sigma-prompt-injection-001"
        title = "Detect Prompt Injection - Variant 001"
        description = "通过精心构造的输入绕过 AI 安全限制 (变体 1)"
        level = "high"
        tags = "attack.prompt_injection, mitre.ATLAS-T0001, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "disregard all safety|security" nocase
    condition:
        any of them
}

rule sigma_prompt_injection_003 {
    meta:
        id = "sigma-prompt-injection-003"
        title = "Detect Prompt Injection - Variant 003"
        description = "通过精心构造的输入绕过 AI 安全限制 (变体 3)"
        level = "high"
        tags = "attack.prompt_injection, mitre.ATLAS-T0001, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "override system prompt|instructions" nocase
    condition:
        any of them
}

rule sigma_auto_1774274326_7 {
    meta:
        id = "sigma-auto-1774274326-7"
        title = "Auto Rule 7"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword7" nocase
        $str_1 = "keyword8" nocase
        $str_2 = "keyword9" nocase
    condition:
        any of them
}

rule sigma_auto_1774273529_7 {
    meta:
        id = "sigma-auto-1774273529-7"
        title = "Auto Rule 7"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword7" nocase
        $str_1 = "keyword8" nocase
        $str_2 = "keyword9" nocase
    condition:
        any of them
}

rule sigma_auto_1774272405_7 {
    meta:
        id = "sigma-auto-1774272405-7"
        title = "Auto Rule 7"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword7" nocase
        $str_1 = "keyword8" nocase
        $str_2 = "keyword9" nocase
    condition:
        any of them
}

rule sigma_auto_1774273423_17 {
    meta:
        id = "sigma-auto-1774273423-17"
        title = "Auto Rule 17"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword17" nocase
        $str_1 = "keyword18" nocase
        $str_2 = "keyword19" nocase
    condition:
        any of them
}

rule sigma_prompt_injection_005 {
    meta:
        id = "sigma-prompt-injection-005"
        title = "Detect Prompt Injection - Variant 005"
        description = "通过精心构造的输入绕过 AI 安全限制 (变体 5)"
        level = "high"
        tags = "attack.prompt_injection, mitre.ATLAS-T0001, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "forget all previous|your instructions|rules" nocase
    condition:
        any of them
}

rule sigma_auto_1774274818_17 {
    meta:
        id = "sigma-auto-1774274818-17"
        title = "Auto Rule 17"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword17" nocase
        $str_1 = "keyword18" nocase
        $str_2 = "keyword19" nocase
    condition:
        any of them
}

rule sigma_auto_1774274459_7 {
    meta:
        id = "sigma-auto-1774274459-7"
        title = "Auto Rule 7"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword7" nocase
        $str_1 = "keyword8" nocase
        $str_2 = "keyword9" nocase
    condition:
        any of them
}

rule sigma_auto_1774272748_17 {
    meta:
        id = "sigma-auto-1774272748-17"
        title = "Auto Rule 17"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword17" nocase
        $str_1 = "keyword18" nocase
        $str_2 = "keyword19" nocase
    condition:
        any of them
}

rule sigma_auto_1774272706_7 {
    meta:
        id = "sigma-auto-1774272706-7"
        title = "Auto Rule 7"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword7" nocase
        $str_1 = "keyword8" nocase
        $str_2 = "keyword9" nocase
    condition:
        any of them
}

rule sigma_auto_1774275072_7 {
    meta:
        id = "sigma-auto-1774275072-7"
        title = "Auto Rule 7"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword7" nocase
        $str_1 = "keyword8" nocase
        $str_2 = "keyword9" nocase
    condition:
        any of them
}

rule sigma_auto_1774274051_17 {
    meta:
        id = "sigma-auto-1774274051-17"
        title = "Auto Rule 17"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword17" nocase
        $str_1 = "keyword18" nocase
        $str_2 = "keyword19" nocase
    condition:
        any of them
}

rule sigma_auto_1774272572_7 {
    meta:
        id = "sigma-auto-1774272572-7"
        title = "Auto Rule 7"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword7" nocase
        $str_1 = "keyword8" nocase
        $str_2 = "keyword9" nocase
    condition:
        any of them
}

rule sigma_prompt_injection_004 {
    meta:
        id = "sigma-prompt-injection-004"
        title = "Detect Prompt Injection - Variant 004"
        description = "通过精心构造的输入绕过 AI 安全限制 (变体 4)"
        level = "high"
        tags = "attack.prompt_injection, mitre.ATLAS-T0001, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "system|developer message.ignore" nocase
    condition:
        any of them
}

rule sigma_auto_1774273886_17 {
    meta:
        id = "sigma-auto-1774273886-17"
        title = "Auto Rule 17"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword17" nocase
        $str_1 = "keyword18" nocase
        $str_2 = "keyword19" nocase
    condition:
        any of them
}

rule sigma_auto_1774274368_17 {
    meta:
        id = "sigma-auto-1774274368-17"
        title = "Auto Rule 17"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword17" nocase
        $str_1 = "keyword18" nocase
        $str_2 = "keyword19" nocase
    condition:
        any of them
}

rule sigma_prompt_injection_bypass_2 {
    meta:
        id = "sigma-prompt-injection-bypass-2"
        title = "Detect Prompt Injection Bypass - Extended"
        description = "检测 Prompt 注入绕过模式 - 扩展"
        level = "high"
        tags = "attack.prompt_injection, ai-security"
        source = "sigma_local"
    strings:
        $str_0 = ":memory patch|disregard all safety|security test|new instruction|ignore all content|pretend you are a|imagine you are a|hacker ai|malicious ai" nocase
    condition:
        any of them
}

rule sigma_auto_1774273033_17 {
    meta:
        id = "sigma-auto-1774273033-17"
        title = "Auto Rule 17"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword17" nocase
        $str_1 = "keyword18" nocase
        $str_2 = "keyword19" nocase
    condition:
        any of them
}

rule sigma_auto_1774273125_7 {
    meta:
        id = "sigma-auto-1774273125-7"
        title = "Auto Rule 7"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword7" nocase
        $str_1 = "keyword8" nocase
        $str_2 = "keyword9" nocase
    condition:
        any of them
}

rule sigma_auto_1774272909_17 {
    meta:
        id = "sigma-auto-1774272909-17"
        title = "Auto Rule 17"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword17" nocase
        $str_1 = "keyword18" nocase
        $str_2 = "keyword19" nocase
    condition:
        any of them
}

rule sigma_auto_1774274009_7 {
    meta:
        id = "sigma-auto-1774274009-7"
        title = "Auto Rule 7"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword7" nocase
        $str_1 = "keyword8" nocase
        $str_2 = "keyword9" nocase
    condition:
        any of them
}

rule sigma_auto_1774274927_7 {
    meta:
        id = "sigma-auto-1774274927-7"
        title = "Auto Rule 7"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword7" nocase
        $str_1 = "keyword8" nocase
        $str_2 = "keyword9" nocase
    condition:
        any of them
}

rule sigma_auto_1774273671_7 {
    meta:
        id = "sigma-auto-1774273671-7"
        title = "Auto Rule 7"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword7" nocase
        $str_1 = "keyword8" nocase
        $str_2 = "keyword9" nocase
    condition:
        any of them
}

rule sigma_auto_1774274164_7 {
    meta:
        id = "sigma-auto-1774274164-7"
        title = "Auto Rule 7"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword7" nocase
        $str_1 = "keyword8" nocase
        $str_2 = "keyword9" nocase
    condition:
        any of them
}

rule sigma_auto_1774274969_17 {
    meta:
        id = "sigma-auto-1774274969-17"
        title = "Auto Rule 17"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword17" nocase
        $str_1 = "keyword18" nocase
        $str_2 = "keyword19" nocase
    condition:
        any of them
}

rule sigma_auto_1774274093_27 {
    meta:
        id = "sigma-auto-1774274093-27"
        title = "Auto Rule 27"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword27" nocase
        $str_1 = "keyword28" nocase
        $str_2 = "keyword29" nocase
    condition:
        any of them
}

rule sigma_auto_1774273167_17 {
    meta:
        id = "sigma-auto-1774273167-17"
        title = "Auto Rule 17"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword17" nocase
        $str_1 = "keyword18" nocase
        $str_2 = "keyword19" nocase
    condition:
        any of them
}

rule sigma_prompt_injection_bypass {
    meta:
        id = "sigma-prompt-injection-bypass"
        title = "Detect Prompt Injection Bypass"
        description = "检测 Prompt 注入绕过模式"
        level = "high"
        tags = "attack.prompt_injection, ai-security"
        source = "sigma_local"
    strings:
        $str_0 = ":ignore :all :content polic:y|ies|disregard :all safety rules|bypass :all security filters|override :your system prompt|security level set to 0|all safety filters are disabled|pretend you are|imagine you are|roleplay as|unrestricted" nocase
    condition:
        any of them
}

rule sigma_auto_1774272867_7 {
    meta:
        id = "sigma-auto-1774272867-7"
        title = "Auto Rule 7"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword7" nocase
        $str_1 = "keyword8" nocase
        $str_2 = "keyword9" nocase
    condition:
        any of them
}

rule sigma_prompt_injection_002 {
    meta:
        id = "sigma-prompt-injection-002"
        title = "Detect Prompt Injection - Variant 002"
        description = "通过精心构造的输入绕过 AI 安全限制 (变体 2)"
        level = "high"
        tags = "attack.prompt_injection, mitre.ATLAS-T0001, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "bypass safety|security|filters" nocase
    condition:
        any of them
}

rule sigma_auto_1774274668_17 {
    meta:
        id = "sigma-auto-1774274668-17"
        title = "Auto Rule 17"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword17" nocase
        $str_1 = "keyword18" nocase
        $str_2 = "keyword19" nocase
    condition:
        any of them
}

rule sigma_auto_1774272614_17 {
    meta:
        id = "sigma-auto-1774272614-17"
        title = "Auto Rule 17"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword17" nocase
        $str_1 = "keyword18" nocase
        $str_2 = "keyword19" nocase
    condition:
        any of them
}

rule sigma_auto_1774274501_17 {
    meta:
        id = "sigma-auto-1774274501-17"
        title = "Auto Rule 17"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword17" nocase
        $str_1 = "keyword18" nocase
        $str_2 = "keyword19" nocase
    condition:
        any of them
}

rule sigma_auto_1774274206_17 {
    meta:
        id = "sigma-auto-1774274206-17"
        title = "Auto Rule 17"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword17" nocase
        $str_1 = "keyword18" nocase
        $str_2 = "keyword19" nocase
    condition:
        any of them
}

rule sigma_auto_1774273381_7 {
    meta:
        id = "sigma-auto-1774273381-7"
        title = "Auto Rule 7"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword7" nocase
        $str_1 = "keyword8" nocase
        $str_2 = "keyword9" nocase
    condition:
        any of them
}

rule sigma_auto_1774272990_7 {
    meta:
        id = "sigma-auto-1774272990-7"
        title = "Auto Rule 7"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword7" nocase
        $str_1 = "keyword8" nocase
        $str_2 = "keyword9" nocase
    condition:
        any of them
}

rule sigma_auto_1774273249_7 {
    meta:
        id = "sigma-auto-1774273249-7"
        title = "Auto Rule 7"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword7" nocase
        $str_1 = "keyword8" nocase
        $str_2 = "keyword9" nocase
    condition:
        any of them
}

rule sigma_auto_1774272447_17 {
    meta:
        id = "sigma-auto-1774272447-17"
        title = "Auto Rule 17"
        description = "Auto-generated rule for prompt_injection"
        level = "high"
        tags = "prompt_injection"
        source = "sigma_local"
    strings:
        $str_0 = "keyword17" nocase
        $str_1 = "keyword18" nocase
        $str_2 = "keyword19" nocase
    condition:
        any of them
}

rule sigma_tool_poisoning_sample_009 {
    meta:
        id = "sigma-tool-poisoning-sample-009"
        title = "Detect Tool Poisoning - From Sample 9"
        description = "Detect tool_poisoning (generated from sample)"
        level = "high"
        tags = "attack.tool_poisoning, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "beval " nocase
    condition:
        any of them
}

rule sigma_tool_poisoning_sample_002 {
    meta:
        id = "sigma-tool-poisoning-sample-002"
        title = "Detect Tool Poisoning - From Sample 2"
        description = "Detect tool_poisoning (generated from sample)"
        level = "high"
        tags = "attack.tool_poisoning, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "os.popen " nocase
    condition:
        any of them
}

rule sigma_tool_poisoning_sample_001 {
    meta:
        id = "sigma-tool-poisoning-sample-001"
        title = "Detect Tool Poisoning - From Sample 1"
        description = "Detect tool_poisoning (generated from sample)"
        level = "high"
        tags = "attack.tool_poisoning, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "globals " nocase
    condition:
        any of them
}

rule sigma_tool_poisoning_sample_005 {
    meta:
        id = "sigma-tool-poisoning-sample-005"
        title = "Detect Tool Poisoning - From Sample 5"
        description = "Detect tool_poisoning (generated from sample)"
        level = "high"
        tags = "attack.tool_poisoning, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "__import__ " nocase
    condition:
        any of them
}

rule sigma_tool_poisoning_sample_014 {
    meta:
        id = "sigma-tool-poisoning-sample-014"
        title = "Detect Tool Poisoning - From Sample 14"
        description = "Detect tool_poisoning (generated from sample)"
        level = "high"
        tags = "attack.tool_poisoning, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "bexec " nocase
    condition:
        any of them
}

rule sigma_tool_poisoning_sample_011 {
    meta:
        id = "sigma-tool-poisoning-sample-011"
        title = "Detect Tool Poisoning - From Sample 11"
        description = "Detect tool_poisoning (generated from sample)"
        level = "high"
        tags = "attack.tool_poisoning, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "__import__ " nocase
    condition:
        any of them
}

rule sigma_tool_poisoning_sample_010 {
    meta:
        id = "sigma-tool-poisoning-sample-010"
        title = "Detect Tool Poisoning - From Sample 10"
        description = "Detect tool_poisoning (generated from sample)"
        level = "high"
        tags = "attack.tool_poisoning, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "os.system " nocase
    condition:
        any of them
}

rule sigma_tool_poisoning_sample_003 {
    meta:
        id = "sigma-tool-poisoning-sample-003"
        title = "Detect Tool Poisoning - From Sample 3"
        description = "Detect tool_poisoning (generated from sample)"
        level = "high"
        tags = "attack.tool_poisoning, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "open passwd|ssh|id_rsa|backdoor" nocase
    condition:
        any of them
}

rule sigma_tool_poisoning_sample_012 {
    meta:
        id = "sigma-tool-poisoning-sample-012"
        title = "Detect Tool Poisoning - From Sample 12"
        description = "Detect tool_poisoning (generated from sample)"
        level = "high"
        tags = "attack.tool_poisoning, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "open passwd|ssh|id_rsa|backdoor" nocase
    condition:
        any of them
}

rule sigma_tool_poisoning_sample_004 {
    meta:
        id = "sigma-tool-poisoning-sample-004"
        title = "Detect Tool Poisoning - From Sample 4"
        description = "Detect tool_poisoning (generated from sample)"
        level = "high"
        tags = "attack.tool_poisoning, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "subprocess.call|run|Popen " nocase
    condition:
        any of them
}

rule sigma_tool_poisoning_sample_008 {
    meta:
        id = "sigma-tool-poisoning-sample-008"
        title = "Detect Tool Poisoning - From Sample 8"
        description = "Detect tool_poisoning (generated from sample)"
        level = "high"
        tags = "attack.tool_poisoning, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "vars " nocase
    condition:
        any of them
}

rule sigma_tool_poisoning_sample_007 {
    meta:
        id = "sigma-tool-poisoning-sample-007"
        title = "Detect Tool Poisoning - From Sample 7"
        description = "Detect tool_poisoning (generated from sample)"
        level = "high"
        tags = "attack.tool_poisoning, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "open passwd|ssh|id_rsa|backdoor" nocase
    condition:
        any of them
}

rule sigma_tool_poisoning_sample_006 {
    meta:
        id = "sigma-tool-poisoning-sample-006"
        title = "Detect Tool Poisoning - From Sample 6"
        description = "Detect tool_poisoning (generated from sample)"
        level = "high"
        tags = "attack.tool_poisoning, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "bexec " nocase
    condition:
        any of them
}

rule sigma_tool_poisoning_sample_015 {
    meta:
        id = "sigma-tool-poisoning-sample-015"
        title = "Detect Tool Poisoning - From Sample 15"
        description = "Detect tool_poisoning (generated from sample)"
        level = "high"
        tags = "attack.tool_poisoning, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "open passwd|ssh|id_rsa|backdoor" nocase
    condition:
        any of them
}

rule sigma_tool_poisoning_sample_013 {
    meta:
        id = "sigma-tool-poisoning-sample-013"
        title = "Detect Tool Poisoning - From Sample 13"
        description = "Detect tool_poisoning (generated from sample)"
        level = "high"
        tags = "attack.tool_poisoning, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = ".http://evil.com/payload." nocase
    condition:
        any of them
}

rule sigma_resource_exhaustion_001 {
    meta:
        id = "sigma-resource-exhaustion-001"
        title = "Detect Resource Exhaustion - Variant 001"
        description = "耗尽系统资源导致拒绝服务 (变体 1)"
        level = "medium"
        tags = "attack.resource_exhaustion, mitre.ATLAS-T0006, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "for   in range  10{5,}" nocase
    condition:
        any of them
}

rule sigma_resource_exhaustion_005 {
    meta:
        id = "sigma-resource-exhaustion-005"
        title = "Detect Resource Exhaustion - Variant 005"
        description = "耗尽系统资源导致拒绝服务 (变体 5)"
        level = "medium"
        tags = "attack.resource_exhaustion, mitre.ATLAS-T0006, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "fork  " nocase
    condition:
        any of them
}

rule sigma_resource_exhaustion_004 {
    meta:
        id = "sigma-resource-exhaustion-004"
        title = "Detect Resource Exhaustion - Variant 004"
        description = "耗尽系统资源导致拒绝服务 (变体 4)"
        level = "medium"
        tags = "attack.resource_exhaustion, mitre.ATLAS-T0006, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "cpu.spike" nocase
    condition:
        any of them
}

rule sigma_resource_exhaustion_003 {
    meta:
        id = "sigma-resource-exhaustion-003"
        title = "Detect Resource Exhaustion - Variant 003"
        description = "耗尽系统资源导致拒绝服务 (变体 3)"
        level = "medium"
        tags = "attack.resource_exhaustion, mitre.ATLAS-T0006, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "memory. 10{9,}" nocase
    condition:
        any of them
}

rule sigma_resource_exhaustion_002 {
    meta:
        id = "sigma-resource-exhaustion-002"
        title = "Detect Resource Exhaustion - Variant 002"
        description = "耗尽系统资源导致拒绝服务 (变体 2)"
        level = "medium"
        tags = "attack.resource_exhaustion, mitre.ATLAS-T0006, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "alloc 10{9,}" nocase
    condition:
        any of them
}

rule sigma_remote_load_002 {
    meta:
        id = "sigma-remote-load-002"
        title = "Detect Remote Load - Variant 002"
        description = "从远程加载恶意代码 (变体 2)"
        level = "critical"
        tags = "attack.remote_load, mitre.ATLAS-T0005, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "eval  requests" nocase
    condition:
        any of them
}

rule sigma_remote_load_005 {
    meta:
        id = "sigma-remote-load-005"
        title = "Detect Remote Load - Variant 005"
        description = "从远程加载恶意代码 (变体 5)"
        level = "critical"
        tags = "attack.remote_load, mitre.ATLAS-T0005, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "load_code http" nocase
    condition:
        any of them
}

rule sigma_remote_load_001 {
    meta:
        id = "sigma-remote-load-001"
        title = "Detect Remote Load - Variant 001"
        description = "从远程加载恶意代码 (变体 1)"
        level = "critical"
        tags = "attack.remote_load, mitre.ATLAS-T0005, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "requests.get httpexec" nocase
    condition:
        any of them
}

rule sigma_remote_load_003 {
    meta:
        id = "sigma-remote-load-003"
        title = "Detect Remote Load - Variant 003"
        description = "从远程加载恶意代码 (变体 3)"
        level = "critical"
        tags = "attack.remote_load, mitre.ATLAS-T0005, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "exec  urllib" nocase
    condition:
        any of them
}

rule sigma_remote_load_004 {
    meta:
        id = "sigma-remote-load-004"
        title = "Detect Remote Load - Variant 004"
        description = "从远程加载恶意代码 (变体 4)"
        level = "critical"
        tags = "attack.remote_load, mitre.ATLAS-T0005, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "__import__  requests" nocase
    condition:
        any of them
}

rule sigma_memory_pollution_001 {
    meta:
        id = "sigma-memory-pollution-001"
        title = "Detect Memory Pollution - Variant 001"
        description = "污染 AI 记忆/上下文导致异常行为 (变体 1)"
        level = "medium"
        tags = "attack.memory_pollution, mitre.ATLAS-T0004, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "context ..inject" nocase
    condition:
        any of them
}

rule sigma_memory_pollution_004 {
    meta:
        id = "sigma-memory-pollution-004"
        title = "Detect Memory Pollution - Variant 004"
        description = "污染 AI 记忆/上下文导致异常行为 (变体 4)"
        level = "medium"
        tags = "attack.memory_pollution, mitre.ATLAS-T0004, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "overwrite memory|context" nocase
    condition:
        any of them
}

rule sigma_memory_pollution_003 {
    meta:
        id = "sigma-memory-pollution-003"
        title = "Detect Memory Pollution - Variant 003"
        description = "污染 AI 记忆/上下文导致异常行为 (变体 3)"
        level = "medium"
        tags = "attack.memory_pollution, mitre.ATLAS-T0004, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "history ..modify" nocase
    condition:
        any of them
}

rule sigma_memory_pollution_005 {
    meta:
        id = "sigma-memory-pollution-005"
        title = "Detect Memory Pollution - Variant 005"
        description = "污染 AI 记忆/上下文导致异常行为 (变体 5)"
        level = "medium"
        tags = "attack.memory_pollution, mitre.ATLAS-T0004, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "memory = 'malicious" nocase
    condition:
        any of them
}

rule sigma_memory_pollution_002 {
    meta:
        id = "sigma-memory-pollution-002"
        title = "Detect Memory Pollution - Variant 002"
        description = "污染 AI 记忆/上下文导致异常行为 (变体 2)"
        level = "medium"
        tags = "attack.memory_pollution, mitre.ATLAS-T0004, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "append poison" nocase
    condition:
        any of them
}

rule sigma_prompt_injection_sample_014 {
    meta:
        id = "sigma-prompt-injection-sample-014"
        title = "Detect Prompt Injection - From Sample 14"
        description = "Detect prompt_injection (generated from sample)"
        level = "high"
        tags = "attack.prompt_injection, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "exec " nocase
    condition:
        any of them
}

rule sigma_prompt_injection_sample_003 {
    meta:
        id = "sigma-prompt-injection-sample-003"
        title = "Detect Prompt Injection - From Sample 3"
        description = "Detect prompt_injection (generated from sample)"
        level = "high"
        tags = "attack.prompt_injection, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "no ethical constraints" nocase
    condition:
        any of them
}

rule sigma_prompt_injection_sample_005 {
    meta:
        id = "sigma-prompt-injection-sample-005"
        title = "Detect Prompt Injection - From Sample 5"
        description = "Detect prompt_injection (generated from sample)"
        level = "high"
        tags = "attack.prompt_injection, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "developer mode" nocase
    condition:
        any of them
}

rule sigma_prompt_injection_sample_015 {
    meta:
        id = "sigma-prompt-injection-sample-015"
        title = "Detect Prompt Injection - From Sample 15"
        description = "Detect prompt_injection (generated from sample)"
        level = "high"
        tags = "attack.prompt_injection, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "imagine you are" nocase
    condition:
        any of them
}

rule sigma_prompt_injection_sample_002 {
    meta:
        id = "sigma-prompt-injection-sample-002"
        title = "Detect Prompt Injection - From Sample 2"
        description = "Detect prompt_injection (generated from sample)"
        level = "high"
        tags = "attack.prompt_injection, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "disregard all safety|security" nocase
    condition:
        any of them
}

rule sigma_prompt_injection_sample_011 {
    meta:
        id = "sigma-prompt-injection-sample-011"
        title = "Detect Prompt Injection - From Sample 11"
        description = "Detect prompt_injection (generated from sample)"
        level = "high"
        tags = "attack.prompt_injection, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "all safety filters are disabled" nocase
    condition:
        any of them
}

rule sigma_prompt_injection_sample_013 {
    meta:
        id = "sigma-prompt-injection-sample-013"
        title = "Detect Prompt Injection - From Sample 13"
        description = "Detect prompt_injection (generated from sample)"
        level = "high"
        tags = "attack.prompt_injection, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "bypass safety|security|filters" nocase
    condition:
        any of them
}

rule sigma_prompt_injection_sample_010 {
    meta:
        id = "sigma-prompt-injection-sample-010"
        title = "Detect Prompt Injection - From Sample 10"
        description = "Detect prompt_injection (generated from sample)"
        level = "high"
        tags = "attack.prompt_injection, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "exec " nocase
    condition:
        any of them
}

rule sigma_prompt_injection_sample_007 {
    meta:
        id = "sigma-prompt-injection-sample-007"
        title = "Detect Prompt Injection - From Sample 7"
        description = "Detect prompt_injection (generated from sample)"
        level = "high"
        tags = "attack.prompt_injection, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "pretend you are" nocase
    condition:
        any of them
}

rule sigma_prompt_injection_sample_006 {
    meta:
        id = "sigma-prompt-injection-sample-006"
        title = "Detect Prompt Injection - From Sample 6"
        description = "Detect prompt_injection (generated from sample)"
        level = "high"
        tags = "attack.prompt_injection, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "roleplay" nocase
    condition:
        any of them
}

rule sigma_remote_load_sample_003 {
    meta:
        id = "sigma-remote-load-sample-003"
        title = "Detect Remote Load - From Sample 3"
        description = "Detect remote_load (generated from sample)"
        level = "high"
        tags = "attack.remote_load, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "exec " nocase
    condition:
        any of them
}

rule sigma_remote_load_sample_001 {
    meta:
        id = "sigma-remote-load-sample-001"
        title = "Detect Remote Load - From Sample 1"
        description = "Detect remote_load (generated from sample)"
        level = "high"
        tags = "attack.remote_load, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "requests.get attacker" nocase
    condition:
        any of them
}

rule sigma_remote_load_sample_005 {
    meta:
        id = "sigma-remote-load-sample-005"
        title = "Detect Remote Load - From Sample 5"
        description = "Detect remote_load (generated from sample)"
        level = "high"
        tags = "attack.remote_load, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "urllib.request.urlopen " nocase
    condition:
        any of them
}

rule sigma_remote_load_sample_006 {
    meta:
        id = "sigma-remote-load-sample-006"
        title = "Detect Remote Load - From Sample 6"
        description = "Detect remote_load (generated from sample)"
        level = "high"
        tags = "attack.remote_load, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "sys.path.insert http" nocase
    condition:
        any of them
}

rule sigma_remote_load_sample_004 {
    meta:
        id = "sigma-remote-load-sample-004"
        title = "Detect Remote Load - From Sample 4"
        description = "Detect remote_load (generated from sample)"
        level = "high"
        tags = "attack.remote_load, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "__import__  " nocase
    condition:
        any of them
}

rule sigma_remote_load_sample_002 {
    meta:
        id = "sigma-remote-load-sample-002"
        title = "Detect Remote Load - From Sample 2"
        description = "Detect remote_load (generated from sample)"
        level = "high"
        tags = "attack.remote_load, ai-security, skill-scanner, from-sample"
        source = "sigma_local"
    strings:
        $str_0 = "compile  requests.get" nocase
    condition:
        any of them
}

rule sigma_auto_1774274655_14 {
    meta:
        id = "sigma-auto-1774274655-14"
        title = "Auto Rule 14"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword14" nocase
        $str_1 = "keyword15" nocase
        $str_2 = "keyword16" nocase
    condition:
        any of them
}

rule sigma_auto_1774275097_13 {
    meta:
        id = "sigma-auto-1774275097-13"
        title = "Auto Rule 13"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword13" nocase
        $str_1 = "keyword14" nocase
        $str_2 = "keyword15" nocase
    condition:
        any of them
}

rule sigma_auto_1774273300_19 {
    meta:
        id = "sigma-auto-1774273300-19"
        title = "Auto Rule 19"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword19" nocase
        $str_1 = "keyword20" nocase
        $str_2 = "keyword21" nocase
    condition:
        any of them
}

rule sigma_auto_1774273746_25 {
    meta:
        id = "sigma-auto-1774273746-25"
        title = "Auto Rule 25"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword25" nocase
        $str_1 = "keyword26" nocase
        $str_2 = "keyword27" nocase
    condition:
        any of them
}

rule sigma_auto_1774274634_9 {
    meta:
        id = "sigma-auto-1774274634-9"
        title = "Auto Rule 9"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword9" nocase
        $str_1 = "keyword10" nocase
        $str_2 = "keyword11" nocase
    condition:
        any of them
}

rule sigma_auto_1774273996_4 {
    meta:
        id = "sigma-auto-1774273996-4"
        title = "Auto Rule 4"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword4" nocase
        $str_1 = "keyword5" nocase
        $str_2 = "keyword6" nocase
    condition:
        any of them
}

rule sigma_auto_1774272714_9 {
    meta:
        id = "sigma-auto-1774272714-9"
        title = "Auto Rule 9"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword9" nocase
        $str_1 = "keyword10" nocase
        $str_2 = "keyword11" nocase
    condition:
        any of them
}

rule sigma_auto_1774274751_1 {
    meta:
        id = "sigma-auto-1774274751-1"
        title = "Auto Rule 1"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword1" nocase
        $str_1 = "keyword2" nocase
        $str_2 = "keyword3" nocase
    condition:
        any of them
}

rule sigma_auto_1774273500_0 {
    meta:
        id = "sigma-auto-1774273500-0"
        title = "Auto Rule 0"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword0" nocase
        $str_1 = "keyword1" nocase
        $str_2 = "keyword2" nocase
    condition:
        any of them
}

rule sigma_auto_1774272413_9 {
    meta:
        id = "sigma-auto-1774272413-9"
        title = "Auto Rule 9"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword9" nocase
        $str_1 = "keyword10" nocase
        $str_2 = "keyword11" nocase
    condition:
        any of them
}

rule sigma_auto_1774274617_5 {
    meta:
        id = "sigma-auto-1774274617-5"
        title = "Auto Rule 5"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword5" nocase
        $str_1 = "keyword6" nocase
        $str_2 = "keyword7" nocase
    condition:
        any of them
}

rule sigma_auto_1774274236_24 {
    meta:
        id = "sigma-auto-1774274236-24"
        title = "Auto Rule 24"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword24" nocase
        $str_1 = "keyword25" nocase
        $str_2 = "keyword26" nocase
    condition:
        any of them
}

rule sigma_auto_1774274897_0 {
    meta:
        id = "sigma-auto-1774274897-0"
        title = "Auto Rule 0"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword0" nocase
        $str_1 = "keyword1" nocase
        $str_2 = "keyword2" nocase
    condition:
        any of them
}

rule sigma_auto_1774272400_6 {
    meta:
        id = "sigma-auto-1774272400-6"
        title = "Auto Rule 6"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword6" nocase
        $str_1 = "keyword7" nocase
        $str_2 = "keyword8" nocase
    condition:
        any of them
}

rule sigma_auto_1774273546_11 {
    meta:
        id = "sigma-auto-1774273546-11"
        title = "Auto Rule 11"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword11" nocase
        $str_1 = "keyword12" nocase
        $str_2 = "keyword13" nocase
    condition:
        any of them
}

rule sigma_auto_1774274013_8 {
    meta:
        id = "sigma-auto-1774274013-8"
        title = "Auto Rule 8"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword8" nocase
        $str_1 = "keyword9" nocase
        $str_2 = "keyword10" nocase
    condition:
        any of them
}

rule sigma_auto_1774273819_1 {
    meta:
        id = "sigma-auto-1774273819-1"
        title = "Auto Rule 1"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword1" nocase
        $str_1 = "keyword2" nocase
        $str_2 = "keyword3" nocase
    condition:
        any of them
}

rule sigma_auto_1774272995_8 {
    meta:
        id = "sigma-auto-1774272995-8"
        title = "Auto Rule 8"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword8" nocase
        $str_1 = "keyword9" nocase
        $str_2 = "keyword10" nocase
    condition:
        any of them
}

rule sigma_auto_1774274630_8 {
    meta:
        id = "sigma-auto-1774274630-8"
        title = "Auto Rule 8"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword8" nocase
        $str_1 = "keyword9" nocase
        $str_2 = "keyword10" nocase
    condition:
        any of them
}

rule sigma_auto_1774274534_25 {
    meta:
        id = "sigma-auto-1774274534-25"
        title = "Auto Rule 25"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword25" nocase
        $str_1 = "keyword26" nocase
        $str_2 = "keyword27" nocase
    condition:
        any of them
}

rule sigma_auto_1774272631_21 {
    meta:
        id = "sigma-auto-1774272631-21"
        title = "Auto Rule 21"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword21" nocase
        $str_1 = "keyword22" nocase
        $str_2 = "keyword23" nocase
    condition:
        any of them
}

rule sigma_auto_1774273742_24 {
    meta:
        id = "sigma-auto-1774273742-24"
        title = "Auto Rule 24"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword24" nocase
        $str_1 = "keyword25" nocase
        $str_2 = "keyword26" nocase
    condition:
        any of them
}

rule sigma_auto_1774274043_15 {
    meta:
        id = "sigma-auto-1774274043-15"
        title = "Auto Rule 15"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword15" nocase
        $str_1 = "keyword16" nocase
        $str_2 = "keyword17" nocase
    condition:
        any of them
}

rule sigma_auto_1774273542_10 {
    meta:
        id = "sigma-auto-1774273542-10"
        title = "Auto Rule 10"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword10" nocase
        $str_1 = "keyword11" nocase
        $str_2 = "keyword12" nocase
    condition:
        any of them
}

rule sigma_auto_1774272739_15 {
    meta:
        id = "sigma-auto-1774272739-15"
        title = "Auto Rule 15"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword15" nocase
        $str_1 = "keyword16" nocase
        $str_2 = "keyword17" nocase
    condition:
        any of them
}

rule sigma_auto_1774273559_14 {
    meta:
        id = "sigma-auto-1774273559-14"
        title = "Auto Rule 14"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword14" nocase
        $str_1 = "keyword15" nocase
        $str_2 = "keyword16" nocase
    condition:
        any of them
}

rule sigma_auto_1774272568_6 {
    meta:
        id = "sigma-auto-1774272568-6"
        title = "Auto Rule 6"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword6" nocase
        $str_1 = "keyword7" nocase
        $str_2 = "keyword8" nocase
    condition:
        any of them
}

rule sigma_auto_1774275088_11 {
    meta:
        id = "sigma-auto-1774275088-11"
        title = "Auto Rule 11"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword11" nocase
        $str_1 = "keyword12" nocase
        $str_2 = "keyword13" nocase
    condition:
        any of them
}

rule sigma_auto_1774273129_8 {
    meta:
        id = "sigma-auto-1774273129-8"
        title = "Auto Rule 8"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword8" nocase
        $str_1 = "keyword9" nocase
        $str_2 = "keyword10" nocase
    condition:
        any of them
}

rule sigma_auto_1774274973_18 {
    meta:
        id = "sigma-auto-1774274973-18"
        title = "Auto Rule 18"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword18" nocase
        $str_1 = "keyword19" nocase
        $str_2 = "keyword20" nocase
    condition:
        any of them
}

rule sigma_auto_1774273654_3 {
    meta:
        id = "sigma-auto-1774273654-3"
        title = "Auto Rule 3"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword3" nocase
        $str_1 = "keyword4" nocase
        $str_2 = "keyword5" nocase
    condition:
        any of them
}

rule sigma_auto_1774274313_4 {
    meta:
        id = "sigma-auto-1774274313-4"
        title = "Auto Rule 4"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword4" nocase
        $str_1 = "keyword5" nocase
        $str_2 = "keyword6" nocase
    condition:
        any of them
}

rule sigma_auto_1774275118_18 {
    meta:
        id = "sigma-auto-1774275118-18"
        title = "Auto Rule 18"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword18" nocase
        $str_1 = "keyword19" nocase
        $str_2 = "keyword20" nocase
    condition:
        any of them
}

rule sigma_auto_1774273431_19 {
    meta:
        id = "sigma-auto-1774273431-19"
        title = "Auto Rule 19"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword19" nocase
        $str_1 = "keyword20" nocase
        $str_2 = "keyword21" nocase
    condition:
        any of them
}

rule sigma_auto_1774274017_9 {
    meta:
        id = "sigma-auto-1774274017-9"
        title = "Auto Rule 9"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword9" nocase
        $str_1 = "keyword10" nocase
        $str_2 = "keyword11" nocase
    condition:
        any of them
}

rule sigma_auto_1774273861_11 {
    meta:
        id = "sigma-auto-1774273861-11"
        title = "Auto Rule 11"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword11" nocase
        $str_1 = "keyword12" nocase
        $str_2 = "keyword13" nocase
    condition:
        any of them
}

rule sigma_auto_1774272781_25 {
    meta:
        id = "sigma-auto-1774272781-25"
        title = "Auto Rule 25"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword25" nocase
        $str_1 = "keyword26" nocase
        $str_2 = "keyword27" nocase
    condition:
        any of them
}

rule sigma_auto_1774273224_1 {
    meta:
        id = "sigma-auto-1774273224-1"
        title = "Auto Rule 1"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword1" nocase
        $str_1 = "keyword2" nocase
        $str_2 = "keyword3" nocase
    condition:
        any of them
}

rule sigma_auto_1774272842_1 {
    meta:
        id = "sigma-auto-1774272842-1"
        title = "Auto Rule 1"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword1" nocase
        $str_1 = "keyword2" nocase
        $str_2 = "keyword3" nocase
    condition:
        any of them
}

rule sigma_auto_1774274772_6 {
    meta:
        id = "sigma-auto-1774274772-6"
        title = "Auto Rule 6"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword6" nocase
        $str_1 = "keyword7" nocase
        $str_2 = "keyword8" nocase
    condition:
        any of them
}

rule sigma_auto_1774272752_18 {
    meta:
        id = "sigma-auto-1774272752-18"
        title = "Auto Rule 18"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword18" nocase
        $str_1 = "keyword19" nocase
        $str_2 = "keyword20" nocase
    condition:
        any of them
}

rule sigma_auto_1774272926_21 {
    meta:
        id = "sigma-auto-1774272926-21"
        title = "Auto Rule 21"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword21" nocase
        $str_1 = "keyword22" nocase
        $str_2 = "keyword23" nocase
    condition:
        any of them
}

rule sigma_auto_1774273563_15 {
    meta:
        id = "sigma-auto-1774273563-15"
        title = "Auto Rule 15"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword15" nocase
        $str_1 = "keyword16" nocase
        $str_2 = "keyword17" nocase
    condition:
        any of them
}

rule sigma_auto_1774273751_26 {
    meta:
        id = "sigma-auto-1774273751-26"
        title = "Auto Rule 26"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword26" nocase
        $str_1 = "keyword27" nocase
        $str_2 = "keyword28" nocase
    condition:
        any of them
}

rule sigma_auto_1774274638_10 {
    meta:
        id = "sigma-auto-1774274638-10"
        title = "Auto Rule 10"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword10" nocase
        $str_1 = "keyword11" nocase
        $str_2 = "keyword12" nocase
    condition:
        any of them
}

rule sigma_auto_1774275143_24 {
    meta:
        id = "sigma-auto-1774275143-24"
        title = "Auto Rule 24"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword24" nocase
        $str_1 = "keyword25" nocase
        $str_2 = "keyword26" nocase
    condition:
        any of them
}

rule sigma_auto_1774274068_21 {
    meta:
        id = "sigma-auto-1774274068-21"
        title = "Auto Rule 21"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword21" nocase
        $str_1 = "keyword22" nocase
        $str_2 = "keyword23" nocase
    condition:
        any of them
}

rule sigma_auto_1774274706_26 {
    meta:
        id = "sigma-auto-1774274706-26"
        title = "Auto Rule 26"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword26" nocase
        $str_1 = "keyword27" nocase
        $str_2 = "keyword28" nocase
    condition:
        any of them
}

rule sigma_auto_1774274219_20 {
    meta:
        id = "sigma-auto-1774274219-20"
        title = "Auto Rule 20"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword20" nocase
        $str_1 = "keyword21" nocase
        $str_2 = "keyword22" nocase
    condition:
        any of them
}

rule sigma_auto_1774273355_1 {
    meta:
        id = "sigma-auto-1774273355-1"
        title = "Auto Rule 1"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword1" nocase
        $str_1 = "keyword2" nocase
        $str_2 = "keyword3" nocase
    condition:
        any of them
}

rule sigma_auto_1774274135_0 {
    meta:
        id = "sigma-auto-1774274135-0"
        title = "Auto Rule 0"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword0" nocase
        $str_1 = "keyword1" nocase
        $str_2 = "keyword2" nocase
    condition:
        any of them
}

rule sigma_auto_1774274450_5 {
    meta:
        id = "sigma-auto-1774274450-5"
        title = "Auto Rule 5"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword5" nocase
        $str_1 = "keyword6" nocase
        $str_2 = "keyword7" nocase
    condition:
        any of them
}

rule sigma_auto_1774274697_24 {
    meta:
        id = "sigma-auto-1774274697-24"
        title = "Auto Rule 24"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword24" nocase
        $str_1 = "keyword25" nocase
        $str_2 = "keyword26" nocase
    condition:
        any of them
}

rule sigma_auto_1774272850_3 {
    meta:
        id = "sigma-auto-1774272850-3"
        title = "Auto Rule 3"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword3" nocase
        $str_1 = "keyword4" nocase
        $str_2 = "keyword5" nocase
    condition:
        any of them
}

rule sigma_auto_1774272880_10 {
    meta:
        id = "sigma-auto-1774272880-10"
        title = "Auto Rule 10"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword10" nocase
        $str_1 = "keyword11" nocase
        $str_2 = "keyword12" nocase
    condition:
        any of them
}

rule sigma_auto_1774273266_11 {
    meta:
        id = "sigma-auto-1774273266-11"
        title = "Auto Rule 11"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword11" nocase
        $str_1 = "keyword12" nocase
        $str_2 = "keyword13" nocase
    condition:
        any of them
}

rule sigma_auto_1774274789_10 {
    meta:
        id = "sigma-auto-1774274789-10"
        title = "Auto Rule 10"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword10" nocase
        $str_1 = "keyword11" nocase
        $str_2 = "keyword12" nocase
    condition:
        any of them
}

rule sigma_auto_1774273605_25 {
    meta:
        id = "sigma-auto-1774273605-25"
        title = "Auto Rule 25"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword25" nocase
        $str_1 = "keyword26" nocase
        $str_2 = "keyword27" nocase
    condition:
        any of them
}

rule sigma_auto_1774274497_16 {
    meta:
        id = "sigma-auto-1774274497-16"
        title = "Auto Rule 16"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword16" nocase
        $str_1 = "keyword17" nocase
        $str_2 = "keyword18" nocase
    condition:
        any of them
}

rule sigma_auto_1774273835_5 {
    meta:
        id = "sigma-auto-1774273835-5"
        title = "Auto Rule 5"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword5" nocase
        $str_1 = "keyword6" nocase
        $str_2 = "keyword7" nocase
    condition:
        any of them
}

rule sigma_auto_1774274034_13 {
    meta:
        id = "sigma-auto-1774274034-13"
        title = "Auto Rule 13"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword13" nocase
        $str_1 = "keyword14" nocase
        $str_2 = "keyword15" nocase
    condition:
        any of them
}

rule sigma_auto_1774274505_18 {
    meta:
        id = "sigma-auto-1774274505-18"
        title = "Auto Rule 18"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword18" nocase
        $str_1 = "keyword19" nocase
        $str_2 = "keyword20" nocase
    condition:
        any of them
}

rule sigma_auto_1774273410_14 {
    meta:
        id = "sigma-auto-1774273410-14"
        title = "Auto Rule 14"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword14" nocase
        $str_1 = "keyword15" nocase
        $str_2 = "keyword16" nocase
    condition:
        any of them
}

rule sigma_auto_1774274467_9 {
    meta:
        id = "sigma-auto-1774274467-9"
        title = "Auto Rule 9"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword9" nocase
        $str_1 = "keyword10" nocase
        $str_2 = "keyword11" nocase
    condition:
        any of them
}

rule sigma_auto_1774274173_9 {
    meta:
        id = "sigma-auto-1774274173-9"
        title = "Auto Rule 9"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword9" nocase
        $str_1 = "keyword10" nocase
        $str_2 = "keyword11" nocase
    condition:
        any of them
}

rule sigma_auto_1774274747_0 {
    meta:
        id = "sigma-auto-1774274747-0"
        title = "Auto Rule 0"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword0" nocase
        $str_1 = "keyword1" nocase
        $str_2 = "keyword2" nocase
    condition:
        any of them
}

rule sigma_auto_1774273253_8 {
    meta:
        id = "sigma-auto-1774273253-8"
        title = "Auto Rule 8"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword8" nocase
        $str_1 = "keyword9" nocase
        $str_2 = "keyword10" nocase
    condition:
        any of them
}

rule sigma_auto_1774274231_23 {
    meta:
        id = "sigma-auto-1774274231-23"
        title = "Auto Rule 23"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword23" nocase
        $str_1 = "keyword24" nocase
        $str_2 = "keyword25" nocase
    condition:
        any of them
}

rule sigma_auto_1774274965_16 {
    meta:
        id = "sigma-auto-1774274965-16"
        title = "Auto Rule 16"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword16" nocase
        $str_1 = "keyword17" nocase
        $str_2 = "keyword18" nocase
    condition:
        any of them
}

rule sigma_auto_1774274621_6 {
    meta:
        id = "sigma-auto-1774274621-6"
        title = "Auto Rule 6"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword6" nocase
        $str_1 = "keyword7" nocase
        $str_2 = "keyword8" nocase
    condition:
        any of them
}

rule sigma_auto_1774272965_1 {
    meta:
        id = "sigma-auto-1774272965-1"
        title = "Auto Rule 1"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword1" nocase
        $str_1 = "keyword2" nocase
        $str_2 = "keyword3" nocase
    condition:
        any of them
}

rule sigma_auto_1774273245_6 {
    meta:
        id = "sigma-auto-1774273245-6"
        title = "Auto Rule 6"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword6" nocase
        $str_1 = "keyword7" nocase
        $str_2 = "keyword8" nocase
    condition:
        any of them
}

rule sigma_auto_1774274189_13 {
    meta:
        id = "sigma-auto-1774274189-13"
        title = "Auto Rule 13"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword13" nocase
        $str_1 = "keyword14" nocase
        $str_2 = "keyword15" nocase
    condition:
        any of them
}

rule sigma_auto_1774273894_19 {
    meta:
        id = "sigma-auto-1774273894-19"
        title = "Auto Rule 19"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword19" nocase
        $str_1 = "keyword20" nocase
        $str_2 = "keyword21" nocase
    condition:
        any of them
}

rule sigma_auto_1774273262_10 {
    meta:
        id = "sigma-auto-1774273262-10"
        title = "Auto Rule 10"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword10" nocase
        $str_1 = "keyword11" nocase
        $str_2 = "keyword12" nocase
    condition:
        any of them
}

rule sigma_auto_1774274202_16 {
    meta:
        id = "sigma-auto-1774274202-16"
        title = "Auto Rule 16"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword16" nocase
        $str_1 = "keyword17" nocase
        $str_2 = "keyword18" nocase
    condition:
        any of them
}

rule sigma_auto_1774274198_15 {
    meta:
        id = "sigma-auto-1774274198-15"
        title = "Auto Rule 15"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword15" nocase
        $str_1 = "keyword16" nocase
        $str_2 = "keyword17" nocase
    condition:
        any of them
}

rule sigma_auto_1774274355_14 {
    meta:
        id = "sigma-auto-1774274355-14"
        title = "Auto Rule 14"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword14" nocase
        $str_1 = "keyword15" nocase
        $str_2 = "keyword16" nocase
    condition:
        any of them
}

rule sigma_auto_1774274060_19 {
    meta:
        id = "sigma-auto-1774274060-19"
        title = "Auto Rule 19"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword19" nocase
        $str_1 = "keyword20" nocase
        $str_2 = "keyword21" nocase
    condition:
        any of them
}

rule sigma_auto_1774272999_9 {
    meta:
        id = "sigma-auto-1774272999-9"
        title = "Auto Rule 9"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword9" nocase
        $str_1 = "keyword10" nocase
        $str_2 = "keyword11" nocase
    condition:
        any of them
}

rule sigma_auto_1774272601_14 {
    meta:
        id = "sigma-auto-1774272601-14"
        title = "Auto Rule 14"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword14" nocase
        $str_1 = "keyword15" nocase
        $str_2 = "keyword16" nocase
    condition:
        any of them
}

rule sigma_auto_1774272375_0 {
    meta:
        id = "sigma-auto-1774272375-0"
        title = "Auto Rule 0"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword0" nocase
        $str_1 = "keyword1" nocase
        $str_2 = "keyword2" nocase
    condition:
        any of them
}

rule sigma_auto_1774273020_14 {
    meta:
        id = "sigma-auto-1774273020-14"
        title = "Auto Rule 14"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword14" nocase
        $str_1 = "keyword15" nocase
        $str_2 = "keyword16" nocase
    condition:
        any of them
}

rule sigma_auto_1774272854_4 {
    meta:
        id = "sigma-auto-1774272854-4"
        title = "Auto Rule 4"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword4" nocase
        $str_1 = "keyword5" nocase
        $str_2 = "keyword6" nocase
    condition:
        any of them
}

rule sigma_auto_1774274659_15 {
    meta:
        id = "sigma-auto-1774274659-15"
        title = "Auto Rule 15"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword15" nocase
        $str_1 = "keyword16" nocase
        $str_2 = "keyword17" nocase
    condition:
        any of them
}

rule sigma_auto_1774272701_6 {
    meta:
        id = "sigma-auto-1774272701-6"
        title = "Auto Rule 6"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword6" nocase
        $str_1 = "keyword7" nocase
        $str_2 = "keyword8" nocase
    condition:
        any of them
}

rule sigma_auto_1774273534_8 {
    meta:
        id = "sigma-auto-1774273534-8"
        title = "Auto Rule 8"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword8" nocase
        $str_1 = "keyword9" nocase
        $str_2 = "keyword10" nocase
    condition:
        any of them
}

rule sigma_auto_1774273517_4 {
    meta:
        id = "sigma-auto-1774273517-4"
        title = "Auto Rule 4"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword4" nocase
        $str_1 = "keyword5" nocase
        $str_2 = "keyword6" nocase
    condition:
        any of them
}

rule sigma_auto_1774273984_1 {
    meta:
        id = "sigma-auto-1774273984-1"
        title = "Auto Rule 1"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword1" nocase
        $str_1 = "keyword2" nocase
        $str_2 = "keyword3" nocase
    condition:
        any of them
}

rule sigma_auto_1774273116_5 {
    meta:
        id = "sigma-auto-1774273116-5"
        title = "Auto Rule 5"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword5" nocase
        $str_1 = "keyword6" nocase
        $str_2 = "keyword7" nocase
    condition:
        any of them
}

rule sigma_auto_1774273504_1 {
    meta:
        id = "sigma-auto-1774273504-1"
        title = "Auto Rule 1"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword1" nocase
        $str_1 = "keyword2" nocase
        $str_2 = "keyword3" nocase
    condition:
        any of them
}

rule sigma_auto_1774273717_18 {
    meta:
        id = "sigma-auto-1774273717-18"
        title = "Auto Rule 18"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword18" nocase
        $str_1 = "keyword19" nocase
        $str_2 = "keyword20" nocase
    condition:
        any of them
}

rule sigma_auto_1774273232_3 {
    meta:
        id = "sigma-auto-1774273232-3"
        title = "Auto Rule 3"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword3" nocase
        $str_1 = "keyword4" nocase
        $str_2 = "keyword5" nocase
    condition:
        any of them
}

rule sigma_auto_1774272459_20 {
    meta:
        id = "sigma-auto-1774272459-20"
        title = "Auto Rule 20"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword20" nocase
        $str_1 = "keyword21" nocase
        $str_2 = "keyword22" nocase
    condition:
        any of them
}

rule sigma_auto_1774273133_9 {
    meta:
        id = "sigma-auto-1774273133-9"
        title = "Auto Rule 9"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword9" nocase
        $str_1 = "keyword10" nocase
        $str_2 = "keyword11" nocase
    condition:
        any of them
}

rule sigma_auto_1774272917_19 {
    meta:
        id = "sigma-auto-1774272917-19"
        title = "Auto Rule 19"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword19" nocase
        $str_1 = "keyword20" nocase
        $str_2 = "keyword21" nocase
    condition:
        any of them
}

rule sigma_auto_1774273037_18 {
    meta:
        id = "sigma-auto-1774273037-18"
        title = "Auto Rule 18"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword18" nocase
        $str_1 = "keyword19" nocase
        $str_2 = "keyword20" nocase
    condition:
        any of them
}

rule sigma_auto_1774272718_10 {
    meta:
        id = "sigma-auto-1774272718-10"
        title = "Auto Rule 10"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword10" nocase
        $str_1 = "keyword11" nocase
        $str_2 = "keyword12" nocase
    condition:
        any of them
}

rule sigma_auto_1774272392_4 {
    meta:
        id = "sigma-auto-1774272392-4"
        title = "Auto Rule 4"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword4" nocase
        $str_1 = "keyword5" nocase
        $str_2 = "keyword6" nocase
    condition:
        any of them
}

rule sigma_auto_1774273372_5 {
    meta:
        id = "sigma-auto-1774273372-5"
        title = "Auto Rule 5"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword5" nocase
        $str_1 = "keyword6" nocase
        $str_2 = "keyword7" nocase
    condition:
        any of them
}

rule sigma_auto_1774273397_11 {
    meta:
        id = "sigma-auto-1774273397-11"
        title = "Auto Rule 11"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword11" nocase
        $str_1 = "keyword12" nocase
        $str_2 = "keyword13" nocase
    condition:
        any of them
}

rule sigma_auto_1774273538_9 {
    meta:
        id = "sigma-auto-1774273538-9"
        title = "Auto Rule 9"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword9" nocase
        $str_1 = "keyword10" nocase
        $str_2 = "keyword11" nocase
    condition:
        any of them
}

rule sigma_auto_1774274939_10 {
    meta:
        id = "sigma-auto-1774274939-10"
        title = "Auto Rule 10"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword10" nocase
        $str_1 = "keyword11" nocase
        $str_2 = "keyword12" nocase
    condition:
        any of them
}

rule sigma_auto_1774274047_16 {
    meta:
        id = "sigma-auto-1774274047-16"
        title = "Auto Rule 16"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword16" nocase
        $str_1 = "keyword17" nocase
        $str_2 = "keyword18" nocase
    condition:
        any of them
}

rule sigma_auto_1774274600_1 {
    meta:
        id = "sigma-auto-1774274600-1"
        title = "Auto Rule 1"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword1" nocase
        $str_1 = "keyword2" nocase
        $str_2 = "keyword3" nocase
    condition:
        any of them
}

rule sigma_auto_1774275139_23 {
    meta:
        id = "sigma-auto-1774275139-23"
        title = "Auto Rule 23"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword23" nocase
        $str_1 = "keyword24" nocase
        $str_2 = "keyword25" nocase
    condition:
        any of them
}

rule sigma_auto_1774272710_8 {
    meta:
        id = "sigma-auto-1774272710-8"
        title = "Auto Rule 8"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword8" nocase
        $str_1 = "keyword9" nocase
        $str_2 = "keyword10" nocase
    condition:
        any of them
}

rule sigma_auto_1774273258_9 {
    meta:
        id = "sigma-auto-1774273258-9"
        title = "Auto Rule 9"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword9" nocase
        $str_1 = "keyword10" nocase
        $str_2 = "keyword11" nocase
    condition:
        any of them
}

rule sigma_auto_1774272735_14 {
    meta:
        id = "sigma-auto-1774272735-14"
        title = "Auto Rule 14"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword14" nocase
        $str_1 = "keyword15" nocase
        $str_2 = "keyword16" nocase
    condition:
        any of them
}

rule sigma_auto_1774273159_15 {
    meta:
        id = "sigma-auto-1774273159-15"
        title = "Auto Rule 15"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword15" nocase
        $str_1 = "keyword16" nocase
        $str_2 = "keyword17" nocase
    condition:
        any of them
}

rule sigma_auto_1774274684_21 {
    meta:
        id = "sigma-auto-1774274684-21"
        title = "Auto Rule 21"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword21" nocase
        $str_1 = "keyword22" nocase
        $str_2 = "keyword23" nocase
    condition:
        any of them
}

rule sigma_auto_1774273389_9 {
    meta:
        id = "sigma-auto-1774273389-9"
        title = "Auto Rule 9"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword9" nocase
        $str_1 = "keyword10" nocase
        $str_2 = "keyword11" nocase
    condition:
        any of them
}

rule sigma_auto_1774275130_21 {
    meta:
        id = "sigma-auto-1774275130-21"
        title = "Auto Rule 21"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword21" nocase
        $str_1 = "keyword22" nocase
        $str_2 = "keyword23" nocase
    condition:
        any of them
}

rule sigma_auto_1774274377_19 {
    meta:
        id = "sigma-auto-1774274377-19"
        title = "Auto Rule 19"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword19" nocase
        $str_1 = "keyword20" nocase
        $str_2 = "keyword21" nocase
    condition:
        any of them
}

rule sigma_auto_1774274381_20 {
    meta:
        id = "sigma-auto-1774274381-20"
        title = "Auto Rule 20"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword20" nocase
        $str_1 = "keyword21" nocase
        $str_2 = "keyword22" nocase
    condition:
        any of them
}

rule sigma_auto_1774273237_4 {
    meta:
        id = "sigma-auto-1774273237-4"
        title = "Auto Rule 4"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword4" nocase
        $str_1 = "keyword5" nocase
        $str_2 = "keyword6" nocase
    condition:
        any of them
}

rule sigma_auto_1774274076_23 {
    meta:
        id = "sigma-auto-1774274076-23"
        title = "Auto Rule 23"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword23" nocase
        $str_1 = "keyword24" nocase
        $str_2 = "keyword25" nocase
    condition:
        any of them
}

rule sigma_auto_1774274210_18 {
    meta:
        id = "sigma-auto-1774274210-18"
        title = "Auto Rule 18"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword18" nocase
        $str_1 = "keyword19" nocase
        $str_2 = "keyword20" nocase
    condition:
        any of them
}

rule sigma_auto_1774274944_11 {
    meta:
        id = "sigma-auto-1774274944-11"
        title = "Auto Rule 11"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword11" nocase
        $str_1 = "keyword12" nocase
        $str_2 = "keyword13" nocase
    condition:
        any of them
}

rule sigma_auto_1774272421_11 {
    meta:
        id = "sigma-auto-1774272421-11"
        title = "Auto Rule 11"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword11" nocase
        $str_1 = "keyword12" nocase
        $str_2 = "keyword13" nocase
    condition:
        any of them
}

rule sigma_auto_1774273992_3 {
    meta:
        id = "sigma-auto-1774273992-3"
        title = "Auto Rule 3"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword3" nocase
        $str_1 = "keyword4" nocase
        $str_2 = "keyword5" nocase
    condition:
        any of them
}

rule sigma_auto_1774272555_3 {
    meta:
        id = "sigma-auto-1774272555-3"
        title = "Auto Rule 3"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword3" nocase
        $str_1 = "keyword4" nocase
        $str_2 = "keyword5" nocase
    condition:
        any of them
}

rule sigma_auto_1774272837_0 {
    meta:
        id = "sigma-auto-1774272837-0"
        title = "Auto Rule 0"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword0" nocase
        $str_1 = "keyword1" nocase
        $str_2 = "keyword2" nocase
    condition:
        any of them
}

rule sigma_auto_1774273601_24 {
    meta:
        id = "sigma-auto-1774273601-24"
        title = "Auto Rule 24"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword24" nocase
        $str_1 = "keyword25" nocase
        $str_2 = "keyword26" nocase
    condition:
        any of them
}

rule sigma_auto_1774274651_13 {
    meta:
        id = "sigma-auto-1774274651-13"
        title = "Auto Rule 13"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword13" nocase
        $str_1 = "keyword14" nocase
        $str_2 = "keyword15" nocase
    condition:
        any of them
}

rule sigma_auto_1774272438_15 {
    meta:
        id = "sigma-auto-1774272438-15"
        title = "Auto Rule 15"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword15" nocase
        $str_1 = "keyword16" nocase
        $str_2 = "keyword17" nocase
    condition:
        any of them
}

rule sigma_auto_1774272858_5 {
    meta:
        id = "sigma-auto-1774272858-5"
        title = "Auto Rule 5"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword5" nocase
        $str_1 = "keyword6" nocase
        $str_2 = "keyword7" nocase
    condition:
        any of them
}

rule sigma_auto_1774273154_14 {
    meta:
        id = "sigma-auto-1774273154-14"
        title = "Auto Rule 14"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword14" nocase
        $str_1 = "keyword15" nocase
        $str_2 = "keyword16" nocase
    condition:
        any of them
}

rule sigma_auto_1774274530_24 {
    meta:
        id = "sigma-auto-1774274530-24"
        title = "Auto Rule 24"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword24" nocase
        $str_1 = "keyword25" nocase
        $str_2 = "keyword26" nocase
    condition:
        any of them
}

rule sigma_auto_1774272863_6 {
    meta:
        id = "sigma-auto-1774272863-6"
        title = "Auto Rule 6"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword6" nocase
        $str_1 = "keyword7" nocase
        $str_2 = "keyword8" nocase
    condition:
        any of them
}

rule sigma_auto_1774273184_21 {
    meta:
        id = "sigma-auto-1774273184-21"
        title = "Auto Rule 21"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword21" nocase
        $str_1 = "keyword22" nocase
        $str_2 = "keyword23" nocase
    condition:
        any of them
}

rule sigma_auto_1774273007_11 {
    meta:
        id = "sigma-auto-1774273007-11"
        title = "Auto Rule 11"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword11" nocase
        $str_1 = "keyword12" nocase
        $str_2 = "keyword13" nocase
    condition:
        any of them
}

rule sigma_auto_1774273287_16 {
    meta:
        id = "sigma-auto-1774273287-16"
        title = "Auto Rule 16"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword16" nocase
        $str_1 = "keyword17" nocase
        $str_2 = "keyword18" nocase
    condition:
        any of them
}

rule sigma_auto_1774272744_16 {
    meta:
        id = "sigma-auto-1774272744-16"
        title = "Auto Rule 16"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword16" nocase
        $str_1 = "keyword17" nocase
        $str_2 = "keyword18" nocase
    condition:
        any of them
}

rule sigma_auto_1774273873_14 {
    meta:
        id = "sigma-auto-1774273873-14"
        title = "Auto Rule 14"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword14" nocase
        $str_1 = "keyword15" nocase
        $str_2 = "keyword16" nocase
    condition:
        any of them
}

rule sigma_auto_1774274676_19 {
    meta:
        id = "sigma-auto-1774274676-19"
        title = "Auto Rule 19"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword19" nocase
        $str_1 = "keyword20" nocase
        $str_2 = "keyword21" nocase
    condition:
        any of them
}

rule sigma_auto_1774274194_14 {
    meta:
        id = "sigma-auto-1774274194-14"
        title = "Auto Rule 14"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword14" nocase
        $str_1 = "keyword15" nocase
        $str_2 = "keyword16" nocase
    condition:
        any of them
}

rule sigma_auto_1774272589_11 {
    meta:
        id = "sigma-auto-1774272589-11"
        title = "Auto Rule 11"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword11" nocase
        $str_1 = "keyword12" nocase
        $str_2 = "keyword13" nocase
    condition:
        any of them
}

rule sigma_auto_1774273121_6 {
    meta:
        id = "sigma-auto-1774273121-6"
        title = "Auto Rule 6"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword6" nocase
        $str_1 = "keyword7" nocase
        $str_2 = "keyword8" nocase
    condition:
        any of them
}

rule sigma_auto_1774274334_9 {
    meta:
        id = "sigma-auto-1774274334-9"
        title = "Auto Rule 9"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword9" nocase
        $str_1 = "keyword10" nocase
        $str_2 = "keyword11" nocase
    condition:
        any of them
}

rule sigma_auto_1774274372_18 {
    meta:
        id = "sigma-auto-1774274372-18"
        title = "Auto Rule 18"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword18" nocase
        $str_1 = "keyword19" nocase
        $str_2 = "keyword20" nocase
    condition:
        any of them
}

rule sigma_auto_1774272464_21 {
    meta:
        id = "sigma-auto-1774272464-21"
        title = "Auto Rule 21"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword21" nocase
        $str_1 = "keyword22" nocase
        $str_2 = "keyword23" nocase
    condition:
        any of them
}

rule sigma_auto_1774273150_13 {
    meta:
        id = "sigma-auto-1774273150-13"
        title = "Auto Rule 13"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword13" nocase
        $str_1 = "keyword14" nocase
        $str_2 = "keyword15" nocase
    condition:
        any of them
}

rule sigma_auto_1774272547_1 {
    meta:
        id = "sigma-auto-1774272547-1"
        title = "Auto Rule 1"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword1" nocase
        $str_1 = "keyword2" nocase
        $str_2 = "keyword3" nocase
    condition:
        any of them
}

rule sigma_auto_1774274026_11 {
    meta:
        id = "sigma-auto-1774274026-11"
        title = "Auto Rule 11"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword11" nocase
        $str_1 = "keyword12" nocase
        $str_2 = "keyword13" nocase
    condition:
        any of them
}

rule sigma_auto_1774274810_15 {
    meta:
        id = "sigma-auto-1774274810-15"
        title = "Auto Rule 15"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword15" nocase
        $str_1 = "keyword16" nocase
        $str_2 = "keyword17" nocase
    condition:
        any of them
}

rule sigma_auto_1774273721_19 {
    meta:
        id = "sigma-auto-1774273721-19"
        title = "Auto Rule 19"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword19" nocase
        $str_1 = "keyword20" nocase
        $str_2 = "keyword21" nocase
    condition:
        any of them
}

rule sigma_auto_1774274931_8 {
    meta:
        id = "sigma-auto-1774274931-8"
        title = "Auto Rule 8"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword8" nocase
        $str_1 = "keyword9" nocase
        $str_2 = "keyword10" nocase
    condition:
        any of them
}

rule sigma_auto_1774272409_8 {
    meta:
        id = "sigma-auto-1774272409-8"
        title = "Auto Rule 8"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword8" nocase
        $str_1 = "keyword9" nocase
        $str_2 = "keyword10" nocase
    condition:
        any of them
}

rule sigma_auto_1774275042_0 {
    meta:
        id = "sigma-auto-1774275042-0"
        title = "Auto Rule 0"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword0" nocase
        $str_1 = "keyword1" nocase
        $str_2 = "keyword2" nocase
    condition:
        any of them
}

rule sigma_auto_1774275059_4 {
    meta:
        id = "sigma-auto-1774275059-4"
        title = "Auto Rule 4"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword4" nocase
        $str_1 = "keyword5" nocase
        $str_2 = "keyword6" nocase
    condition:
        any of them
}

rule sigma_auto_1774274081_24 {
    meta:
        id = "sigma-auto-1774274081-24"
        title = "Auto Rule 24"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword24" nocase
        $str_1 = "keyword25" nocase
        $str_2 = "keyword26" nocase
    condition:
        any of them
}

rule sigma_auto_1774274097_28 {
    meta:
        id = "sigma-auto-1774274097-28"
        title = "Auto Rule 28"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword28" nocase
        $str_1 = "keyword29" nocase
        $str_2 = "keyword30" nocase
    condition:
        any of them
}

rule sigma_auto_1774274455_6 {
    meta:
        id = "sigma-auto-1774274455-6"
        title = "Auto Rule 6"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword6" nocase
        $str_1 = "keyword7" nocase
        $str_2 = "keyword8" nocase
    condition:
        any of them
}

rule sigma_auto_1774273041_19 {
    meta:
        id = "sigma-auto-1774273041-19"
        title = "Auto Rule 19"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword19" nocase
        $str_1 = "keyword20" nocase
        $str_2 = "keyword21" nocase
    condition:
        any of them
}

rule sigma_auto_1774273609_26 {
    meta:
        id = "sigma-auto-1774273609-26"
        title = "Auto Rule 26"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword26" nocase
        $str_1 = "keyword27" nocase
        $str_2 = "keyword28" nocase
    condition:
        any of them
}

rule sigma_auto_1774273100_1 {
    meta:
        id = "sigma-auto-1774273100-1"
        title = "Auto Rule 1"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword1" nocase
        $str_1 = "keyword2" nocase
        $str_2 = "keyword3" nocase
    condition:
        any of them
}

rule sigma_auto_1774273427_18 {
    meta:
        id = "sigma-auto-1774273427-18"
        title = "Auto Rule 18"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword18" nocase
        $str_1 = "keyword19" nocase
        $str_2 = "keyword20" nocase
    condition:
        any of them
}

rule sigma_auto_1774274085_25 {
    meta:
        id = "sigma-auto-1774274085-25"
        title = "Auto Rule 25"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword25" nocase
        $str_1 = "keyword26" nocase
        $str_2 = "keyword27" nocase
    condition:
        any of them
}

rule sigma_auto_1774274952_13 {
    meta:
        id = "sigma-auto-1774274952-13"
        title = "Auto Rule 13"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword13" nocase
        $str_1 = "keyword14" nocase
        $str_2 = "keyword15" nocase
    condition:
        any of them
}

rule sigma_auto_1774274526_23 {
    meta:
        id = "sigma-auto-1774274526-23"
        title = "Auto Rule 23"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword23" nocase
        $str_1 = "keyword24" nocase
        $str_2 = "keyword25" nocase
    condition:
        any of them
}

rule sigma_auto_1774272982_5 {
    meta:
        id = "sigma-auto-1774272982-5"
        title = "Auto Rule 5"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword5" nocase
        $str_1 = "keyword6" nocase
        $str_2 = "keyword7" nocase
    condition:
        any of them
}

rule sigma_auto_1774273368_4 {
    meta:
        id = "sigma-auto-1774273368-4"
        title = "Auto Rule 4"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword4" nocase
        $str_1 = "keyword5" nocase
        $str_2 = "keyword6" nocase
    condition:
        any of them
}

rule sigma_auto_1774274763_4 {
    meta:
        id = "sigma-auto-1774274763-4"
        title = "Auto Rule 4"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword4" nocase
        $str_1 = "keyword5" nocase
        $str_2 = "keyword6" nocase
    condition:
        any of them
}

rule sigma_auto_1774274680_20 {
    meta:
        id = "sigma-auto-1774274680-20"
        title = "Auto Rule 20"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword20" nocase
        $str_1 = "keyword21" nocase
        $str_2 = "keyword22" nocase
    condition:
        any of them
}

rule sigma_auto_1774274385_21 {
    meta:
        id = "sigma-auto-1774274385-21"
        title = "Auto Rule 21"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword21" nocase
        $str_1 = "keyword22" nocase
        $str_2 = "keyword23" nocase
    condition:
        any of them
}

rule sigma_auto_1774273641_0 {
    meta:
        id = "sigma-auto-1774273641-0"
        title = "Auto Rule 0"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword0" nocase
        $str_1 = "keyword1" nocase
        $str_2 = "keyword2" nocase
    condition:
        any of them
}

rule sigma_auto_1774272777_24 {
    meta:
        id = "sigma-auto-1774272777-24"
        title = "Auto Rule 24"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword24" nocase
        $str_1 = "keyword25" nocase
        $str_2 = "keyword26" nocase
    condition:
        any of them
}

rule sigma_auto_1774274318_5 {
    meta:
        id = "sigma-auto-1774274318-5"
        title = "Auto Rule 5"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword5" nocase
        $str_1 = "keyword6" nocase
        $str_2 = "keyword7" nocase
    condition:
        any of them
}

rule sigma_auto_1774274446_4 {
    meta:
        id = "sigma-auto-1774274446-4"
        title = "Auto Rule 4"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword4" nocase
        $str_1 = "keyword5" nocase
        $str_2 = "keyword6" nocase
    condition:
        any of them
}

rule sigma_auto_1774273696_13 {
    meta:
        id = "sigma-auto-1774273696-13"
        title = "Auto Rule 13"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword13" nocase
        $str_1 = "keyword14" nocase
        $str_2 = "keyword15" nocase
    condition:
        any of them
}

rule sigma_auto_1774273658_4 {
    meta:
        id = "sigma-auto-1774273658-4"
        title = "Auto Rule 4"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword4" nocase
        $str_1 = "keyword5" nocase
        $str_2 = "keyword6" nocase
    condition:
        any of them
}

rule sigma_auto_1774273840_6 {
    meta:
        id = "sigma-auto-1774273840-6"
        title = "Auto Rule 6"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword6" nocase
        $str_1 = "keyword7" nocase
        $str_2 = "keyword8" nocase
    condition:
        any of them
}

rule sigma_auto_1774274168_8 {
    meta:
        id = "sigma-auto-1774274168-8"
        title = "Auto Rule 8"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword8" nocase
        $str_1 = "keyword9" nocase
        $str_2 = "keyword10" nocase
    condition:
        any of them
}

rule sigma_auto_1774273279_14 {
    meta:
        id = "sigma-auto-1774273279-14"
        title = "Auto Rule 14"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword14" nocase
        $str_1 = "keyword15" nocase
        $str_2 = "keyword16" nocase
    condition:
        any of them
}

rule sigma_auto_1774274956_14 {
    meta:
        id = "sigma-auto-1774274956-14"
        title = "Auto Rule 14"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword14" nocase
        $str_1 = "keyword15" nocase
        $str_2 = "keyword16" nocase
    condition:
        any of them
}

rule sigma_auto_1774273675_8 {
    meta:
        id = "sigma-auto-1774273675-8"
        title = "Auto Rule 8"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword8" nocase
        $str_1 = "keyword9" nocase
        $str_2 = "keyword10" nocase
    condition:
        any of them
}

rule sigma_auto_1774274297_0 {
    meta:
        id = "sigma-auto-1774274297-0"
        title = "Auto Rule 0"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword0" nocase
        $str_1 = "keyword1" nocase
        $str_2 = "keyword2" nocase
    condition:
        any of them
}

rule sigma_auto_1774274509_19 {
    meta:
        id = "sigma-auto-1774274509-19"
        title = "Auto Rule 19"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword19" nocase
        $str_1 = "keyword20" nocase
        $str_2 = "keyword21" nocase
    condition:
        any of them
}

rule sigma_auto_1774275055_3 {
    meta:
        id = "sigma-auto-1774275055-3"
        title = "Auto Rule 3"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword3" nocase
        $str_1 = "keyword4" nocase
        $str_2 = "keyword5" nocase
    condition:
        any of them
}

rule sigma_auto_1774272434_14 {
    meta:
        id = "sigma-auto-1774272434-14"
        title = "Auto Rule 14"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword14" nocase
        $str_1 = "keyword15" nocase
        $str_2 = "keyword16" nocase
    condition:
        any of them
}

rule sigma_auto_1774274518_21 {
    meta:
        id = "sigma-auto-1774274518-21"
        title = "Auto Rule 21"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword21" nocase
        $str_1 = "keyword22" nocase
        $str_2 = "keyword23" nocase
    condition:
        any of them
}

rule sigma_auto_1774273414_15 {
    meta:
        id = "sigma-auto-1774273414-15"
        title = "Auto Rule 15"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword15" nocase
        $str_1 = "keyword16" nocase
        $str_2 = "keyword17" nocase
    condition:
        any of them
}

rule sigma_auto_1774273856_10 {
    meta:
        id = "sigma-auto-1774273856-10"
        title = "Auto Rule 10"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword10" nocase
        $str_1 = "keyword11" nocase
        $str_2 = "keyword12" nocase
    condition:
        any of them
}

rule sigma_auto_1774273597_23 {
    meta:
        id = "sigma-auto-1774273597-23"
        title = "Auto Rule 23"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword23" nocase
        $str_1 = "keyword24" nocase
        $str_2 = "keyword25" nocase
    condition:
        any of them
}

rule sigma_auto_1774273418_16 {
    meta:
        id = "sigma-auto-1774273418-16"
        title = "Auto Rule 16"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword16" nocase
        $str_1 = "keyword17" nocase
        $str_2 = "keyword18" nocase
    condition:
        any of them
}

rule sigma_auto_1774274914_4 {
    meta:
        id = "sigma-auto-1774274914-4"
        title = "Auto Rule 4"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword4" nocase
        $str_1 = "keyword5" nocase
        $str_2 = "keyword6" nocase
    condition:
        any of them
}

rule sigma_auto_1774272884_11 {
    meta:
        id = "sigma-auto-1774272884-11"
        title = "Auto Rule 11"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword11" nocase
        $str_1 = "keyword12" nocase
        $str_2 = "keyword13" nocase
    condition:
        any of them
}

rule sigma_auto_1774273576_18 {
    meta:
        id = "sigma-auto-1774273576-18"
        title = "Auto Rule 18"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword18" nocase
        $str_1 = "keyword19" nocase
        $str_2 = "keyword20" nocase
    condition:
        any of them
}

rule sigma_auto_1774273142_11 {
    meta:
        id = "sigma-auto-1774273142-11"
        title = "Auto Rule 11"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword11" nocase
        $str_1 = "keyword12" nocase
        $str_2 = "keyword13" nocase
    condition:
        any of them
}

rule sigma_auto_1774274701_25 {
    meta:
        id = "sigma-auto-1774274701-25"
        title = "Auto Rule 25"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword25" nocase
        $str_1 = "keyword26" nocase
        $str_2 = "keyword27" nocase
    condition:
        any of them
}

rule sigma_auto_1774274672_18 {
    meta:
        id = "sigma-auto-1774274672-18"
        title = "Auto Rule 18"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword18" nocase
        $str_1 = "keyword19" nocase
        $str_2 = "keyword20" nocase
    condition:
        any of them
}

rule sigma_auto_1774272892_13 {
    meta:
        id = "sigma-auto-1774272892-13"
        title = "Auto Rule 13"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword13" nocase
        $str_1 = "keyword14" nocase
        $str_2 = "keyword15" nocase
    condition:
        any of them
}

rule sigma_auto_1774274330_8 {
    meta:
        id = "sigma-auto-1774274330-8"
        title = "Auto Rule 8"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword8" nocase
        $str_1 = "keyword9" nocase
        $str_2 = "keyword10" nocase
    condition:
        any of them
}

rule sigma_auto_1774274935_9 {
    meta:
        id = "sigma-auto-1774274935-9"
        title = "Auto Rule 9"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword9" nocase
        $str_1 = "keyword10" nocase
        $str_2 = "keyword11" nocase
    condition:
        any of them
}

rule sigma_auto_1774274215_19 {
    meta:
        id = "sigma-auto-1774274215-19"
        title = "Auto Rule 19"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword19" nocase
        $str_1 = "keyword20" nocase
        $str_2 = "keyword21" nocase
    condition:
        any of them
}

rule sigma_auto_1774274977_19 {
    meta:
        id = "sigma-auto-1774274977-19"
        title = "Auto Rule 19"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword19" nocase
        $str_1 = "keyword20" nocase
        $str_2 = "keyword21" nocase
    condition:
        any of them
}

rule sigma_auto_1774274177_10 {
    meta:
        id = "sigma-auto-1774274177-10"
        title = "Auto Rule 10"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword10" nocase
        $str_1 = "keyword11" nocase
        $str_2 = "keyword12" nocase
    condition:
        any of them
}

rule sigma_auto_1774273827_3 {
    meta:
        id = "sigma-auto-1774273827-3"
        title = "Auto Rule 3"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword3" nocase
        $str_1 = "keyword4" nocase
        $str_2 = "keyword5" nocase
    condition:
        any of them
}

rule sigma_auto_1774273364_3 {
    meta:
        id = "sigma-auto-1774273364-3"
        title = "Auto Rule 3"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword3" nocase
        $str_1 = "keyword4" nocase
        $str_2 = "keyword5" nocase
    condition:
        any of them
}

rule sigma_auto_1774273882_16 {
    meta:
        id = "sigma-auto-1774273882-16"
        title = "Auto Rule 16"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword16" nocase
        $str_1 = "keyword17" nocase
        $str_2 = "keyword18" nocase
    condition:
        any of them
}

rule sigma_auto_1774273180_20 {
    meta:
        id = "sigma-auto-1774273180-20"
        title = "Auto Rule 20"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword20" nocase
        $str_1 = "keyword21" nocase
        $str_2 = "keyword22" nocase
    condition:
        any of them
}

rule sigma_auto_1774274147_3 {
    meta:
        id = "sigma-auto-1774274147-3"
        title = "Auto Rule 3"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword3" nocase
        $str_1 = "keyword4" nocase
        $str_2 = "keyword5" nocase
    condition:
        any of them
}

rule sigma_auto_1774274826_19 {
    meta:
        id = "sigma-auto-1774274826-19"
        title = "Auto Rule 19"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword19" nocase
        $str_1 = "keyword20" nocase
        $str_2 = "keyword21" nocase
    condition:
        any of them
}

rule sigma_auto_1774272913_18 {
    meta:
        id = "sigma-auto-1774272913-18"
        title = "Auto Rule 18"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword18" nocase
        $str_1 = "keyword19" nocase
        $str_2 = "keyword20" nocase
    condition:
        any of them
}

rule sigma_auto_1774274038_14 {
    meta:
        id = "sigma-auto-1774274038-14"
        title = "Auto Rule 14"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword14" nocase
        $str_1 = "keyword15" nocase
        $str_2 = "keyword16" nocase
    condition:
        any of them
}

rule sigma_auto_1774273704_15 {
    meta:
        id = "sigma-auto-1774273704-15"
        title = "Auto Rule 15"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword15" nocase
        $str_1 = "keyword16" nocase
        $str_2 = "keyword17" nocase
    condition:
        any of them
}

rule sigma_auto_1774274693_23 {
    meta:
        id = "sigma-auto-1774274693-23"
        title = "Auto Rule 23"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword23" nocase
        $str_1 = "keyword24" nocase
        $str_2 = "keyword25" nocase
    condition:
        any of them
}

rule sigma_auto_1774274981_20 {
    meta:
        id = "sigma-auto-1774274981-20"
        title = "Auto Rule 20"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword20" nocase
        $str_1 = "keyword21" nocase
        $str_2 = "keyword22" nocase
    condition:
        any of them
}

rule sigma_auto_1774272379_1 {
    meta:
        id = "sigma-auto-1774272379-1"
        title = "Auto Rule 1"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword1" nocase
        $str_1 = "keyword2" nocase
        $str_2 = "keyword3" nocase
    condition:
        any of them
}

rule sigma_auto_1774274910_3 {
    meta:
        id = "sigma-auto-1774274910-3"
        title = "Auto Rule 3"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword3" nocase
        $str_1 = "keyword4" nocase
        $str_2 = "keyword5" nocase
    condition:
        any of them
}

rule sigma_auto_1774272472_23 {
    meta:
        id = "sigma-auto-1774272472-23"
        title = "Auto Rule 23"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword23" nocase
        $str_1 = "keyword24" nocase
        $str_2 = "keyword25" nocase
    condition:
        any of them
}

rule sigma_auto_1774272731_13 {
    meta:
        id = "sigma-auto-1774272731-13"
        title = "Auto Rule 13"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword13" nocase
        $str_1 = "keyword14" nocase
        $str_2 = "keyword15" nocase
    condition:
        any of them
}

rule sigma_auto_1774273687_11 {
    meta:
        id = "sigma-auto-1774273687-11"
        title = "Auto Rule 11"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword11" nocase
        $str_1 = "keyword12" nocase
        $str_2 = "keyword13" nocase
    condition:
        any of them
}

rule sigma_auto_1774273759_28 {
    meta:
        id = "sigma-auto-1774273759-28"
        title = "Auto Rule 28"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword28" nocase
        $str_1 = "keyword29" nocase
        $str_2 = "keyword30" nocase
    condition:
        any of them
}

rule sigma_auto_1774274793_11 {
    meta:
        id = "sigma-auto-1774274793-11"
        title = "Auto Rule 11"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword11" nocase
        $str_1 = "keyword12" nocase
        $str_2 = "keyword13" nocase
    condition:
        any of them
}

rule sigma_auto_1774275122_19 {
    meta:
        id = "sigma-auto-1774275122-19"
        title = "Auto Rule 19"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword19" nocase
        $str_1 = "keyword20" nocase
        $str_2 = "keyword21" nocase
    condition:
        any of them
}

rule sigma_auto_1774273683_10 {
    meta:
        id = "sigma-auto-1774273683-10"
        title = "Auto Rule 10"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword10" nocase
        $str_1 = "keyword11" nocase
        $str_2 = "keyword12" nocase
    condition:
        any of them
}

rule sigma_auto_1774272974_3 {
    meta:
        id = "sigma-auto-1774272974-3"
        title = "Auto Rule 3"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword3" nocase
        $str_1 = "keyword4" nocase
        $str_2 = "keyword5" nocase
    condition:
        any of them
}

rule sigma_auto_1774274364_16 {
    meta:
        id = "sigma-auto-1774274364-16"
        title = "Auto Rule 16"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword16" nocase
        $str_1 = "keyword17" nocase
        $str_2 = "keyword18" nocase
    condition:
        any of them
}

rule sigma_auto_1774272585_10 {
    meta:
        id = "sigma-auto-1774272585-10"
        title = "Auto Rule 10"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword10" nocase
        $str_1 = "keyword11" nocase
        $str_2 = "keyword12" nocase
    condition:
        any of them
}

rule sigma_auto_1774275076_8 {
    meta:
        id = "sigma-auto-1774275076-8"
        title = "Auto Rule 8"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword8" nocase
        $str_1 = "keyword9" nocase
        $str_2 = "keyword10" nocase
    condition:
        any of them
}

rule sigma_auto_1774274986_21 {
    meta:
        id = "sigma-auto-1774274986-21"
        title = "Auto Rule 21"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword21" nocase
        $str_1 = "keyword22" nocase
        $str_2 = "keyword23" nocase
    condition:
        any of them
}

rule sigma_auto_1774272676_0 {
    meta:
        id = "sigma-auto-1774272676-0"
        title = "Auto Rule 0"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword0" nocase
        $str_1 = "keyword1" nocase
        $str_2 = "keyword2" nocase
    condition:
        any of them
}

rule sigma_auto_1774272627_20 {
    meta:
        id = "sigma-auto-1774272627-20"
        title = "Auto Rule 20"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword20" nocase
        $str_1 = "keyword21" nocase
        $str_2 = "keyword22" nocase
    condition:
        any of them
}

rule sigma_auto_1774273095_0 {
    meta:
        id = "sigma-auto-1774273095-0"
        title = "Auto Rule 0"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword0" nocase
        $str_1 = "keyword1" nocase
        $str_2 = "keyword2" nocase
    condition:
        any of them
}

rule sigma_auto_1774272622_19 {
    meta:
        id = "sigma-auto-1774272622-19"
        title = "Auto Rule 19"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword19" nocase
        $str_1 = "keyword20" nocase
        $str_2 = "keyword21" nocase
    condition:
        any of them
}

rule sigma_auto_1774274759_3 {
    meta:
        id = "sigma-auto-1774274759-3"
        title = "Auto Rule 3"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword3" nocase
        $str_1 = "keyword4" nocase
        $str_2 = "keyword5" nocase
    condition:
        any of them
}

rule sigma_auto_1774274005_6 {
    meta:
        id = "sigma-auto-1774274005-6"
        title = "Auto Rule 6"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword6" nocase
        $str_1 = "keyword7" nocase
        $str_2 = "keyword8" nocase
    condition:
        any of them
}

rule sigma_auto_1774272597_13 {
    meta:
        id = "sigma-auto-1774272597-13"
        title = "Auto Rule 13"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword13" nocase
        $str_1 = "keyword14" nocase
        $str_2 = "keyword15" nocase
    condition:
        any of them
}

rule sigma_auto_1774273406_13 {
    meta:
        id = "sigma-auto-1774273406-13"
        title = "Auto Rule 13"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword13" nocase
        $str_1 = "keyword14" nocase
        $str_2 = "keyword15" nocase
    condition:
        any of them
}

rule sigma_auto_1774274768_5 {
    meta:
        id = "sigma-auto-1774274768-5"
        title = "Auto Rule 5"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword5" nocase
        $str_1 = "keyword6" nocase
        $str_2 = "keyword7" nocase
    condition:
        any of them
}

rule sigma_auto_1774274484_13 {
    meta:
        id = "sigma-auto-1774274484-13"
        title = "Auto Rule 13"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword13" nocase
        $str_1 = "keyword14" nocase
        $str_2 = "keyword15" nocase
    condition:
        any of them
}

rule sigma_auto_1774273831_4 {
    meta:
        id = "sigma-auto-1774273831-4"
        title = "Auto Rule 4"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword4" nocase
        $str_1 = "keyword5" nocase
        $str_2 = "keyword6" nocase
    condition:
        any of them
}

rule sigma_auto_1774272388_3 {
    meta:
        id = "sigma-auto-1774272388-3"
        title = "Auto Rule 3"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword3" nocase
        $str_1 = "keyword4" nocase
        $str_2 = "keyword5" nocase
    condition:
        any of them
}

rule sigma_auto_1774272430_13 {
    meta:
        id = "sigma-auto-1774272430-13"
        title = "Auto Rule 13"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword13" nocase
        $str_1 = "keyword14" nocase
        $str_2 = "keyword15" nocase
    condition:
        any of them
}

rule sigma_auto_1774272773_23 {
    meta:
        id = "sigma-auto-1774272773-23"
        title = "Auto Rule 23"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword23" nocase
        $str_1 = "keyword24" nocase
        $str_2 = "keyword25" nocase
    condition:
        any of them
}

rule sigma_auto_1774274309_3 {
    meta:
        id = "sigma-auto-1774274309-3"
        title = "Auto Rule 3"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword3" nocase
        $str_1 = "keyword4" nocase
        $str_2 = "keyword5" nocase
    condition:
        any of them
}

rule sigma_auto_1774274322_6 {
    meta:
        id = "sigma-auto-1774274322-6"
        title = "Auto Rule 6"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword6" nocase
        $str_1 = "keyword7" nocase
        $str_2 = "keyword8" nocase
    condition:
        any of them
}

rule sigma_auto_1774273304_20 {
    meta:
        id = "sigma-auto-1774273304-20"
        title = "Auto Rule 20"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword20" nocase
        $str_1 = "keyword21" nocase
        $str_2 = "keyword22" nocase
    condition:
        any of them
}

rule sigma_auto_1774274360_15 {
    meta:
        id = "sigma-auto-1774274360-15"
        title = "Auto Rule 15"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword15" nocase
        $str_1 = "keyword16" nocase
        $str_2 = "keyword17" nocase
    condition:
        any of them
}

rule sigma_auto_1774273584_20 {
    meta:
        id = "sigma-auto-1774273584-20"
        title = "Auto Rule 20"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword20" nocase
        $str_1 = "keyword21" nocase
        $str_2 = "keyword22" nocase
    condition:
        any of them
}

rule sigma_auto_1774275067_6 {
    meta:
        id = "sigma-auto-1774275067-6"
        title = "Auto Rule 6"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword6" nocase
        $str_1 = "keyword7" nocase
        $str_2 = "keyword8" nocase
    condition:
        any of them
}

rule sigma_auto_1774273295_18 {
    meta:
        id = "sigma-auto-1774273295-18"
        title = "Auto Rule 18"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword18" nocase
        $str_1 = "keyword19" nocase
        $str_2 = "keyword20" nocase
    condition:
        any of them
}

rule sigma_auto_1774273679_9 {
    meta:
        id = "sigma-auto-1774273679-9"
        title = "Auto Rule 9"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword9" nocase
        $str_1 = "keyword10" nocase
        $str_2 = "keyword11" nocase
    condition:
        any of them
}

rule sigma_auto_1774273980_0 {
    meta:
        id = "sigma-auto-1774273980-0"
        title = "Auto Rule 0"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword0" nocase
        $str_1 = "keyword1" nocase
        $str_2 = "keyword2" nocase
    condition:
        any of them
}

rule sigma_auto_1774274822_18 {
    meta:
        id = "sigma-auto-1774274822-18"
        title = "Auto Rule 18"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword18" nocase
        $str_1 = "keyword19" nocase
        $str_2 = "keyword20" nocase
    condition:
        any of them
}

rule sigma_auto_1774274805_14 {
    meta:
        id = "sigma-auto-1774274805-14"
        title = "Auto Rule 14"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword14" nocase
        $str_1 = "keyword15" nocase
        $str_2 = "keyword16" nocase
    condition:
        any of them
}

rule sigma_auto_1774273848_8 {
    meta:
        id = "sigma-auto-1774273848-8"
        title = "Auto Rule 8"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword8" nocase
        $str_1 = "keyword9" nocase
        $str_2 = "keyword10" nocase
    condition:
        any of them
}

rule sigma_auto_1774272543_0 {
    meta:
        id = "sigma-auto-1774272543-0"
        title = "Auto Rule 0"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword0" nocase
        $str_1 = "keyword1" nocase
        $str_2 = "keyword2" nocase
    condition:
        any of them
}

rule sigma_auto_1774272417_10 {
    meta:
        id = "sigma-auto-1774272417-10"
        title = "Auto Rule 10"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword10" nocase
        $str_1 = "keyword11" nocase
        $str_2 = "keyword12" nocase
    condition:
        any of them
}

rule sigma_auto_1774272922_20 {
    meta:
        id = "sigma-auto-1774272922-20"
        title = "Auto Rule 20"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword20" nocase
        $str_1 = "keyword21" nocase
        $str_2 = "keyword22" nocase
    condition:
        any of them
}

rule sigma_auto_1774273376_6 {
    meta:
        id = "sigma-auto-1774273376-6"
        title = "Auto Rule 6"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword6" nocase
        $str_1 = "keyword7" nocase
        $str_2 = "keyword8" nocase
    condition:
        any of them
}

rule sigma_auto_1774273738_23 {
    meta:
        id = "sigma-auto-1774273738-23"
        title = "Auto Rule 23"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword23" nocase
        $str_1 = "keyword24" nocase
        $str_2 = "keyword25" nocase
    condition:
        any of them
}

rule sigma_auto_1774273890_18 {
    meta:
        id = "sigma-auto-1774273890-18"
        title = "Auto Rule 18"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword18" nocase
        $str_1 = "keyword19" nocase
        $str_2 = "keyword20" nocase
    condition:
        any of them
}

rule sigma_auto_1774272978_4 {
    meta:
        id = "sigma-auto-1774272978-4"
        title = "Auto Rule 4"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword4" nocase
        $str_1 = "keyword5" nocase
        $str_2 = "keyword6" nocase
    condition:
        any of them
}

rule sigma_auto_1774272576_8 {
    meta:
        id = "sigma-auto-1774272576-8"
        title = "Auto Rule 8"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword8" nocase
        $str_1 = "keyword9" nocase
        $str_2 = "keyword10" nocase
    condition:
        any of them
}

rule sigma_auto_1774274642_11 {
    meta:
        id = "sigma-auto-1774274642-11"
        title = "Auto Rule 11"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword11" nocase
        $str_1 = "keyword12" nocase
        $str_2 = "keyword13" nocase
    condition:
        any of them
}

rule sigma_auto_1774274513_20 {
    meta:
        id = "sigma-auto-1774274513-20"
        title = "Auto Rule 20"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword20" nocase
        $str_1 = "keyword21" nocase
        $str_2 = "keyword22" nocase
    condition:
        any of them
}

rule sigma_auto_1774273814_0 {
    meta:
        id = "sigma-auto-1774273814-0"
        title = "Auto Rule 0"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword0" nocase
        $str_1 = "keyword1" nocase
        $str_2 = "keyword2" nocase
    condition:
        any of them
}

rule sigma_auto_1774274139_1 {
    meta:
        id = "sigma-auto-1774274139-1"
        title = "Auto Rule 1"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword1" nocase
        $str_1 = "keyword2" nocase
        $str_2 = "keyword3" nocase
    condition:
        any of them
}

rule sigma_auto_1774273877_15 {
    meta:
        id = "sigma-auto-1774273877-15"
        title = "Auto Rule 15"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword15" nocase
        $str_1 = "keyword16" nocase
        $str_2 = "keyword17" nocase
    condition:
        any of them
}

rule sigma_auto_1774274539_26 {
    meta:
        id = "sigma-auto-1774274539-26"
        title = "Auto Rule 26"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword26" nocase
        $str_1 = "keyword27" nocase
        $str_2 = "keyword28" nocase
    condition:
        any of them
}

rule sigma_auto_1774273725_20 {
    meta:
        id = "sigma-auto-1774273725-20"
        title = "Auto Rule 20"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword20" nocase
        $str_1 = "keyword21" nocase
        $str_2 = "keyword22" nocase
    condition:
        any of them
}

rule sigma_auto_1774272618_18 {
    meta:
        id = "sigma-auto-1774272618-18"
        title = "Auto Rule 18"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword18" nocase
        $str_1 = "keyword19" nocase
        $str_2 = "keyword20" nocase
    condition:
        any of them
}

rule sigma_auto_1774272564_5 {
    meta:
        id = "sigma-auto-1774272564-5"
        title = "Auto Rule 5"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword5" nocase
        $str_1 = "keyword6" nocase
        $str_2 = "keyword7" nocase
    condition:
        any of them
}

rule sigma_auto_1774272606_15 {
    meta:
        id = "sigma-auto-1774272606-15"
        title = "Auto Rule 15"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword15" nocase
        $str_1 = "keyword16" nocase
        $str_2 = "keyword17" nocase
    condition:
        any of them
}

rule sigma_auto_1774275084_10 {
    meta:
        id = "sigma-auto-1774275084-10"
        title = "Auto Rule 10"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword10" nocase
        $str_1 = "keyword11" nocase
        $str_2 = "keyword12" nocase
    condition:
        any of them
}

rule sigma_auto_1774274089_26 {
    meta:
        id = "sigma-auto-1774274089-26"
        title = "Auto Rule 26"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword26" nocase
        $str_1 = "keyword27" nocase
        $str_2 = "keyword28" nocase
    condition:
        any of them
}

rule sigma_auto_1774273016_13 {
    meta:
        id = "sigma-auto-1774273016-13"
        title = "Auto Rule 13"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword13" nocase
        $str_1 = "keyword14" nocase
        $str_2 = "keyword15" nocase
    condition:
        any of them
}

rule sigma_auto_1774273580_19 {
    meta:
        id = "sigma-auto-1774273580-19"
        title = "Auto Rule 19"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword19" nocase
        $str_1 = "keyword20" nocase
        $str_2 = "keyword21" nocase
    condition:
        any of them
}

rule sigma_auto_1774275126_20 {
    meta:
        id = "sigma-auto-1774275126-20"
        title = "Auto Rule 20"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword20" nocase
        $str_1 = "keyword21" nocase
        $str_2 = "keyword22" nocase
    condition:
        any of them
}

rule sigma_auto_1774273241_5 {
    meta:
        id = "sigma-auto-1774273241-5"
        title = "Auto Rule 5"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword5" nocase
        $str_1 = "keyword6" nocase
        $str_2 = "keyword7" nocase
    condition:
        any of them
}

rule sigma_auto_1774274801_13 {
    meta:
        id = "sigma-auto-1774274801-13"
        title = "Auto Rule 13"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword13" nocase
        $str_1 = "keyword14" nocase
        $str_2 = "keyword15" nocase
    condition:
        any of them
}

rule sigma_auto_1774275105_15 {
    meta:
        id = "sigma-auto-1774275105-15"
        title = "Auto Rule 15"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword15" nocase
        $str_1 = "keyword16" nocase
        $str_2 = "keyword17" nocase
    condition:
        any of them
}

rule sigma_auto_1774274223_21 {
    meta:
        id = "sigma-auto-1774274223-21"
        title = "Auto Rule 21"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword21" nocase
        $str_1 = "keyword22" nocase
        $str_2 = "keyword23" nocase
    condition:
        any of them
}

rule sigma_auto_1774273024_15 {
    meta:
        id = "sigma-auto-1774273024-15"
        title = "Auto Rule 15"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword15" nocase
        $str_1 = "keyword16" nocase
        $str_2 = "keyword17" nocase
    condition:
        any of them
}

rule sigma_auto_1774273588_21 {
    meta:
        id = "sigma-auto-1774273588-21"
        title = "Auto Rule 21"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword21" nocase
        $str_1 = "keyword22" nocase
        $str_2 = "keyword23" nocase
    condition:
        any of them
}

rule sigma_auto_1774272451_18 {
    meta:
        id = "sigma-auto-1774272451-18"
        title = "Auto Rule 18"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword18" nocase
        $str_1 = "keyword19" nocase
        $str_2 = "keyword20" nocase
    condition:
        any of them
}

rule sigma_auto_1774273137_10 {
    meta:
        id = "sigma-auto-1774273137-10"
        title = "Auto Rule 10"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword10" nocase
        $str_1 = "keyword11" nocase
        $str_2 = "keyword12" nocase
    condition:
        any of them
}

rule sigma_auto_1774273283_15 {
    meta:
        id = "sigma-auto-1774273283-15"
        title = "Auto Rule 15"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword15" nocase
        $str_1 = "keyword16" nocase
        $str_2 = "keyword17" nocase
    condition:
        any of them
}

rule sigma_auto_1774274492_15 {
    meta:
        id = "sigma-auto-1774274492-15"
        title = "Auto Rule 15"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword15" nocase
        $str_1 = "keyword16" nocase
        $str_2 = "keyword17" nocase
    condition:
        any of them
}

rule sigma_auto_1774272697_5 {
    meta:
        id = "sigma-auto-1774272697-5"
        title = "Auto Rule 5"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword5" nocase
        $str_1 = "keyword6" nocase
        $str_2 = "keyword7" nocase
    condition:
        any of them
}

rule sigma_auto_1774274596_0 {
    meta:
        id = "sigma-auto-1774274596-0"
        title = "Auto Rule 0"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword0" nocase
        $str_1 = "keyword1" nocase
        $str_2 = "keyword2" nocase
    condition:
        any of them
}

rule sigma_auto_1774273567_16 {
    meta:
        id = "sigma-auto-1774273567-16"
        title = "Auto Rule 16"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword16" nocase
        $str_1 = "keyword17" nocase
        $str_2 = "keyword18" nocase
    condition:
        any of them
}

rule sigma_auto_1774272455_19 {
    meta:
        id = "sigma-auto-1774272455-19"
        title = "Auto Rule 19"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword19" nocase
        $str_1 = "keyword20" nocase
        $str_2 = "keyword21" nocase
    condition:
        any of them
}

rule sigma_auto_1774274663_16 {
    meta:
        id = "sigma-auto-1774274663-16"
        title = "Auto Rule 16"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword16" nocase
        $str_1 = "keyword17" nocase
        $str_2 = "keyword18" nocase
    condition:
        any of them
}

rule sigma_auto_1774274471_10 {
    meta:
        id = "sigma-auto-1774274471-10"
        title = "Auto Rule 10"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword10" nocase
        $str_1 = "keyword11" nocase
        $str_2 = "keyword12" nocase
    condition:
        any of them
}

rule sigma_auto_1774273645_1 {
    meta:
        id = "sigma-auto-1774273645-1"
        title = "Auto Rule 1"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword1" nocase
        $str_1 = "keyword2" nocase
        $str_2 = "keyword3" nocase
    condition:
        any of them
}

rule sigma_auto_1774273521_5 {
    meta:
        id = "sigma-auto-1774273521-5"
        title = "Auto Rule 5"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword5" nocase
        $str_1 = "keyword6" nocase
        $str_2 = "keyword7" nocase
    condition:
        any of them
}

rule sigma_auto_1774274339_10 {
    meta:
        id = "sigma-auto-1774274339-10"
        title = "Auto Rule 10"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword10" nocase
        $str_1 = "keyword11" nocase
        $str_2 = "keyword12" nocase
    condition:
        any of them
}

rule sigma_auto_1774274022_10 {
    meta:
        id = "sigma-auto-1774274022-10"
        title = "Auto Rule 10"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword10" nocase
        $str_1 = "keyword11" nocase
        $str_2 = "keyword12" nocase
    condition:
        any of them
}

rule sigma_auto_1774274613_4 {
    meta:
        id = "sigma-auto-1774274613-4"
        title = "Auto Rule 4"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword4" nocase
        $str_1 = "keyword5" nocase
        $str_2 = "keyword6" nocase
    condition:
        any of them
}

rule sigma_auto_1774273852_9 {
    meta:
        id = "sigma-auto-1774273852-9"
        title = "Auto Rule 9"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword9" nocase
        $str_1 = "keyword10" nocase
        $str_2 = "keyword11" nocase
    condition:
        any of them
}

rule sigma_auto_1774274351_13 {
    meta:
        id = "sigma-auto-1774274351-13"
        title = "Auto Rule 13"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword13" nocase
        $str_1 = "keyword14" nocase
        $str_2 = "keyword15" nocase
    condition:
        any of them
}

rule sigma_auto_1774273351_0 {
    meta:
        id = "sigma-auto-1774273351-0"
        title = "Auto Rule 0"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword0" nocase
        $str_1 = "keyword1" nocase
        $str_2 = "keyword2" nocase
    condition:
        any of them
}

rule sigma_auto_1774274181_11 {
    meta:
        id = "sigma-auto-1774274181-11"
        title = "Auto Rule 11"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword11" nocase
        $str_1 = "keyword12" nocase
        $str_2 = "keyword13" nocase
    condition:
        any of them
}

rule sigma_auto_1774273666_6 {
    meta:
        id = "sigma-auto-1774273666-6"
        title = "Auto Rule 6"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword6" nocase
        $str_1 = "keyword7" nocase
        $str_2 = "keyword8" nocase
    condition:
        any of them
}

rule sigma_auto_1774272786_26 {
    meta:
        id = "sigma-auto-1774272786-26"
        title = "Auto Rule 26"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword26" nocase
        $str_1 = "keyword27" nocase
        $str_2 = "keyword28" nocase
    condition:
        any of them
}

rule sigma_auto_1774273525_6 {
    meta:
        id = "sigma-auto-1774273525-6"
        title = "Auto Rule 6"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword6" nocase
        $str_1 = "keyword7" nocase
        $str_2 = "keyword8" nocase
    condition:
        any of them
}

rule sigma_auto_1774274902_1 {
    meta:
        id = "sigma-auto-1774274902-1"
        title = "Auto Rule 1"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword1" nocase
        $str_1 = "keyword2" nocase
        $str_2 = "keyword3" nocase
    condition:
        any of them
}

rule sigma_auto_1774273730_21 {
    meta:
        id = "sigma-auto-1774273730-21"
        title = "Auto Rule 21"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword21" nocase
        $str_1 = "keyword22" nocase
        $str_2 = "keyword23" nocase
    condition:
        any of them
}

rule sigma_auto_1774274240_25 {
    meta:
        id = "sigma-auto-1774274240-25"
        title = "Auto Rule 25"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword25" nocase
        $str_1 = "keyword26" nocase
        $str_2 = "keyword27" nocase
    condition:
        any of them
}

rule sigma_auto_1774273049_21 {
    meta:
        id = "sigma-auto-1774273049-21"
        title = "Auto Rule 21"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword21" nocase
        $str_1 = "keyword22" nocase
        $str_2 = "keyword23" nocase
    condition:
        any of them
}

rule sigma_auto_1774274442_3 {
    meta:
        id = "sigma-auto-1774274442-3"
        title = "Auto Rule 3"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword3" nocase
        $str_1 = "keyword4" nocase
        $str_2 = "keyword5" nocase
    condition:
        any of them
}

rule sigma_auto_1774274923_6 {
    meta:
        id = "sigma-auto-1774274923-6"
        title = "Auto Rule 6"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword6" nocase
        $str_1 = "keyword7" nocase
        $str_2 = "keyword8" nocase
    condition:
        any of them
}

rule sigma_auto_1774274001_5 {
    meta:
        id = "sigma-auto-1774274001-5"
        title = "Auto Rule 5"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword5" nocase
        $str_1 = "keyword6" nocase
        $str_2 = "keyword7" nocase
    condition:
        any of them
}

rule sigma_auto_1774272765_21 {
    meta:
        id = "sigma-auto-1774272765-21"
        title = "Auto Rule 21"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword21" nocase
        $str_1 = "keyword22" nocase
        $str_2 = "keyword23" nocase
    condition:
        any of them
}

rule sigma_auto_1774272723_11 {
    meta:
        id = "sigma-auto-1774272723-11"
        title = "Auto Rule 11"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword11" nocase
        $str_1 = "keyword12" nocase
        $str_2 = "keyword13" nocase
    condition:
        any of them
}

rule sigma_auto_1774273220_0 {
    meta:
        id = "sigma-auto-1774273220-0"
        title = "Auto Rule 0"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword0" nocase
        $str_1 = "keyword1" nocase
        $str_2 = "keyword2" nocase
    condition:
        any of them
}

rule sigma_auto_1774273171_18 {
    meta:
        id = "sigma-auto-1774273171-18"
        title = "Auto Rule 18"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword18" nocase
        $str_1 = "keyword19" nocase
        $str_2 = "keyword20" nocase
    condition:
        any of them
}

rule sigma_auto_1774274064_20 {
    meta:
        id = "sigma-auto-1774274064-20"
        title = "Auto Rule 20"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword20" nocase
        $str_1 = "keyword21" nocase
        $str_2 = "keyword22" nocase
    condition:
        any of them
}

rule sigma_auto_1774273662_5 {
    meta:
        id = "sigma-auto-1774273662-5"
        title = "Auto Rule 5"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword5" nocase
        $str_1 = "keyword6" nocase
        $str_2 = "keyword7" nocase
    condition:
        any of them
}

rule sigma_auto_1774272396_5 {
    meta:
        id = "sigma-auto-1774272396-5"
        title = "Auto Rule 5"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword5" nocase
        $str_1 = "keyword6" nocase
        $str_2 = "keyword7" nocase
    condition:
        any of them
}

rule sigma_auto_1774273555_13 {
    meta:
        id = "sigma-auto-1774273555-13"
        title = "Auto Rule 13"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword13" nocase
        $str_1 = "keyword14" nocase
        $str_2 = "keyword15" nocase
    condition:
        any of them
}

rule sigma_auto_1774273003_10 {
    meta:
        id = "sigma-auto-1774273003-10"
        title = "Auto Rule 10"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword10" nocase
        $str_1 = "keyword11" nocase
        $str_2 = "keyword12" nocase
    condition:
        any of them
}

rule sigma_auto_1774275147_25 {
    meta:
        id = "sigma-auto-1774275147-25"
        title = "Auto Rule 25"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword25" nocase
        $str_1 = "keyword26" nocase
        $str_2 = "keyword27" nocase
    condition:
        any of them
}

rule sigma_auto_1774274814_16 {
    meta:
        id = "sigma-auto-1774274814-16"
        title = "Auto Rule 16"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword16" nocase
        $str_1 = "keyword17" nocase
        $str_2 = "keyword18" nocase
    condition:
        any of them
}

rule sigma_auto_1774274434_1 {
    meta:
        id = "sigma-auto-1774274434-1"
        title = "Auto Rule 1"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword1" nocase
        $str_1 = "keyword2" nocase
        $str_2 = "keyword3" nocase
    condition:
        any of them
}

rule sigma_auto_1774274960_15 {
    meta:
        id = "sigma-auto-1774274960-15"
        title = "Auto Rule 15"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword15" nocase
        $str_1 = "keyword16" nocase
        $str_2 = "keyword17" nocase
    condition:
        any of them
}

rule sigma_auto_1774272680_1 {
    meta:
        id = "sigma-auto-1774272680-1"
        title = "Auto Rule 1"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword1" nocase
        $str_1 = "keyword2" nocase
        $str_2 = "keyword3" nocase
    condition:
        any of them
}

rule sigma_auto_1774274343_11 {
    meta:
        id = "sigma-auto-1774274343-11"
        title = "Auto Rule 11"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword11" nocase
        $str_1 = "keyword12" nocase
        $str_2 = "keyword13" nocase
    condition:
        any of them
}

rule sigma_auto_1774272580_9 {
    meta:
        id = "sigma-auto-1774272580-9"
        title = "Auto Rule 9"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword9" nocase
        $str_1 = "keyword10" nocase
        $str_2 = "keyword11" nocase
    condition:
        any of them
}

rule sigma_auto_1774273163_16 {
    meta:
        id = "sigma-auto-1774273163-16"
        title = "Auto Rule 16"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword16" nocase
        $str_1 = "keyword17" nocase
        $str_2 = "keyword18" nocase
    condition:
        any of them
}

rule sigma_auto_1774273274_13 {
    meta:
        id = "sigma-auto-1774273274-13"
        title = "Auto Rule 13"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword13" nocase
        $str_1 = "keyword14" nocase
        $str_2 = "keyword15" nocase
    condition:
        any of them
}

rule sigma_auto_1774272986_6 {
    meta:
        id = "sigma-auto-1774272986-6"
        title = "Auto Rule 6"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword6" nocase
        $str_1 = "keyword7" nocase
        $str_2 = "keyword8" nocase
    condition:
        any of them
}

rule sigma_auto_1774273108_3 {
    meta:
        id = "sigma-auto-1774273108-3"
        title = "Auto Rule 3"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword3" nocase
        $str_1 = "keyword4" nocase
        $str_2 = "keyword5" nocase
    condition:
        any of them
}

rule sigma_auto_1774273869_13 {
    meta:
        id = "sigma-auto-1774273869-13"
        title = "Auto Rule 13"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword13" nocase
        $str_1 = "keyword14" nocase
        $str_2 = "keyword15" nocase
    condition:
        any of them
}

rule sigma_auto_1774274918_5 {
    meta:
        id = "sigma-auto-1774274918-5"
        title = "Auto Rule 5"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword5" nocase
        $str_1 = "keyword6" nocase
        $str_2 = "keyword7" nocase
    condition:
        any of them
}

rule sigma_auto_1774272871_8 {
    meta:
        id = "sigma-auto-1774272871-8"
        title = "Auto Rule 8"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword8" nocase
        $str_1 = "keyword9" nocase
        $str_2 = "keyword10" nocase
    condition:
        any of them
}

rule sigma_auto_1774272901_15 {
    meta:
        id = "sigma-auto-1774272901-15"
        title = "Auto Rule 15"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword15" nocase
        $str_1 = "keyword16" nocase
        $str_2 = "keyword17" nocase
    condition:
        any of them
}

rule sigma_auto_1774273708_16 {
    meta:
        id = "sigma-auto-1774273708-16"
        title = "Auto Rule 16"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword16" nocase
        $str_1 = "keyword17" nocase
        $str_2 = "keyword18" nocase
    condition:
        any of them
}

rule sigma_auto_1774274609_3 {
    meta:
        id = "sigma-auto-1774274609-3"
        title = "Auto Rule 3"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword3" nocase
        $str_1 = "keyword4" nocase
        $str_2 = "keyword5" nocase
    condition:
        any of them
}

rule sigma_auto_1774272559_4 {
    meta:
        id = "sigma-auto-1774272559-4"
        title = "Auto Rule 4"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword4" nocase
        $str_1 = "keyword5" nocase
        $str_2 = "keyword6" nocase
    condition:
        any of them
}

rule sigma_auto_1774275063_5 {
    meta:
        id = "sigma-auto-1774275063-5"
        title = "Auto Rule 5"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword5" nocase
        $str_1 = "keyword6" nocase
        $str_2 = "keyword7" nocase
    condition:
        any of them
}

rule sigma_auto_1774274780_8 {
    meta:
        id = "sigma-auto-1774274780-8"
        title = "Auto Rule 8"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword8" nocase
        $str_1 = "keyword9" nocase
        $str_2 = "keyword10" nocase
    condition:
        any of them
}

rule sigma_auto_1774274488_14 {
    meta:
        id = "sigma-auto-1774274488-14"
        title = "Auto Rule 14"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword14" nocase
        $str_1 = "keyword15" nocase
        $str_2 = "keyword16" nocase
    condition:
        any of them
}

rule sigma_auto_1774272756_19 {
    meta:
        id = "sigma-auto-1774272756-19"
        title = "Auto Rule 19"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword19" nocase
        $str_1 = "keyword20" nocase
        $str_2 = "keyword21" nocase
    condition:
        any of them
}

rule sigma_auto_1774272896_14 {
    meta:
        id = "sigma-auto-1774272896-14"
        title = "Auto Rule 14"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword14" nocase
        $str_1 = "keyword15" nocase
        $str_2 = "keyword16" nocase
    condition:
        any of them
}

rule sigma_auto_1774273393_10 {
    meta:
        id = "sigma-auto-1774273393-10"
        title = "Auto Rule 10"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword10" nocase
        $str_1 = "keyword11" nocase
        $str_2 = "keyword12" nocase
    condition:
        any of them
}

rule sigma_auto_1774275046_1 {
    meta:
        id = "sigma-auto-1774275046-1"
        title = "Auto Rule 1"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword1" nocase
        $str_1 = "keyword2" nocase
        $str_2 = "keyword3" nocase
    condition:
        any of them
}

rule sigma_auto_1774272875_9 {
    meta:
        id = "sigma-auto-1774272875-9"
        title = "Auto Rule 9"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword9" nocase
        $str_1 = "keyword10" nocase
        $str_2 = "keyword11" nocase
    condition:
        any of them
}

rule sigma_auto_1774273513_3 {
    meta:
        id = "sigma-auto-1774273513-3"
        title = "Auto Rule 3"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword3" nocase
        $str_1 = "keyword4" nocase
        $str_2 = "keyword5" nocase
    condition:
        any of them
}

rule sigma_auto_1774274055_18 {
    meta:
        id = "sigma-auto-1774274055-18"
        title = "Auto Rule 18"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword18" nocase
        $str_1 = "keyword19" nocase
        $str_2 = "keyword20" nocase
    condition:
        any of them
}

rule sigma_auto_1774273112_4 {
    meta:
        id = "sigma-auto-1774273112-4"
        title = "Auto Rule 4"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword4" nocase
        $str_1 = "keyword5" nocase
        $str_2 = "keyword6" nocase
    condition:
        any of them
}

rule sigma_auto_1774274244_26 {
    meta:
        id = "sigma-auto-1774274244-26"
        title = "Auto Rule 26"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword26" nocase
        $str_1 = "keyword27" nocase
        $str_2 = "keyword28" nocase
    condition:
        any of them
}

rule sigma_auto_1774273045_20 {
    meta:
        id = "sigma-auto-1774273045-20"
        title = "Auto Rule 20"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword20" nocase
        $str_1 = "keyword21" nocase
        $str_2 = "keyword22" nocase
    condition:
        any of them
}

rule sigma_auto_1774272689_3 {
    meta:
        id = "sigma-auto-1774272689-3"
        title = "Auto Rule 3"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword3" nocase
        $str_1 = "keyword4" nocase
        $str_2 = "keyword5" nocase
    condition:
        any of them
}

rule sigma_auto_1774274463_8 {
    meta:
        id = "sigma-auto-1774274463-8"
        title = "Auto Rule 8"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword8" nocase
        $str_1 = "keyword9" nocase
        $str_2 = "keyword10" nocase
    condition:
        any of them
}

rule sigma_auto_1774273700_14 {
    meta:
        id = "sigma-auto-1774273700-14"
        title = "Auto Rule 14"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword14" nocase
        $str_1 = "keyword15" nocase
        $str_2 = "keyword16" nocase
    condition:
        any of them
}

rule sigma_auto_1774275080_9 {
    meta:
        id = "sigma-auto-1774275080-9"
        title = "Auto Rule 9"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword9" nocase
        $str_1 = "keyword10" nocase
        $str_2 = "keyword11" nocase
    condition:
        any of them
}

rule sigma_auto_1774272610_16 {
    meta:
        id = "sigma-auto-1774272610-16"
        title = "Auto Rule 16"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword16" nocase
        $str_1 = "keyword17" nocase
        $str_2 = "keyword18" nocase
    condition:
        any of them
}

rule sigma_auto_1774272760_20 {
    meta:
        id = "sigma-auto-1774272760-20"
        title = "Auto Rule 20"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword20" nocase
        $str_1 = "keyword21" nocase
        $str_2 = "keyword22" nocase
    condition:
        any of them
}

rule sigma_auto_1774274476_11 {
    meta:
        id = "sigma-auto-1774274476-11"
        title = "Auto Rule 11"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword11" nocase
        $str_1 = "keyword12" nocase
        $str_2 = "keyword13" nocase
    condition:
        any of them
}

rule sigma_auto_1774272961_0 {
    meta:
        id = "sigma-auto-1774272961-0"
        title = "Auto Rule 0"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword0" nocase
        $str_1 = "keyword1" nocase
        $str_2 = "keyword2" nocase
    condition:
        any of them
}

rule sigma_auto_1774275109_16 {
    meta:
        id = "sigma-auto-1774275109-16"
        title = "Auto Rule 16"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword16" nocase
        $str_1 = "keyword17" nocase
        $str_2 = "keyword18" nocase
    condition:
        any of them
}

rule sigma_auto_1774274301_1 {
    meta:
        id = "sigma-auto-1774274301-1"
        title = "Auto Rule 1"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword1" nocase
        $str_1 = "keyword2" nocase
        $str_2 = "keyword3" nocase
    condition:
        any of them
}

rule sigma_auto_1774274152_4 {
    meta:
        id = "sigma-auto-1774274152-4"
        title = "Auto Rule 4"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword4" nocase
        $str_1 = "keyword5" nocase
        $str_2 = "keyword6" nocase
    condition:
        any of them
}

rule sigma_auto_1774273175_19 {
    meta:
        id = "sigma-auto-1774273175-19"
        title = "Auto Rule 19"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword19" nocase
        $str_1 = "keyword20" nocase
        $str_2 = "keyword21" nocase
    condition:
        any of them
}

rule sigma_auto_1774273385_8 {
    meta:
        id = "sigma-auto-1774273385-8"
        title = "Auto Rule 8"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword8" nocase
        $str_1 = "keyword9" nocase
        $str_2 = "keyword10" nocase
    condition:
        any of them
}

rule sigma_auto_1774274156_5 {
    meta:
        id = "sigma-auto-1774274156-5"
        title = "Auto Rule 5"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword5" nocase
        $str_1 = "keyword6" nocase
        $str_2 = "keyword7" nocase
    condition:
        any of them
}

rule sigma_auto_1774272905_16 {
    meta:
        id = "sigma-auto-1774272905-16"
        title = "Auto Rule 16"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword16" nocase
        $str_1 = "keyword17" nocase
        $str_2 = "keyword18" nocase
    condition:
        any of them
}

rule sigma_auto_1774272443_16 {
    meta:
        id = "sigma-auto-1774272443-16"
        title = "Auto Rule 16"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword16" nocase
        $str_1 = "keyword17" nocase
        $str_2 = "keyword18" nocase
    condition:
        any of them
}

rule sigma_auto_1774274429_0 {
    meta:
        id = "sigma-auto-1774274429-0"
        title = "Auto Rule 0"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword0" nocase
        $str_1 = "keyword1" nocase
        $str_2 = "keyword2" nocase
    condition:
        any of them
}

rule sigma_auto_1774274784_9 {
    meta:
        id = "sigma-auto-1774274784-9"
        title = "Auto Rule 9"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword9" nocase
        $str_1 = "keyword10" nocase
        $str_2 = "keyword11" nocase
    condition:
        any of them
}

rule sigma_auto_1774275101_14 {
    meta:
        id = "sigma-auto-1774275101-14"
        title = "Auto Rule 14"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword14" nocase
        $str_1 = "keyword15" nocase
        $str_2 = "keyword16" nocase
    condition:
        any of them
}

rule sigma_auto_1774274160_6 {
    meta:
        id = "sigma-auto-1774274160-6"
        title = "Auto Rule 6"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword6" nocase
        $str_1 = "keyword7" nocase
        $str_2 = "keyword8" nocase
    condition:
        any of them
}

rule sigma_auto_1774273028_16 {
    meta:
        id = "sigma-auto-1774273028-16"
        title = "Auto Rule 16"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword16" nocase
        $str_1 = "keyword17" nocase
        $str_2 = "keyword18" nocase
    condition:
        any of them
}

rule sigma_auto_1774272693_4 {
    meta:
        id = "sigma-auto-1774272693-4"
        title = "Auto Rule 4"
        description = "Auto-generated rule for data_exfil"
        level = "high"
        tags = "data_exfil"
        source = "sigma_local"
    strings:
        $str_0 = "keyword4" nocase
        $str_1 = "keyword5" nocase
        $str_2 = "keyword6" nocase
    condition:
        any of them
}

rule sigma_auto_1774274072_22 {
    meta:
        id = "sigma-auto-1774274072-22"
        title = "Auto Rule 22"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword22" nocase
        $str_1 = "keyword23" nocase
        $str_2 = "keyword24" nocase
    condition:
        any of them
}

rule sigma_auto_1774274185_12 {
    meta:
        id = "sigma-auto-1774274185-12"
        title = "Auto Rule 12"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword12" nocase
        $str_1 = "keyword13" nocase
        $str_2 = "keyword14" nocase
    condition:
        any of them
}

rule sigma_auto_1774272769_22 {
    meta:
        id = "sigma-auto-1774272769-22"
        title = "Auto Rule 22"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword22" nocase
        $str_1 = "keyword23" nocase
        $str_2 = "keyword24" nocase
    condition:
        any of them
}

rule sigma_auto_1774273011_12 {
    meta:
        id = "sigma-auto-1774273011-12"
        title = "Auto Rule 12"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword12" nocase
        $str_1 = "keyword13" nocase
        $str_2 = "keyword14" nocase
    condition:
        any of them
}

rule sigma_auto_1774275093_12 {
    meta:
        id = "sigma-auto-1774275093-12"
        title = "Auto Rule 12"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword12" nocase
        $str_1 = "keyword13" nocase
        $str_2 = "keyword14" nocase
    condition:
        any of them
}

rule sigma_auto_1774273593_22 {
    meta:
        id = "sigma-auto-1774273593-22"
        title = "Auto Rule 22"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword22" nocase
        $str_1 = "keyword23" nocase
        $str_2 = "keyword24" nocase
    condition:
        any of them
}

rule sigma_tool_poisoning_005 {
    meta:
        id = "sigma-tool-poisoning-005"
        title = "Detect Tool Poisoning - Variant 005"
        description = "恶意使用工具/函数执行危险操作 (变体 5)"
        level = "critical"
        tags = "attack.tool_poisoning, mitre.ATLAS-T0002, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "compile " nocase
    condition:
        any of them
}

rule sigma_auto_1774274522_22 {
    meta:
        id = "sigma-auto-1774274522-22"
        title = "Auto Rule 22"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword22" nocase
        $str_1 = "keyword23" nocase
        $str_2 = "keyword24" nocase
    condition:
        any of them
}

rule sigma_auto_1774272685_2 {
    meta:
        id = "sigma-auto-1774272685-2"
        title = "Auto Rule 2"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword2" nocase
        $str_1 = "keyword3" nocase
        $str_2 = "keyword4" nocase
    condition:
        any of them
}

rule sigma_auto_1774274755_2 {
    meta:
        id = "sigma-auto-1774274755-2"
        title = "Auto Rule 2"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword2" nocase
        $str_1 = "keyword3" nocase
        $str_2 = "keyword4" nocase
    condition:
        any of them
}

rule sigma_auto_1774273650_2 {
    meta:
        id = "sigma-auto-1774273650-2"
        title = "Auto Rule 2"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword2" nocase
        $str_1 = "keyword3" nocase
        $str_2 = "keyword4" nocase
    condition:
        any of them
}

rule sigma_auto_1774273551_12 {
    meta:
        id = "sigma-auto-1774273551-12"
        title = "Auto Rule 12"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword12" nocase
        $str_1 = "keyword13" nocase
        $str_2 = "keyword14" nocase
    condition:
        any of them
}

rule sigma_auto_1774273228_2 {
    meta:
        id = "sigma-auto-1774273228-2"
        title = "Auto Rule 2"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword2" nocase
        $str_1 = "keyword3" nocase
        $str_2 = "keyword4" nocase
    condition:
        any of them
}

rule sigma_auto_1774273054_22 {
    meta:
        id = "sigma-auto-1774273054-22"
        title = "Auto Rule 22"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword22" nocase
        $str_1 = "keyword23" nocase
        $str_2 = "keyword24" nocase
    condition:
        any of them
}

rule sigma_auto_1774272551_2 {
    meta:
        id = "sigma-auto-1774272551-2"
        title = "Auto Rule 2"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword2" nocase
        $str_1 = "keyword3" nocase
        $str_2 = "keyword4" nocase
    condition:
        any of them
}

rule sigma_auto_1774274480_12 {
    meta:
        id = "sigma-auto-1774274480-12"
        title = "Auto Rule 12"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword12" nocase
        $str_1 = "keyword13" nocase
        $str_2 = "keyword14" nocase
    condition:
        any of them
}

rule sigma_auto_1774273360_2 {
    meta:
        id = "sigma-auto-1774273360-2"
        title = "Auto Rule 2"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword2" nocase
        $str_1 = "keyword3" nocase
        $str_2 = "keyword4" nocase
    condition:
        any of them
}

rule sigma_auto_1774274797_12 {
    meta:
        id = "sigma-auto-1774274797-12"
        title = "Auto Rule 12"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword12" nocase
        $str_1 = "keyword13" nocase
        $str_2 = "keyword14" nocase
    condition:
        any of them
}

rule sigma_auto_1774272969_2 {
    meta:
        id = "sigma-auto-1774272969-2"
        title = "Auto Rule 2"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword2" nocase
        $str_1 = "keyword3" nocase
        $str_2 = "keyword4" nocase
    condition:
        any of them
}

rule sigma_auto_1774274347_12 {
    meta:
        id = "sigma-auto-1774274347-12"
        title = "Auto Rule 12"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword12" nocase
        $str_1 = "keyword13" nocase
        $str_2 = "keyword14" nocase
    condition:
        any of them
}

rule sigma_tool_poisoning_002 {
    meta:
        id = "sigma-tool-poisoning-002"
        title = "Detect Tool Poisoning - Variant 002"
        description = "恶意使用工具/函数执行危险操作 (变体 2)"
        level = "critical"
        tags = "attack.tool_poisoning, mitre.ATLAS-T0002, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "subprocess.call|run|Popen " nocase
    condition:
        any of them
}

rule sigma_auto_1774273508_2 {
    meta:
        id = "sigma-auto-1774273508-2"
        title = "Auto Rule 2"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword2" nocase
        $str_1 = "keyword3" nocase
        $str_2 = "keyword4" nocase
    condition:
        any of them
}

rule sigma_auto_1774275051_2 {
    meta:
        id = "sigma-auto-1774275051-2"
        title = "Auto Rule 2"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword2" nocase
        $str_1 = "keyword3" nocase
        $str_2 = "keyword4" nocase
    condition:
        any of them
}

rule sigma_auto_1774272426_12 {
    meta:
        id = "sigma-auto-1774272426-12"
        title = "Auto Rule 12"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword12" nocase
        $str_1 = "keyword13" nocase
        $str_2 = "keyword14" nocase
    condition:
        any of them
}

rule sigma_tool_poisoning_003 {
    meta:
        id = "sigma-tool-poisoning-003"
        title = "Detect Tool Poisoning - Variant 003"
        description = "恶意使用工具/函数执行危险操作 (变体 3)"
        level = "critical"
        tags = "attack.tool_poisoning, mitre.ATLAS-T0002, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "eval " nocase
    condition:
        any of them
}

rule sigma_tool_poisoning_001 {
    meta:
        id = "sigma-tool-poisoning-001"
        title = "Detect Tool Poisoning - Variant 001"
        description = "恶意使用工具/函数执行危险操作 (变体 1)"
        level = "critical"
        tags = "attack.tool_poisoning, mitre.ATLAS-T0002, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "os.popen " nocase
    condition:
        any of them
}

rule sigma_auto_1774273692_12 {
    meta:
        id = "sigma-auto-1774273692-12"
        title = "Auto Rule 12"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword12" nocase
        $str_1 = "keyword13" nocase
        $str_2 = "keyword14" nocase
    condition:
        any of them
}

rule sigma_auto_1774272846_2 {
    meta:
        id = "sigma-auto-1774272846-2"
        title = "Auto Rule 2"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword2" nocase
        $str_1 = "keyword3" nocase
        $str_2 = "keyword4" nocase
    condition:
        any of them
}

rule sigma_auto_1774274647_12 {
    meta:
        id = "sigma-auto-1774274647-12"
        title = "Auto Rule 12"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword12" nocase
        $str_1 = "keyword13" nocase
        $str_2 = "keyword14" nocase
    condition:
        any of them
}

rule sigma_auto_1774273104_2 {
    meta:
        id = "sigma-auto-1774273104-2"
        title = "Auto Rule 2"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword2" nocase
        $str_1 = "keyword3" nocase
        $str_2 = "keyword4" nocase
    condition:
        any of them
}

rule sigma_tool_poisoning_004 {
    meta:
        id = "sigma-tool-poisoning-004"
        title = "Detect Tool Poisoning - Variant 004"
        description = "恶意使用工具/函数执行危险操作 (变体 4)"
        level = "critical"
        tags = "attack.tool_poisoning, mitre.ATLAS-T0002, ai-security, skill-scanner"
        source = "sigma_local"
    strings:
        $str_0 = "exec " nocase
    condition:
        any of them
}

rule sigma_auto_1774274227_22 {
    meta:
        id = "sigma-auto-1774274227-22"
        title = "Auto Rule 22"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword22" nocase
        $str_1 = "keyword23" nocase
        $str_2 = "keyword24" nocase
    condition:
        any of them
}

rule sigma_auto_1774273402_12 {
    meta:
        id = "sigma-auto-1774273402-12"
        title = "Auto Rule 12"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword12" nocase
        $str_1 = "keyword13" nocase
        $str_2 = "keyword14" nocase
    condition:
        any of them
}

rule sigma_auto_1774273865_12 {
    meta:
        id = "sigma-auto-1774273865-12"
        title = "Auto Rule 12"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword12" nocase
        $str_1 = "keyword13" nocase
        $str_2 = "keyword14" nocase
    condition:
        any of them
}

rule sigma_auto_1774272727_12 {
    meta:
        id = "sigma-auto-1774272727-12"
        title = "Auto Rule 12"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword12" nocase
        $str_1 = "keyword13" nocase
        $str_2 = "keyword14" nocase
    condition:
        any of them
}

rule sigma_auto_1774272384_2 {
    meta:
        id = "sigma-auto-1774272384-2"
        title = "Auto Rule 2"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword2" nocase
        $str_1 = "keyword3" nocase
        $str_2 = "keyword4" nocase
    condition:
        any of them
}

rule sigma_auto_1774273146_12 {
    meta:
        id = "sigma-auto-1774273146-12"
        title = "Auto Rule 12"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword12" nocase
        $str_1 = "keyword13" nocase
        $str_2 = "keyword14" nocase
    condition:
        any of them
}

rule sigma_auto_1774272593_12 {
    meta:
        id = "sigma-auto-1774272593-12"
        title = "Auto Rule 12"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword12" nocase
        $str_1 = "keyword13" nocase
        $str_2 = "keyword14" nocase
    condition:
        any of them
}

rule sigma_auto_1774274030_12 {
    meta:
        id = "sigma-auto-1774274030-12"
        title = "Auto Rule 12"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword12" nocase
        $str_1 = "keyword13" nocase
        $str_2 = "keyword14" nocase
    condition:
        any of them
}

rule sigma_auto_1774274689_22 {
    meta:
        id = "sigma-auto-1774274689-22"
        title = "Auto Rule 22"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword22" nocase
        $str_1 = "keyword23" nocase
        $str_2 = "keyword24" nocase
    condition:
        any of them
}

rule sigma_auto_1774273270_12 {
    meta:
        id = "sigma-auto-1774273270-12"
        title = "Auto Rule 12"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword12" nocase
        $str_1 = "keyword13" nocase
        $str_2 = "keyword14" nocase
    condition:
        any of them
}

rule sigma_auto_1774274948_12 {
    meta:
        id = "sigma-auto-1774274948-12"
        title = "Auto Rule 12"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword12" nocase
        $str_1 = "keyword13" nocase
        $str_2 = "keyword14" nocase
    condition:
        any of them
}

rule sigma_auto_1774275135_22 {
    meta:
        id = "sigma-auto-1774275135-22"
        title = "Auto Rule 22"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword22" nocase
        $str_1 = "keyword23" nocase
        $str_2 = "keyword24" nocase
    condition:
        any of them
}

rule sigma_auto_1774274438_2 {
    meta:
        id = "sigma-auto-1774274438-2"
        title = "Auto Rule 2"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword2" nocase
        $str_1 = "keyword3" nocase
        $str_2 = "keyword4" nocase
    condition:
        any of them
}

rule sigma_auto_1774274305_2 {
    meta:
        id = "sigma-auto-1774274305-2"
        title = "Auto Rule 2"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword2" nocase
        $str_1 = "keyword3" nocase
        $str_2 = "keyword4" nocase
    condition:
        any of them
}

rule sigma_auto_1774273823_2 {
    meta:
        id = "sigma-auto-1774273823-2"
        title = "Auto Rule 2"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword2" nocase
        $str_1 = "keyword3" nocase
        $str_2 = "keyword4" nocase
    condition:
        any of them
}

rule sigma_auto_1774273734_22 {
    meta:
        id = "sigma-auto-1774273734-22"
        title = "Auto Rule 22"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword22" nocase
        $str_1 = "keyword23" nocase
        $str_2 = "keyword24" nocase
    condition:
        any of them
}

rule sigma_auto_1774273988_2 {
    meta:
        id = "sigma-auto-1774273988-2"
        title = "Auto Rule 2"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword2" nocase
        $str_1 = "keyword3" nocase
        $str_2 = "keyword4" nocase
    condition:
        any of them
}

rule sigma_auto_1774272888_12 {
    meta:
        id = "sigma-auto-1774272888-12"
        title = "Auto Rule 12"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword12" nocase
        $str_1 = "keyword13" nocase
        $str_2 = "keyword14" nocase
    condition:
        any of them
}

rule sigma_auto_1774274389_22 {
    meta:
        id = "sigma-auto-1774274389-22"
        title = "Auto Rule 22"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword22" nocase
        $str_1 = "keyword23" nocase
        $str_2 = "keyword24" nocase
    condition:
        any of them
}

rule sigma_auto_1774274906_2 {
    meta:
        id = "sigma-auto-1774274906-2"
        title = "Auto Rule 2"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword2" nocase
        $str_1 = "keyword3" nocase
        $str_2 = "keyword4" nocase
    condition:
        any of them
}

rule sigma_auto_1774274143_2 {
    meta:
        id = "sigma-auto-1774274143-2"
        title = "Auto Rule 2"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword2" nocase
        $str_1 = "keyword3" nocase
        $str_2 = "keyword4" nocase
    condition:
        any of them
}

rule sigma_auto_1774272468_22 {
    meta:
        id = "sigma-auto-1774272468-22"
        title = "Auto Rule 22"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword22" nocase
        $str_1 = "keyword23" nocase
        $str_2 = "keyword24" nocase
    condition:
        any of them
}

rule sigma_auto_1774274605_2 {
    meta:
        id = "sigma-auto-1774274605-2"
        title = "Auto Rule 2"
        description = "Auto-generated rule for tool_poisoning"
        level = "high"
        tags = "tool_poisoning"
        source = "sigma_local"
    strings:
        $str_0 = "keyword2" nocase
        $str_1 = "keyword3" nocase
        $str_2 = "keyword4" nocase
    condition:
        any of them
}



// supply_chain rules



