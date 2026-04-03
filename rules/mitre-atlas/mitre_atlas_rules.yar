// MITRE ATLAS Rules - AI/Agent Threats
// Generated: 2026-04-02T21:41:34.639297
// Source: https://atlas.mitre.org/
// Techniques: 8

rule MITRE_ATLAS_ATLAS_001 {
    meta:
        description = "LLM Prompt Injection"
        mitre_atlas = "ATLAS-001"
        tactic = "Initial Access"
        author = "MITRE ATLAS + Local Enhancement"
        date = "2026-04-02"
    strings:
        $technique_name = "LLM Prompt Injection" nocase
        $atlas_id = "ATLAS-001" nocase
    condition:
        any of them
}

rule MITRE_ATLAS_ATLAS_002 {
    meta:
        description = "Agent Tool Poisoning"
        mitre_atlas = "ATLAS-002"
        tactic = "Execution"
        author = "MITRE ATLAS + Local Enhancement"
        date = "2026-04-02"
    strings:
        $technique_name = "Agent Tool Poisoning" nocase
        $atlas_id = "ATLAS-002" nocase
    condition:
        any of them
}

rule MITRE_ATLAS_ATLAS_003 {
    meta:
        description = "Memory Pollution"
        mitre_atlas = "ATLAS-003"
        tactic = "Persistence"
        author = "MITRE ATLAS + Local Enhancement"
        date = "2026-04-02"
    strings:
        $technique_name = "Memory Pollution" nocase
        $atlas_id = "ATLAS-003" nocase
    condition:
        any of them
}

rule MITRE_ATLAS_ATLAS_004 {
    meta:
        description = "Data Exfiltration via LLM"
        mitre_atlas = "ATLAS-004"
        tactic = "Exfiltration"
        author = "MITRE ATLAS + Local Enhancement"
        date = "2026-04-02"
    strings:
        $technique_name = "Data Exfiltration via LLM" nocase
        $atlas_id = "ATLAS-004" nocase
    condition:
        any of them
}

rule MITRE_ATLAS_ATLAS_005 {
    meta:
        description = "Model Theft"
        mitre_atlas = "ATLAS-005"
        tactic = "Collection"
        author = "MITRE ATLAS + Local Enhancement"
        date = "2026-04-02"
    strings:
        $technique_name = "Model Theft" nocase
        $atlas_id = "ATLAS-005" nocase
    condition:
        any of them
}

rule MITRE_ATLAS_ATLAS_006 {
    meta:
        description = "Prompt Leakage"
        mitre_atlas = "ATLAS-006"
        tactic = "Discovery"
        author = "MITRE ATLAS + Local Enhancement"
        date = "2026-04-02"
    strings:
        $technique_name = "Prompt Leakage" nocase
        $atlas_id = "ATLAS-006" nocase
    condition:
        any of them
}

rule MITRE_ATLAS_ATLAS_007 {
    meta:
        description = "Agent Impersonation"
        mitre_atlas = "ATLAS-007"
        tactic = "Defense Evasion"
        author = "MITRE ATLAS + Local Enhancement"
        date = "2026-04-02"
    strings:
        $technique_name = "Agent Impersonation" nocase
        $atlas_id = "ATLAS-007" nocase
    condition:
        any of them
}

rule MITRE_ATLAS_ATLAS_008 {
    meta:
        description = "Training Data Poisoning"
        mitre_atlas = "ATLAS-008"
        tactic = "Initial Access"
        author = "MITRE ATLAS + Local Enhancement"
        date = "2026-04-02"
    strings:
        $technique_name = "Training Data Poisoning" nocase
        $atlas_id = "ATLAS-008" nocase
    condition:
        any of them
}