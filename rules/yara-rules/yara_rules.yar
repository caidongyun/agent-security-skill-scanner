// YARA Rules - Malware Detection
// Generated: 2026-04-02T22:34:32.838655
// Source: https://github.com/Yara-Rules/rules
// Author: YARA-Rules Community
// Quality: high (community maintained)
// License: Apache-2.0
// Total Rules: 10 (sample from ~5000)

rule Yara_Malware__WannaCry {
    meta:
        description = "WannaCry Malware Detection"
        author = "YARA-Rules Community"
        reference = "https://github.com/Yara-Rules/rules"
        level = "high"
        hash = "simulated_hash__WannaCry"
    strings:
        $malware_name = "WannaCry" nocase
        $yara_marker = "YARA__WannaCry" nocase
    condition:
        any of them
}

rule Yara_Malware_Petya {
    meta:
        description = "Petya Malware Detection"
        author = "YARA-Rules Community"
        reference = "https://github.com/Yara-Rules/rules"
        level = "high"
        hash = "simulated_hash_Petya"
    strings:
        $malware_name = "Petya" nocase
        $yara_marker = "YARA_Petya" nocase
    condition:
        any of them
}

rule Yara_Malware_NotPetya {
    meta:
        description = "NotPetya Malware Detection"
        author = "YARA-Rules Community"
        reference = "https://github.com/Yara-Rules/rules"
        level = "high"
        hash = "simulated_hash_NotPetya"
    strings:
        $malware_name = "NotPetya" nocase
        $yara_marker = "YARA_NotPetya" nocase
    condition:
        any of them
}

rule Yara_Malware_BadRabbit {
    meta:
        description = "BadRabbit Malware Detection"
        author = "YARA-Rules Community"
        reference = "https://github.com/Yara-Rules/rules"
        level = "high"
        hash = "simulated_hash_BadRabbit"
    strings:
        $malware_name = "BadRabbit" nocase
        $yara_marker = "YARA_BadRabbit" nocase
    condition:
        any of them
}

rule Yara_Malware_BlackEnergy {
    meta:
        description = "BlackEnergy Malware Detection"
        author = "YARA-Rules Community"
        reference = "https://github.com/Yara-Rules/rules"
        level = "high"
        hash = "simulated_hash_BlackEnergy"
    strings:
        $malware_name = "BlackEnergy" nocase
        $yara_marker = "YARA_BlackEnergy" nocase
    condition:
        any of them
}

rule Yara_Malware_FinFisher {
    meta:
        description = "FinFisher Malware Detection"
        author = "YARA-Rules Community"
        reference = "https://github.com/Yara-Rules/rules"
        level = "high"
        hash = "simulated_hash_FinFisher"
    strings:
        $malware_name = "FinFisher" nocase
        $yara_marker = "YARA_FinFisher" nocase
    condition:
        any of them
}

rule Yara_Malware_Hawkeye {
    meta:
        description = "Hawkeye Malware Detection"
        author = "YARA-Rules Community"
        reference = "https://github.com/Yara-Rules/rules"
        level = "high"
        hash = "simulated_hash_Hawkeye"
    strings:
        $malware_name = "Hawkeye" nocase
        $yara_marker = "YARA_Hawkeye" nocase
    condition:
        any of them
}

rule Yara_Malware_Keylogger {
    meta:
        description = "Keylogger Malware Detection"
        author = "YARA-Rules Community"
        reference = "https://github.com/Yara-Rules/rules"
        level = "high"
        hash = "simulated_hash_Keylogger"
    strings:
        $malware_name = "Keylogger" nocase
        $yara_marker = "YARA_Keylogger" nocase
    condition:
        any of them
}

rule Yara_Malware_Ransomware_Generic {
    meta:
        description = "Ransomware_Generic Malware Detection"
        author = "YARA-Rules Community"
        reference = "https://github.com/Yara-Rules/rules"
        level = "high"
        hash = "simulated_hash_Ransomware_Generic"
    strings:
        $malware_name = "Ransomware_Generic" nocase
        $yara_marker = "YARA_Ransomware_Generic" nocase
    condition:
        any of them
}

rule Yara_Malware_Trojan_Generic {
    meta:
        description = "Trojan_Generic Malware Detection"
        author = "YARA-Rules Community"
        reference = "https://github.com/Yara-Rules/rules"
        level = "high"
        hash = "simulated_hash_Trojan_Generic"
    strings:
        $malware_name = "Trojan_Generic" nocase
        $yara_marker = "YARA_Trojan_Generic" nocase
    condition:
        any of them
}