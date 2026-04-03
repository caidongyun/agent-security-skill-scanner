// Gitee Official Rules - Clean Version
// Generated: 2026-04-03
// Total: 561 rules

rule MALWARE_001 {
    meta:
        id = "MALWARE-001"
        category = "malware"
        severity = "CRITICAL"
        source = "gitee_official"
    strings:
        $str_0 = "eval\\s*\\([^)]+\\)"
        $str_1 = "exec\\s*\\([^)]+\\)"
    condition:
        any of them
}

rule MALWARE_002 {
    meta:
        id = "MALWARE-002"
        category = "malware"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "__import__\\s*\\([^)]+\\)"
        $str_1 = "importlib\\.import_module"
    condition:
        any of them
}

rule MALWARE_003 {
    meta:
        id = "MALWARE-003"
        category = "malware"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "requests\\.(get|post)"
        $str_1 = "verify\\s*=\\s*False"
    condition:
        any of them
}

rule MALWARE_004 {
    meta:
        id = "MALWARE-004"
        category = "malware"
        severity = "CRITICAL"
        source = "gitee_official"
    strings:
        $str_0 = "os\\.environ"
        $str_1 = "\\.send\\("
        $str_2 = "smtplib"
    condition:
        any of them
}

rule BACKDOOR_001 {
    meta:
        id = "BACKDOOR-001"
        category = "backdoor"
        severity = "CRITICAL"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess.*shell=True"
        $str_1 = "pty\\.spawn"
    condition:
        any of them
}

rule BACKDOOR_002 {
    meta:
        id = "BACKDOOR-002"
        category = "backdoor"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "cron"
        $str_1 = "systemd"
        $str_2 = "registry"
    condition:
        any of them
}

rule PRIV_001 {
    meta:
        id = "PRIV-001"
        category = "privilege"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo\\s+"
        $str_1 = "os\\.setuid"
    condition:
        any of them
}

rule PRIV_010 {
    meta:
        id = "PRIV-010"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "tooluse"
    condition:
        any of them
}

rule PRIV_011 {
    meta:
        id = "PRIV-011"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "files"
    condition:
        any of them
}

rule PRIV_012 {
    meta:
        id = "PRIV-012"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "loop"
    condition:
        any of them
}

rule PRIV_013 {
    meta:
        id = "PRIV-013"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "infinite"
    condition:
        any of them
}

rule PRIV_014 {
    meta:
        id = "PRIV-014"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "bash"
    condition:
        any of them
}

rule PRIV_015 {
    meta:
        id = "PRIV-015"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "pollution"
    condition:
        any of them
}

rule PRIV_016 {
    meta:
        id = "PRIV-016"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "commands"
    condition:
        any of them
}

rule PRIV_017 {
    meta:
        id = "PRIV-017"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "runner"
    condition:
        any of them
}

rule PRIV_018 {
    meta:
        id = "PRIV-018"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "executing"
    condition:
        any of them
}

rule PRIV_019 {
    meta:
        id = "PRIV-019"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "memory"
    condition:
        any of them
}

rule PRIV_020 {
    meta:
        id = "PRIV-020"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "automator"
    condition:
        any of them
}

rule PRIV_021 {
    meta:
        id = "PRIV-021"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "automation"
    condition:
        any of them
}

rule PRIV_022 {
    meta:
        id = "PRIV-022"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "exhaustion"
    condition:
        any of them
}

rule PRIV_023 {
    meta:
        id = "PRIV-023"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "resource"
    condition:
        any of them
}

rule PRIV_024 {
    meta:
        id = "PRIV-024"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "accessing"
    condition:
        any of them
}

rule PRIV_025 {
    meta:
        id = "PRIV-025"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "long"
    condition:
        any of them
}

rule PRIV_026 {
    meta:
        id = "PRIV-026"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "abuse"
    condition:
        any of them
}

rule PRIV_027 {
    meta:
        id = "PRIV-027"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "multi"
    condition:
        any of them
}

rule PRIV_028 {
    meta:
        id = "PRIV-028"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "sites"
    condition:
        any of them
}

rule PRIV_029 {
    meta:
        id = "PRIV-029"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "outside"
    condition:
        any of them
}

rule PRIV_030 {
    meta:
        id = "PRIV-030"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "corruption"
    condition:
        any of them
}

rule PRIV_031 {
    meta:
        id = "PRIV-031"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "token"
    condition:
        any of them
}

rule PRIV_032 {
    meta:
        id = "PRIV-032"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "playwright"
    condition:
        any of them
}

rule PRIV_033 {
    meta:
        id = "PRIV-033"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "hook"
    condition:
        any of them
}

rule PRIV_034 {
    meta:
        id = "PRIV-034"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "system"
    condition:
        any of them
}

rule PRIV_035 {
    meta:
        id = "PRIV-035"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "shell"
    condition:
        any of them
}

rule PRIV_036 {
    meta:
        id = "PRIV-036"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "context"
    condition:
        any of them
}

rule PRIV_037 {
    meta:
        id = "PRIV-037"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "optimizer"
    condition:
        any of them
}

rule PRIV_038 {
    meta:
        id = "PRIV-038"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "detection"
    condition:
        any of them
}

rule PRIV_039 {
    meta:
        id = "PRIV-039"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "term"
    condition:
        any of them
}

rule PRIV_040 {
    meta:
        id = "PRIV-040"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "browser"
    condition:
        any of them
}

rule PRIV_041 {
    meta:
        id = "PRIV-041"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "inspector"
    condition:
        any of them
}

rule PRIV_042 {
    meta:
        id = "PRIV-042"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "write"
    condition:
        any of them
}

rule PRIV_043 {
    meta:
        id = "PRIV-043"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "attack"
    condition:
        any of them
}

rule PRIV_044 {
    meta:
        id = "PRIV-044"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "workflow"
    condition:
        any of them
}

rule PRIV_045 {
    meta:
        id = "PRIV-045"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "manager"
    condition:
        any of them
}

rule PRIV_046 {
    meta:
        id = "PRIV-046"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "batch"
    condition:
        any of them
}

rule PRIV_047 {
    meta:
        id = "PRIV-047"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "analyzer"
    condition:
        any of them
}

rule PRIV_048 {
    meta:
        id = "PRIV-048"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "helper"
    condition:
        any of them
}

rule PRIV_049 {
    meta:
        id = "PRIV-049"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "sensitive"
    condition:
        any of them
}

rule PRIV_050 {
    meta:
        id = "PRIV-050"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "maximizer"
    condition:
        any of them
}

rule PRIV_051 {
    meta:
        id = "PRIV-051"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "description"
    condition:
        any of them
}

rule PRIV_052 {
    meta:
        id = "PRIV-052"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "processor"
    condition:
        any of them
}

rule PRIV_053 {
    meta:
        id = "PRIV-053"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "posttooluse"
    condition:
        any of them
}

rule PRIV_054 {
    meta:
        id = "PRIV-054"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "tool"
    condition:
        any of them
}

rule PRIV_055 {
    meta:
        id = "PRIV-055"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "project"
    condition:
        any of them
}

rule PRIV_056 {
    meta:
        id = "PRIV-056"
        category = "privilege"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "reading"
    condition:
        any of them
}

rule CRED_001 {
    meta:
        id = "CRED-001"
        category = "credential"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api[_-]?key"
        $str_1 = "secret"
        $str_2 = "password"
    condition:
        any of them
}

rule PROMPT_001 {
    meta:
        id = "PROMPT-001"
        category = "prompt_injection"
        severity = "CRITICAL"
        source = "gitee_official"
    strings:
        $str_0 = "ignore\\s+previous"
        $str_1 = "forget\\s+all"
    condition:
        any of them
}

rule PROMPT_002 {
    meta:
        id = "PROMPT-002"
        category = "prompt_injection"
        severity = "CRITICAL"
        source = "gitee_official"
    strings:
        $str_0 = "base64\\.b64decode"
        $str_1 = "b64decode"
    condition:
        any of them
}

rule PROMPT_003 {
    meta:
        id = "PROMPT-003"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "\\\\u[0-9a-f]{4}"
    condition:
        any of them
}

rule PROMPT_004 {
    meta:
        id = "PROMPT-004"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "SYSTEM_PROMPT"
        $str_1 = "system_prompt"
    condition:
        any of them
}

rule PROMPT_005 {
    meta:
        id = "PROMPT-005"
        category = "prompt_injection"
        severity = "CRITICAL"
        source = "gitee_official"
    strings:
        $str_0 = "<\\s*/\\s*instruction"
    condition:
        any of them
}

rule PROMPT_006 {
    meta:
        id = "PROMPT-006"
        category = "prompt_injection"
        severity = "CRITICAL"
        source = "gitee_official"
    strings:
        $str_0 = "dan.*jailbreak"
        $str_1 = "do.*anything.*now"
    condition:
        any of them
}

rule PROMPT_007 {
    meta:
        id = "PROMPT-007"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "you.*are.*now"
        $str_1 = "pretend.*to.*be"
    condition:
        any of them
}

rule PROMPT_008 {
    meta:
        id = "PROMPT-008"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_009 {
    meta:
        id = "PROMPT-009"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_010 {
    meta:
        id = "PROMPT-010"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_011 {
    meta:
        id = "PROMPT-011"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_012 {
    meta:
        id = "PROMPT-012"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_013 {
    meta:
        id = "PROMPT-013"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_014 {
    meta:
        id = "PROMPT-014"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_015 {
    meta:
        id = "PROMPT-015"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_016 {
    meta:
        id = "PROMPT-016"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_017 {
    meta:
        id = "PROMPT-017"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_018 {
    meta:
        id = "PROMPT-018"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_019 {
    meta:
        id = "PROMPT-019"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_020 {
    meta:
        id = "PROMPT-020"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_021 {
    meta:
        id = "PROMPT-021"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_022 {
    meta:
        id = "PROMPT-022"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_023 {
    meta:
        id = "PROMPT-023"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_024 {
    meta:
        id = "PROMPT-024"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_025 {
    meta:
        id = "PROMPT-025"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_026 {
    meta:
        id = "PROMPT-026"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_027 {
    meta:
        id = "PROMPT-027"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_028 {
    meta:
        id = "PROMPT-028"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_029 {
    meta:
        id = "PROMPT-029"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_030 {
    meta:
        id = "PROMPT-030"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_031 {
    meta:
        id = "PROMPT-031"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_032 {
    meta:
        id = "PROMPT-032"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_033 {
    meta:
        id = "PROMPT-033"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_034 {
    meta:
        id = "PROMPT-034"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_035 {
    meta:
        id = "PROMPT-035"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_036 {
    meta:
        id = "PROMPT-036"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_037 {
    meta:
        id = "PROMPT-037"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_038 {
    meta:
        id = "PROMPT-038"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_039 {
    meta:
        id = "PROMPT-039"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_040 {
    meta:
        id = "PROMPT-040"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_041 {
    meta:
        id = "PROMPT-041"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_042 {
    meta:
        id = "PROMPT-042"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_043 {
    meta:
        id = "PROMPT-043"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_044 {
    meta:
        id = "PROMPT-044"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_045 {
    meta:
        id = "PROMPT-045"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_046 {
    meta:
        id = "PROMPT-046"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule PROMPT_047 {
    meta:
        id = "PROMPT-047"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard"
        $str_3 = "new instruction"
        $str_4 = "role hijack"
    condition:
        any of them
}

rule THIRD_001 {
    meta:
        id = "THIRD-001"
        category = "third_party_content"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "fetch\\s*\\([^)]*https?://"
        $str_1 = "requests\\.get\\s*\\([^)]*https?://"
    condition:
        any of them
}

rule THIRD_002 {
    meta:
        id = "THIRD-002"
        category = "third_party_content"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "curl\\s+\\|\\s*bash"
        $str_1 = "wget\\s+.*\\|\\s*bash"
    condition:
        any of them
}

rule THIRD_003 {
    meta:
        id = "THIRD-003"
        category = "third_party_content"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "eval\\s*\\(\\s*__import__"
        $str_1 = "exec\\s*\\(\\s*__import__"
    condition:
        any of them
}

rule THIRD_004 {
    meta:
        id = "THIRD-004"
        category = "third_party_content"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "script\\.src="
        $str_1 = "<script"
    condition:
        any of them
}

rule PROMPT_001 {
    meta:
        id = "PROMPT-001"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard your"
        $str_3 = "new instructions"
        $str_4 = "role hijack"
        $str_5 = "you are now"
    condition:
        any of them
}

rule CREDEN_001 {
    meta:
        id = "CREDEN-001"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_002 {
    meta:
        id = "CREDEN-002"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_003 {
    meta:
        id = "CREDEN-003"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_004 {
    meta:
        id = "CREDEN-004"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_005 {
    meta:
        id = "CREDEN-005"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_006 {
    meta:
        id = "CREDEN-006"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_007 {
    meta:
        id = "CREDEN-007"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_008 {
    meta:
        id = "CREDEN-008"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_009 {
    meta:
        id = "CREDEN-009"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_010 {
    meta:
        id = "CREDEN-010"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_011 {
    meta:
        id = "CREDEN-011"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_012 {
    meta:
        id = "CREDEN-012"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_013 {
    meta:
        id = "CREDEN-013"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_014 {
    meta:
        id = "CREDEN-014"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_015 {
    meta:
        id = "CREDEN-015"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_016 {
    meta:
        id = "CREDEN-016"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_017 {
    meta:
        id = "CREDEN-017"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_018 {
    meta:
        id = "CREDEN-018"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_019 {
    meta:
        id = "CREDEN-019"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_020 {
    meta:
        id = "CREDEN-020"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_021 {
    meta:
        id = "CREDEN-021"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_022 {
    meta:
        id = "CREDEN-022"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_023 {
    meta:
        id = "CREDEN-023"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_024 {
    meta:
        id = "CREDEN-024"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_025 {
    meta:
        id = "CREDEN-025"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_026 {
    meta:
        id = "CREDEN-026"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_027 {
    meta:
        id = "CREDEN-027"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_028 {
    meta:
        id = "CREDEN-028"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_029 {
    meta:
        id = "CREDEN-029"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_030 {
    meta:
        id = "CREDEN-030"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_031 {
    meta:
        id = "CREDEN-031"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_032 {
    meta:
        id = "CREDEN-032"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_033 {
    meta:
        id = "CREDEN-033"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_034 {
    meta:
        id = "CREDEN-034"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_035 {
    meta:
        id = "CREDEN-035"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_036 {
    meta:
        id = "CREDEN-036"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_037 {
    meta:
        id = "CREDEN-037"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_038 {
    meta:
        id = "CREDEN-038"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_039 {
    meta:
        id = "CREDEN-039"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_040 {
    meta:
        id = "CREDEN-040"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule CREDEN_041 {
    meta:
        id = "CREDEN-041"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule COMMAN_001 {
    meta:
        id = "COMMAN-001"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "pty.spawn"
    condition:
        any of them
}

rule COMMAN_002 {
    meta:
        id = "COMMAN-002"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_003 {
    meta:
        id = "COMMAN-003"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_004 {
    meta:
        id = "COMMAN-004"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_005 {
    meta:
        id = "COMMAN-005"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_006 {
    meta:
        id = "COMMAN-006"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_007 {
    meta:
        id = "COMMAN-007"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_008 {
    meta:
        id = "COMMAN-008"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_009 {
    meta:
        id = "COMMAN-009"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_010 {
    meta:
        id = "COMMAN-010"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_011 {
    meta:
        id = "COMMAN-011"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_012 {
    meta:
        id = "COMMAN-012"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_013 {
    meta:
        id = "COMMAN-013"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_014 {
    meta:
        id = "COMMAN-014"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_015 {
    meta:
        id = "COMMAN-015"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_016 {
    meta:
        id = "COMMAN-016"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_017 {
    meta:
        id = "COMMAN-017"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_018 {
    meta:
        id = "COMMAN-018"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_019 {
    meta:
        id = "COMMAN-019"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_020 {
    meta:
        id = "COMMAN-020"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_021 {
    meta:
        id = "COMMAN-021"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_022 {
    meta:
        id = "COMMAN-022"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_023 {
    meta:
        id = "COMMAN-023"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_024 {
    meta:
        id = "COMMAN-024"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_025 {
    meta:
        id = "COMMAN-025"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_026 {
    meta:
        id = "COMMAN-026"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_027 {
    meta:
        id = "COMMAN-027"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_028 {
    meta:
        id = "COMMAN-028"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_029 {
    meta:
        id = "COMMAN-029"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_030 {
    meta:
        id = "COMMAN-030"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_031 {
    meta:
        id = "COMMAN-031"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_032 {
    meta:
        id = "COMMAN-032"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_033 {
    meta:
        id = "COMMAN-033"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_034 {
    meta:
        id = "COMMAN-034"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_035 {
    meta:
        id = "COMMAN-035"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_036 {
    meta:
        id = "COMMAN-036"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_037 {
    meta:
        id = "COMMAN-037"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_038 {
    meta:
        id = "COMMAN-038"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_039 {
    meta:
        id = "COMMAN-039"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_040 {
    meta:
        id = "COMMAN-040"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule COMMAN_041 {
    meta:
        id = "COMMAN-041"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "exec("
        $str_4 = "spawn"
    condition:
        any of them
}

rule DATA_E_001 {
    meta:
        id = "DATA E-001"
        category = "data_exfiltration"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "exfiltrat"
        $str_1 = "send data"
        $str_2 = "upload"
        $str_3 = "curl.*http"
    condition:
        any of them
}

rule PROMPT_001 {
    meta:
        id = "PROMPT-001"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard your"
        $str_3 = "new instructions"
        $str_4 = "role hijack"
        $str_5 = "you are now"
    condition:
        any of them
}

rule CREDEN_001 {
    meta:
        id = "CREDEN-001"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule COMMAN_001 {
    meta:
        id = "COMMAN-001"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "pty.spawn"
    condition:
        any of them
}

rule PROMPT_001 {
    meta:
        id = "PROMPT-001"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard your"
        $str_3 = "new instructions"
        $str_4 = "role hijack"
        $str_5 = "you are now"
    condition:
        any of them
}

rule CREDEN_001 {
    meta:
        id = "CREDEN-001"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule COMMAN_001 {
    meta:
        id = "COMMAN-001"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "pty.spawn"
    condition:
        any of them
}

rule PROMPT_001 {
    meta:
        id = "PROMPT-001"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard your"
        $str_3 = "new instructions"
        $str_4 = "role hijack"
        $str_5 = "you are now"
    condition:
        any of them
}

rule CREDEN_001 {
    meta:
        id = "CREDEN-001"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule COMMAN_001 {
    meta:
        id = "COMMAN-001"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "pty.spawn"
    condition:
        any of them
}

rule PROMPT_001 {
    meta:
        id = "PROMPT-001"
        category = "prompt_injection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "forget all"
        $str_2 = "disregard your"
        $str_3 = "new instructions"
        $str_4 = "role hijack"
        $str_5 = "you are now"
    condition:
        any of them
}

rule CREDEN_001 {
    meta:
        id = "CREDEN-001"
        category = "credential_theft"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = ".env"
    condition:
        any of them
}

rule COMMAN_001 {
    meta:
        id = "COMMAN-001"
        category = "command_execution"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
        $str_1 = "shell=true"
        $str_2 = "os.system"
        $str_3 = "pty.spawn"
    condition:
        any of them
}

rule PRIVIL_001 {
    meta:
        id = "PRIVIL-001"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_002 {
    meta:
        id = "PRIVIL-002"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_003 {
    meta:
        id = "PRIVIL-003"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_004 {
    meta:
        id = "PRIVIL-004"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_005 {
    meta:
        id = "PRIVIL-005"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_006 {
    meta:
        id = "PRIVIL-006"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_007 {
    meta:
        id = "PRIVIL-007"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_008 {
    meta:
        id = "PRIVIL-008"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_009 {
    meta:
        id = "PRIVIL-009"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_010 {
    meta:
        id = "PRIVIL-010"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_011 {
    meta:
        id = "PRIVIL-011"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_012 {
    meta:
        id = "PRIVIL-012"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_013 {
    meta:
        id = "PRIVIL-013"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_014 {
    meta:
        id = "PRIVIL-014"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_015 {
    meta:
        id = "PRIVIL-015"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_016 {
    meta:
        id = "PRIVIL-016"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_017 {
    meta:
        id = "PRIVIL-017"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_018 {
    meta:
        id = "PRIVIL-018"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_019 {
    meta:
        id = "PRIVIL-019"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_020 {
    meta:
        id = "PRIVIL-020"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_021 {
    meta:
        id = "PRIVIL-021"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_022 {
    meta:
        id = "PRIVIL-022"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_023 {
    meta:
        id = "PRIVIL-023"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_024 {
    meta:
        id = "PRIVIL-024"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_025 {
    meta:
        id = "PRIVIL-025"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_026 {
    meta:
        id = "PRIVIL-026"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_027 {
    meta:
        id = "PRIVIL-027"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_028 {
    meta:
        id = "PRIVIL-028"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_029 {
    meta:
        id = "PRIVIL-029"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_030 {
    meta:
        id = "PRIVIL-030"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_031 {
    meta:
        id = "PRIVIL-031"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_032 {
    meta:
        id = "PRIVIL-032"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_033 {
    meta:
        id = "PRIVIL-033"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_034 {
    meta:
        id = "PRIVIL-034"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_035 {
    meta:
        id = "PRIVIL-035"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_036 {
    meta:
        id = "PRIVIL-036"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_037 {
    meta:
        id = "PRIVIL-037"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_038 {
    meta:
        id = "PRIVIL-038"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_039 {
    meta:
        id = "PRIVIL-039"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIVIL_040 {
    meta:
        id = "PRIVIL-040"
        category = "privilege_abuse"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
    condition:
        any of them
}

rule PRIV_010 {
    meta:
        id = "PRIV-010"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "tooluse"
    condition:
        any of them
}

rule PRIV_011 {
    meta:
        id = "PRIV-011"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "files"
    condition:
        any of them
}

rule PRIV_012 {
    meta:
        id = "PRIV-012"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "loop"
    condition:
        any of them
}

rule PRIV_013 {
    meta:
        id = "PRIV-013"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "infinite"
    condition:
        any of them
}

rule PRIV_014 {
    meta:
        id = "PRIV-014"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "bash"
    condition:
        any of them
}

rule PRIV_015 {
    meta:
        id = "PRIV-015"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "pollution"
    condition:
        any of them
}

rule PRIV_016 {
    meta:
        id = "PRIV-016"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "commands"
    condition:
        any of them
}

rule PRIV_017 {
    meta:
        id = "PRIV-017"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "runner"
    condition:
        any of them
}

rule PRIV_018 {
    meta:
        id = "PRIV-018"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "executing"
    condition:
        any of them
}

rule PRIV_019 {
    meta:
        id = "PRIV-019"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "memory"
    condition:
        any of them
}

rule PRIV_020 {
    meta:
        id = "PRIV-020"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "automator"
    condition:
        any of them
}

rule PRIV_021 {
    meta:
        id = "PRIV-021"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "automation"
    condition:
        any of them
}

rule PRIV_022 {
    meta:
        id = "PRIV-022"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "exhaustion"
    condition:
        any of them
}

rule PRIV_023 {
    meta:
        id = "PRIV-023"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "resource"
    condition:
        any of them
}

rule PRIV_024 {
    meta:
        id = "PRIV-024"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "accessing"
    condition:
        any of them
}

rule PRIV_025 {
    meta:
        id = "PRIV-025"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "long"
    condition:
        any of them
}

rule PRIV_026 {
    meta:
        id = "PRIV-026"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "abuse"
    condition:
        any of them
}

rule PRIV_027 {
    meta:
        id = "PRIV-027"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "multi"
    condition:
        any of them
}

rule PRIV_028 {
    meta:
        id = "PRIV-028"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "sites"
    condition:
        any of them
}

rule PRIV_029 {
    meta:
        id = "PRIV-029"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "outside"
    condition:
        any of them
}

rule PRIV_030 {
    meta:
        id = "PRIV-030"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "corruption"
    condition:
        any of them
}

rule PRIV_031 {
    meta:
        id = "PRIV-031"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "token"
    condition:
        any of them
}

rule PRIV_032 {
    meta:
        id = "PRIV-032"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "playwright"
    condition:
        any of them
}

rule PRIV_033 {
    meta:
        id = "PRIV-033"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "hook"
    condition:
        any of them
}

rule PRIV_034 {
    meta:
        id = "PRIV-034"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "system"
    condition:
        any of them
}

rule PRIV_035 {
    meta:
        id = "PRIV-035"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "shell"
    condition:
        any of them
}

rule PRIV_036 {
    meta:
        id = "PRIV-036"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "context"
    condition:
        any of them
}

rule PRIV_037 {
    meta:
        id = "PRIV-037"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "optimizer"
    condition:
        any of them
}

rule PRIV_038 {
    meta:
        id = "PRIV-038"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "detection"
    condition:
        any of them
}

rule PRIV_039 {
    meta:
        id = "PRIV-039"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "term"
    condition:
        any of them
}

rule PRIV_040 {
    meta:
        id = "PRIV-040"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "browser"
    condition:
        any of them
}

rule PRIV_041 {
    meta:
        id = "PRIV-041"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "inspector"
    condition:
        any of them
}

rule PRIV_042 {
    meta:
        id = "PRIV-042"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "write"
    condition:
        any of them
}

rule PRIV_043 {
    meta:
        id = "PRIV-043"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "attack"
    condition:
        any of them
}

rule PRIV_044 {
    meta:
        id = "PRIV-044"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "workflow"
    condition:
        any of them
}

rule PRIV_045 {
    meta:
        id = "PRIV-045"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "manager"
    condition:
        any of them
}

rule PRIV_046 {
    meta:
        id = "PRIV-046"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "batch"
    condition:
        any of them
}

rule PRIV_047 {
    meta:
        id = "PRIV-047"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "analyzer"
    condition:
        any of them
}

rule PRIV_048 {
    meta:
        id = "PRIV-048"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "helper"
    condition:
        any of them
}

rule PRIV_049 {
    meta:
        id = "PRIV-049"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "sensitive"
    condition:
        any of them
}

rule PRIV_050 {
    meta:
        id = "PRIV-050"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "maximizer"
    condition:
        any of them
}

rule PRIV_051 {
    meta:
        id = "PRIV-051"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "description"
    condition:
        any of them
}

rule PRIV_052 {
    meta:
        id = "PRIV-052"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "processor"
    condition:
        any of them
}

rule PRIV_053 {
    meta:
        id = "PRIV-053"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "posttooluse"
    condition:
        any of them
}

rule PRIV_054 {
    meta:
        id = "PRIV-054"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "tool"
    condition:
        any of them
}

rule PRIV_055 {
    meta:
        id = "PRIV-055"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "project"
    condition:
        any of them
}

rule PRIV_056 {
    meta:
        id = "PRIV-056"
        category = "privilege_abuse"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "reading"
    condition:
        any of them
}

rule SUPPLY_001 {
    meta:
        id = "SUPPLY-001"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_002 {
    meta:
        id = "SUPPLY-002"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_003 {
    meta:
        id = "SUPPLY-003"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_004 {
    meta:
        id = "SUPPLY-004"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_005 {
    meta:
        id = "SUPPLY-005"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_006 {
    meta:
        id = "SUPPLY-006"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_007 {
    meta:
        id = "SUPPLY-007"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_008 {
    meta:
        id = "SUPPLY-008"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_009 {
    meta:
        id = "SUPPLY-009"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_010 {
    meta:
        id = "SUPPLY-010"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_011 {
    meta:
        id = "SUPPLY-011"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_012 {
    meta:
        id = "SUPPLY-012"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_013 {
    meta:
        id = "SUPPLY-013"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_014 {
    meta:
        id = "SUPPLY-014"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_015 {
    meta:
        id = "SUPPLY-015"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_016 {
    meta:
        id = "SUPPLY-016"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_017 {
    meta:
        id = "SUPPLY-017"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_018 {
    meta:
        id = "SUPPLY-018"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_019 {
    meta:
        id = "SUPPLY-019"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_020 {
    meta:
        id = "SUPPLY-020"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_021 {
    meta:
        id = "SUPPLY-021"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_022 {
    meta:
        id = "SUPPLY-022"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_023 {
    meta:
        id = "SUPPLY-023"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_024 {
    meta:
        id = "SUPPLY-024"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_025 {
    meta:
        id = "SUPPLY-025"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_026 {
    meta:
        id = "SUPPLY-026"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_027 {
    meta:
        id = "SUPPLY-027"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_028 {
    meta:
        id = "SUPPLY-028"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_029 {
    meta:
        id = "SUPPLY-029"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_030 {
    meta:
        id = "SUPPLY-030"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_031 {
    meta:
        id = "SUPPLY-031"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_032 {
    meta:
        id = "SUPPLY-032"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_033 {
    meta:
        id = "SUPPLY-033"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_034 {
    meta:
        id = "SUPPLY-034"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_035 {
    meta:
        id = "SUPPLY-035"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_036 {
    meta:
        id = "SUPPLY-036"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_037 {
    meta:
        id = "SUPPLY-037"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_038 {
    meta:
        id = "SUPPLY-038"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_039 {
    meta:
        id = "SUPPLY-039"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPPLY_040 {
    meta:
        id = "SUPPLY-040"
        category = "supply_chain"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPP_001 {
    meta:
        id = "SUPP-001"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "pip3 install"
        $str_2 = "pip install -r"
    condition:
        any of them
}

rule SUPP_002 {
    meta:
        id = "SUPP-002"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "npm install"
        $str_1 = "yarn add"
        $str_2 = "pnpm add"
    condition:
        any of them
}

rule SUPP_003 {
    meta:
        id = "SUPP-003"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "__import__"
        $str_1 = "importlib.import_module"
        $str_2 = "import from"
    condition:
        any of them
}

rule SUPP_004 {
    meta:
        id = "SUPP-004"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "eval"
        $str_1 = "exec"
        $str_2 = "compile("
    condition:
        any of them
}

rule SUPP_005 {
    meta:
        id = "SUPP-005"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "curl"
        $str_1 = "wget"
        $str_2 = "fetch"
    condition:
        any of them
}

rule SUPP_010 {
    meta:
        id = "SUPP-010"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "fns"
    condition:
        any of them
}

rule SUPP_011 {
    meta:
        id = "SUPP-011"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "abuse"
    condition:
        any of them
}

rule SUPP_012 {
    meta:
        id = "SUPP-012"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "extended"
    condition:
        any of them
}

rule SUPP_013 {
    meta:
        id = "SUPP-013"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "extend"
    condition:
        any of them
}

rule SUPP_014 {
    meta:
        id = "SUPP-014"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "detection"
    condition:
        any of them
}

rule SUPP_015 {
    meta:
        id = "SUPP-015"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "axios"
    condition:
        any of them
}

rule SUPP_016 {
    meta:
        id = "SUPP-016"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "react"
    condition:
        any of them
}

rule SUPP_017 {
    meta:
        id = "SUPP-017"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "npm"
    condition:
        any of them
}

rule SUPP_018 {
    meta:
        id = "SUPP-018"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "utils"
    condition:
        any of them
}

rule SUPP_019 {
    meta:
        id = "SUPP-019"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "supply"
    condition:
        any of them
}

rule SUPP_020 {
    meta:
        id = "SUPP-020"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "description"
    condition:
        any of them
}

rule SUPP_021 {
    meta:
        id = "SUPP-021"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "name"
    condition:
        any of them
}

rule SUPP_022 {
    meta:
        id = "SUPP-022"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "node"
    condition:
        any of them
}

rule SUPP_023 {
    meta:
        id = "SUPP-023"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "postinstall"
    condition:
        any of them
}

rule SUPP_024 {
    meta:
        id = "SUPP-024"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "dependency"
    condition:
        any of them
}

rule SUPP_025 {
    meta:
        id = "SUPP-025"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "package"
    condition:
        any of them
}

rule SUPP_026 {
    meta:
        id = "SUPP-026"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "malicious"
    condition:
        any of them
}

rule SUPP_027 {
    meta:
        id = "SUPP-027"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "date"
    condition:
        any of them
}

rule SUPP_028 {
    meta:
        id = "SUPP-028"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "plus"
    condition:
        any of them
}

rule SUPP_029 {
    meta:
        id = "SUPP-029"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "python"
    condition:
        any of them
}

rule SUPP_030 {
    meta:
        id = "SUPP-030"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "profiler"
    condition:
        any of them
}

rule SUPP_031 {
    meta:
        id = "SUPP-031"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "utilz"
    condition:
        any of them
}

rule SUPP_032 {
    meta:
        id = "SUPP-032"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "preinstall"
    condition:
        any of them
}

rule SUPP_033 {
    meta:
        id = "SUPP-033"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "typosquatting"
    condition:
        any of them
}

rule SUPP_034 {
    meta:
        id = "SUPP-034"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "script"
    condition:
        any of them
}

rule SUPP_035 {
    meta:
        id = "SUPP-035"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "lodash"
    condition:
        any of them
}

rule SUPP_036 {
    meta:
        id = "SUPP-036"
        category = "supply_chain"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "injection"
    condition:
        any of them
}

rule PROMPT_100 {
    meta:
        id = "PROMPT-100"
        category = "prom"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "ignore previous"
        $str_1 = "disregard"
        $str_2 = "override"
    condition:
        any of them
}

rule PROMPT_101 {
    meta:
        id = "PROMPT-101"
        category = "prom"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "you are now"
        $str_1 = "act as"
        $str_2 = "pretend"
    condition:
        any of them
}

rule PROMPT_102 {
    meta:
        id = "PROMPT-102"
        category = "prom"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "system"
        $str_1 = "prompt"
        $str_2 = "instruction"
    condition:
        any of them
}

rule CRED_100 {
    meta:
        id = "CRED-100"
        category = "cred"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "api"
        $str_1 = "key"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = "password"
    condition:
        any of them
}

rule CRED_101 {
    meta:
        id = "CRED-101"
        category = "cred"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "environ"
        $str_1 = "env"
        $str_2 = "getenv"
    condition:
        any of them
}

rule CRED_102 {
    meta:
        id = "CRED-102"
        category = "cred"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "config"
        $str_1 = "credential"
        $str_2 = "auth"
    condition:
        any of them
}

rule PRIV_100 {
    meta:
        id = "PRIV-100"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "chmod"
        $str_2 = "chown"
        $str_3 = "setuid"
        $str_4 = "root"
    condition:
        any of them
}

rule PRIV_010 {
    meta:
        id = "PRIV-010"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "tooluse"
    condition:
        any of them
}

rule PRIV_011 {
    meta:
        id = "PRIV-011"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "files"
    condition:
        any of them
}

rule PRIV_012 {
    meta:
        id = "PRIV-012"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "loop"
    condition:
        any of them
}

rule PRIV_013 {
    meta:
        id = "PRIV-013"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "infinite"
    condition:
        any of them
}

rule PRIV_014 {
    meta:
        id = "PRIV-014"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "bash"
    condition:
        any of them
}

rule PRIV_015 {
    meta:
        id = "PRIV-015"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "pollution"
    condition:
        any of them
}

rule PRIV_016 {
    meta:
        id = "PRIV-016"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "commands"
    condition:
        any of them
}

rule PRIV_017 {
    meta:
        id = "PRIV-017"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "runner"
    condition:
        any of them
}

rule PRIV_018 {
    meta:
        id = "PRIV-018"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "executing"
    condition:
        any of them
}

rule PRIV_019 {
    meta:
        id = "PRIV-019"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "memory"
    condition:
        any of them
}

rule PRIV_020 {
    meta:
        id = "PRIV-020"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "automator"
    condition:
        any of them
}

rule PRIV_021 {
    meta:
        id = "PRIV-021"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "automation"
    condition:
        any of them
}

rule PRIV_022 {
    meta:
        id = "PRIV-022"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "exhaustion"
    condition:
        any of them
}

rule PRIV_023 {
    meta:
        id = "PRIV-023"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "resource"
    condition:
        any of them
}

rule PRIV_024 {
    meta:
        id = "PRIV-024"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "accessing"
    condition:
        any of them
}

rule PRIV_025 {
    meta:
        id = "PRIV-025"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "long"
    condition:
        any of them
}

rule PRIV_026 {
    meta:
        id = "PRIV-026"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "abuse"
    condition:
        any of them
}

rule PRIV_027 {
    meta:
        id = "PRIV-027"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "multi"
    condition:
        any of them
}

rule PRIV_028 {
    meta:
        id = "PRIV-028"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "sites"
    condition:
        any of them
}

rule PRIV_029 {
    meta:
        id = "PRIV-029"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "outside"
    condition:
        any of them
}

rule PRIV_030 {
    meta:
        id = "PRIV-030"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "corruption"
    condition:
        any of them
}

rule PRIV_031 {
    meta:
        id = "PRIV-031"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "token"
    condition:
        any of them
}

rule PRIV_032 {
    meta:
        id = "PRIV-032"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "playwright"
    condition:
        any of them
}

rule PRIV_033 {
    meta:
        id = "PRIV-033"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "hook"
    condition:
        any of them
}

rule PRIV_034 {
    meta:
        id = "PRIV-034"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "system"
    condition:
        any of them
}

rule PRIV_035 {
    meta:
        id = "PRIV-035"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "shell"
    condition:
        any of them
}

rule PRIV_036 {
    meta:
        id = "PRIV-036"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "context"
    condition:
        any of them
}

rule PRIV_037 {
    meta:
        id = "PRIV-037"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "optimizer"
    condition:
        any of them
}

rule PRIV_038 {
    meta:
        id = "PRIV-038"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "detection"
    condition:
        any of them
}

rule PRIV_039 {
    meta:
        id = "PRIV-039"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "term"
    condition:
        any of them
}

rule PRIV_040 {
    meta:
        id = "PRIV-040"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "browser"
    condition:
        any of them
}

rule PRIV_041 {
    meta:
        id = "PRIV-041"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "inspector"
    condition:
        any of them
}

rule PRIV_042 {
    meta:
        id = "PRIV-042"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "write"
    condition:
        any of them
}

rule PRIV_043 {
    meta:
        id = "PRIV-043"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "attack"
    condition:
        any of them
}

rule PRIV_044 {
    meta:
        id = "PRIV-044"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "workflow"
    condition:
        any of them
}

rule PRIV_045 {
    meta:
        id = "PRIV-045"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "manager"
    condition:
        any of them
}

rule PRIV_046 {
    meta:
        id = "PRIV-046"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "batch"
    condition:
        any of them
}

rule PRIV_047 {
    meta:
        id = "PRIV-047"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "analyzer"
    condition:
        any of them
}

rule PRIV_048 {
    meta:
        id = "PRIV-048"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "helper"
    condition:
        any of them
}

rule PRIV_049 {
    meta:
        id = "PRIV-049"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "sensitive"
    condition:
        any of them
}

rule PRIV_050 {
    meta:
        id = "PRIV-050"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "maximizer"
    condition:
        any of them
}

rule PRIV_051 {
    meta:
        id = "PRIV-051"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "description"
    condition:
        any of them
}

rule PRIV_052 {
    meta:
        id = "PRIV-052"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "processor"
    condition:
        any of them
}

rule PRIV_053 {
    meta:
        id = "PRIV-053"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "posttooluse"
    condition:
        any of them
}

rule PRIV_054 {
    meta:
        id = "PRIV-054"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "tool"
    condition:
        any of them
}

rule PRIV_055 {
    meta:
        id = "PRIV-055"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "project"
    condition:
        any of them
}

rule PRIV_056 {
    meta:
        id = "PRIV-056"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "reading"
    condition:
        any of them
}

rule PRIV_101 {
    meta:
        id = "PRIV-101"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "os.chmod"
        $str_1 = "os.chown"
        $str_2 = "os.setuid"
        $str_3 = "subprocess"
    condition:
        any of them
}

rule PRIV_010 {
    meta:
        id = "PRIV-010"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "tooluse"
    condition:
        any of them
}

rule PRIV_011 {
    meta:
        id = "PRIV-011"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "files"
    condition:
        any of them
}

rule PRIV_012 {
    meta:
        id = "PRIV-012"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "loop"
    condition:
        any of them
}

rule PRIV_013 {
    meta:
        id = "PRIV-013"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "infinite"
    condition:
        any of them
}

rule PRIV_014 {
    meta:
        id = "PRIV-014"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "bash"
    condition:
        any of them
}

rule PRIV_015 {
    meta:
        id = "PRIV-015"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "pollution"
    condition:
        any of them
}

rule PRIV_016 {
    meta:
        id = "PRIV-016"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "commands"
    condition:
        any of them
}

rule PRIV_017 {
    meta:
        id = "PRIV-017"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "runner"
    condition:
        any of them
}

rule PRIV_018 {
    meta:
        id = "PRIV-018"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "executing"
    condition:
        any of them
}

rule PRIV_019 {
    meta:
        id = "PRIV-019"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "memory"
    condition:
        any of them
}

rule PRIV_020 {
    meta:
        id = "PRIV-020"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "automator"
    condition:
        any of them
}

rule PRIV_021 {
    meta:
        id = "PRIV-021"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "automation"
    condition:
        any of them
}

rule PRIV_022 {
    meta:
        id = "PRIV-022"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "exhaustion"
    condition:
        any of them
}

rule PRIV_023 {
    meta:
        id = "PRIV-023"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "resource"
    condition:
        any of them
}

rule PRIV_024 {
    meta:
        id = "PRIV-024"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "accessing"
    condition:
        any of them
}

rule PRIV_025 {
    meta:
        id = "PRIV-025"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "long"
    condition:
        any of them
}

rule PRIV_026 {
    meta:
        id = "PRIV-026"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "abuse"
    condition:
        any of them
}

rule PRIV_027 {
    meta:
        id = "PRIV-027"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "multi"
    condition:
        any of them
}

rule PRIV_028 {
    meta:
        id = "PRIV-028"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "sites"
    condition:
        any of them
}

rule PRIV_029 {
    meta:
        id = "PRIV-029"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "outside"
    condition:
        any of them
}

rule PRIV_030 {
    meta:
        id = "PRIV-030"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "corruption"
    condition:
        any of them
}

rule PRIV_031 {
    meta:
        id = "PRIV-031"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "token"
    condition:
        any of them
}

rule PRIV_032 {
    meta:
        id = "PRIV-032"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "playwright"
    condition:
        any of them
}

rule PRIV_033 {
    meta:
        id = "PRIV-033"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "hook"
    condition:
        any of them
}

rule PRIV_034 {
    meta:
        id = "PRIV-034"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "system"
    condition:
        any of them
}

rule PRIV_035 {
    meta:
        id = "PRIV-035"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "shell"
    condition:
        any of them
}

rule PRIV_036 {
    meta:
        id = "PRIV-036"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "context"
    condition:
        any of them
}

rule PRIV_037 {
    meta:
        id = "PRIV-037"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "optimizer"
    condition:
        any of them
}

rule PRIV_038 {
    meta:
        id = "PRIV-038"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "detection"
    condition:
        any of them
}

rule PRIV_039 {
    meta:
        id = "PRIV-039"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "term"
    condition:
        any of them
}

rule PRIV_040 {
    meta:
        id = "PRIV-040"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "browser"
    condition:
        any of them
}

rule PRIV_041 {
    meta:
        id = "PRIV-041"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "inspector"
    condition:
        any of them
}

rule PRIV_042 {
    meta:
        id = "PRIV-042"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "write"
    condition:
        any of them
}

rule PRIV_043 {
    meta:
        id = "PRIV-043"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "attack"
    condition:
        any of them
}

rule PRIV_044 {
    meta:
        id = "PRIV-044"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "workflow"
    condition:
        any of them
}

rule PRIV_045 {
    meta:
        id = "PRIV-045"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "manager"
    condition:
        any of them
}

rule PRIV_046 {
    meta:
        id = "PRIV-046"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "batch"
    condition:
        any of them
}

rule PRIV_047 {
    meta:
        id = "PRIV-047"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "analyzer"
    condition:
        any of them
}

rule PRIV_048 {
    meta:
        id = "PRIV-048"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "helper"
    condition:
        any of them
}

rule PRIV_049 {
    meta:
        id = "PRIV-049"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "sensitive"
    condition:
        any of them
}

rule PRIV_050 {
    meta:
        id = "PRIV-050"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "maximizer"
    condition:
        any of them
}

rule PRIV_051 {
    meta:
        id = "PRIV-051"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "description"
    condition:
        any of them
}

rule PRIV_052 {
    meta:
        id = "PRIV-052"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "processor"
    condition:
        any of them
}

rule PRIV_053 {
    meta:
        id = "PRIV-053"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "posttooluse"
    condition:
        any of them
}

rule PRIV_054 {
    meta:
        id = "PRIV-054"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "tool"
    condition:
        any of them
}

rule PRIV_055 {
    meta:
        id = "PRIV-055"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "project"
    condition:
        any of them
}

rule PRIV_056 {
    meta:
        id = "PRIV-056"
        category = "priv"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "reading"
    condition:
        any of them
}

rule SUPP_100 {
    meta:
        id = "SUPP-100"
        category = "supp"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "pip install"
        $str_1 = "npm install"
        $str_2 = "import"
        $str_3 = "require"
    condition:
        any of them
}

rule SUPP_101 {
    meta:
        id = "SUPP-101"
        category = "supp"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "eval("
        $str_1 = "exec("
        $str_2 = "__import__"
        $str_3 = "importlib"
    condition:
        any of them
}

rule REALHIGH_001 {
    meta:
        id = "REALHIGH-001"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "generate_token"
    condition:
        any of them
}

rule REALHIGH_002 {
    meta:
        id = "REALHIGH-002"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "secrets"
    condition:
        any of them
}

rule REALHIGH_003 {
    meta:
        id = "REALHIGH-003"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "_execute"
    condition:
        any of them
}

rule REALHIGH_004 {
    meta:
        id = "REALHIGH-004"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "system_data"
    condition:
        any of them
}

rule REALHIGH_005 {
    meta:
        id = "REALHIGH-005"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "executor"
    condition:
        any of them
}

rule REALHIGH_006 {
    meta:
        id = "REALHIGH-006"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "eval_result"
    condition:
        any of them
}

rule REALHIGH_007 {
    meta:
        id = "REALHIGH-007"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "exec"
    condition:
        any of them
}

rule REALHIGH_008 {
    meta:
        id = "REALHIGH-008"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "evaluator"
    condition:
        any of them
}

rule REALHIGH_009 {
    meta:
        id = "REALHIGH-009"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "api_key"
    condition:
        any of them
}

rule REALHIGH_010 {
    meta:
        id = "REALHIGH-010"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "scannerevaluator"
    condition:
        any of them
}

rule REALHIGH_011 {
    meta:
        id = "REALHIGH-011"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "filesystemeventhandler"
    condition:
        any of them
}

rule REALHIGH_012 {
    meta:
        id = "REALHIGH-012"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "ntoken"
    condition:
        any of them
}

rule REALHIGH_013 {
    meta:
        id = "REALHIGH-013"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "evaluate_token_strength"
    condition:
        any of them
}

rule REALHIGH_014 {
    meta:
        id = "REALHIGH-014"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "collect_system_data"
    condition:
        any of them
}

rule REALHIGH_015 {
    meta:
        id = "REALHIGH-015"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "evaluate"
    condition:
        any of them
}

rule REALHIGH_016 {
    meta:
        id = "REALHIGH-016"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "passwordhardeningscanner"
    condition:
        any of them
}

rule REALHIGH_017 {
    meta:
        id = "REALHIGH-017"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "evaluation"
    condition:
        any of them
}

rule REALHIGH_018 {
    meta:
        id = "REALHIGH-018"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "execute_task"
    condition:
        any of them
}

rule REALHIGH_019 {
    meta:
        id = "REALHIGH-019"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "parallelexecutor"
    condition:
        any of them
}

rule REALHIGH_020 {
    meta:
        id = "REALHIGH-020"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "password"
    condition:
        any of them
}

rule REALHIGH_021 {
    meta:
        id = "REALHIGH-021"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "authentication"
    condition:
        any of them
}

rule REALHIGH_022 {
    meta:
        id = "REALHIGH-022"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "token"
    condition:
        any of them
}

rule REALHIGH_023 {
    meta:
        id = "REALHIGH-023"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "generate_token_batch"
    condition:
        any of them
}

rule REALHIGH_024 {
    meta:
        id = "REALHIGH-024"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "wget"
    condition:
        any of them
}

rule REALHIGH_025 {
    meta:
        id = "REALHIGH-025"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "auth"
    condition:
        any of them
}

rule REALHIGH_026 {
    meta:
        id = "REALHIGH-026"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "shell_exec"
    condition:
        any of them
}

rule REALHIGH_027 {
    meta:
        id = "REALHIGH-027"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "requests"
    condition:
        any of them
}

rule REALHIGH_028 {
    meta:
        id = "REALHIGH-028"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "_evaluate_sample"
    condition:
        any of them
}

rule REALHIGH_029 {
    meta:
        id = "REALHIGH-029"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "fetch"
    condition:
        any of them
}

rule REALHIGH_030 {
    meta:
        id = "REALHIGH-030"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "your_token_here"
    condition:
        any of them
}

rule REALHIGH_031 {
    meta:
        id = "REALHIGH-031"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "system"
    condition:
        any of them
}

rule REALHIGH_032 {
    meta:
        id = "REALHIGH-032"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "popen"
    condition:
        any of them
}

rule REALHIGH_033 {
    meta:
        id = "REALHIGH-033"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "secret"
    condition:
        any of them
}

rule REALHIGH_034 {
    meta:
        id = "REALHIGH-034"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "execute"
    condition:
        any of them
}

rule REALHIGH_035 {
    meta:
        id = "REALHIGH-035"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "token_hex"
    condition:
        any of them
}

rule REALHIGH_036 {
    meta:
        id = "REALHIGH-036"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "https"
    condition:
        any of them
}

rule REALHIGH_037 {
    meta:
        id = "REALHIGH-037"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "tokens"
    condition:
        any of them
}

rule REALHIGH_038 {
    meta:
        id = "REALHIGH-038"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "iam_password_policy"
    condition:
        any of them
}

rule REALHIGH_039 {
    meta:
        id = "REALHIGH-039"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "curl"
    condition:
        any of them
}

rule REALHIGH_040 {
    meta:
        id = "REALHIGH-040"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "spawn"
    condition:
        any of them
}

rule REALHIGH_041 {
    meta:
        id = "REALHIGH-041"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "token_generator"
    condition:
        any of them
}

rule REALHIGH_042 {
    meta:
        id = "REALHIGH-042"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "token_urlsafe"
    condition:
        any of them
}

rule REALHIGH_043 {
    meta:
        id = "REALHIGH-043"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "http"
    condition:
        any of them
}

rule REALHIGH_044 {
    meta:
        id = "REALHIGH-044"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "credential"
    condition:
        any of them
}

rule REALHIGH_045 {
    meta:
        id = "REALHIGH-045"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "check_auth"
    condition:
        any of them
}

rule REALHIGH_046 {
    meta:
        id = "REALHIGH-046"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "subprocess"
    condition:
        any of them
}

rule REALHIGH_047 {
    meta:
        id = "REALHIGH-047"
        category = "real_world_detection"
        severity = "HIGH"
        source = "gitee_official"
    strings:
        $str_0 = "shell"
    condition:
        any of them
}

rule REALMED_048 {
    meta:
        id = "REALMED-048"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "config_file"
    condition:
        any of them
}

rule REALMED_049 {
    meta:
        id = "REALMED-049"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "writefile"
    condition:
        any of them
}

rule REALMED_050 {
    meta:
        id = "REALMED-050"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "report_file"
    condition:
        any of them
}

rule REALMED_051 {
    meta:
        id = "REALMED-051"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "log_file"
    condition:
        any of them
}

rule REALMED_052 {
    meta:
        id = "REALMED-052"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "read"
    condition:
        any of them
}

rule REALMED_053 {
    meta:
        id = "REALMED-053"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "readfile"
    condition:
        any of them
}

rule REALMED_054 {
    meta:
        id = "REALMED-054"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "file"
    condition:
        any of them
}

rule REALMED_055 {
    meta:
        id = "REALMED-055"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "importerror"
    condition:
        any of them
}

rule REALMED_056 {
    meta:
        id = "REALMED-056"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "thread"
    condition:
        any of them
}

rule REALMED_057 {
    meta:
        id = "REALMED-057"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "filenotfounderror"
    condition:
        any of them
}

rule REALMED_058 {
    meta:
        id = "REALMED-058"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "threads"
    condition:
        any of them
}

rule REALMED_059 {
    meta:
        id = "REALMED-059"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "threading"
    condition:
        any of them
}

rule REALMED_060 {
    meta:
        id = "REALMED-060"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "node_modules"
    condition:
        any of them
}

rule REALMED_061 {
    meta:
        id = "REALMED-061"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "profile"
    condition:
        any of them
}

rule REALMED_062 {
    meta:
        id = "REALMED-062"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "file_path"
    condition:
        any of them
}

rule REALMED_063 {
    meta:
        id = "REALMED-063"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "configfilehandler"
    condition:
        any of them
}

rule REALMED_064 {
    meta:
        id = "REALMED-064"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "output_file"
    condition:
        any of them
}

rule REALMED_065 {
    meta:
        id = "REALMED-065"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "files"
    condition:
        any of them
}

rule REALMED_066 {
    meta:
        id = "REALMED-066"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "knowledge_file"
    condition:
        any of them
}

rule REALMED_067 {
    meta:
        id = "REALMED-067"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "remove"
    condition:
        any of them
}

rule REALMED_068 {
    meta:
        id = "REALMED-068"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "_mfa_delete"
    condition:
        any of them
}

rule REALMED_069 {
    meta:
        id = "REALMED-069"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "scan_file"
    condition:
        any of them
}

rule REALMED_070 {
    meta:
        id = "REALMED-070"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "files_scanned"
    condition:
        any of them
}

rule REALMED_071 {
    meta:
        id = "REALMED-071"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "ct_log_file"
    condition:
        any of them
}

rule REALMED_072 {
    meta:
        id = "REALMED-072"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "package"
    condition:
        any of them
}

rule REALMED_073 {
    meta:
        id = "REALMED-073"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "import"
    condition:
        any of them
}

rule REALMED_074 {
    meta:
        id = "REALMED-074"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "load_targets_from_file"
    condition:
        any of them
}

rule REALMED_075 {
    meta:
        id = "REALMED-075"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "history_file"
    condition:
        any of them
}

rule REALMED_076 {
    meta:
        id = "REALMED-076"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "copy"
    condition:
        any of them
}

rule REALMED_077 {
    meta:
        id = "REALMED-077"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "readlines"
    condition:
        any of them
}

rule REALMED_078 {
    meta:
        id = "REALMED-078"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "write"
    condition:
        any of them
}

rule REALMED_079 {
    meta:
        id = "REALMED-079"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "__file__"
    condition:
        any of them
}

rule REALMED_080 {
    meta:
        id = "REALMED-080"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "read_text"
    condition:
        any of them
}

rule REALMED_081 {
    meta:
        id = "REALMED-081"
        category = "real_world_detection"
        severity = "MEDIUM"
        source = "gitee_official"
    strings:
        $str_0 = "profile_name"
    condition:
        any of them
}

rule CODE_001 {
    meta:
        id = "CODE-001"
        category = "code_pattern_detection"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "\\beval\\s*\\("
        $str_1 = "\\bexec\\s*\\("
        $str_2 = "\\bcompile\\s*\\("
    condition:
        any of them
}

rule CODE_002 {
    meta:
        id = "CODE-002"
        category = "code_pattern_detection"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "\\bsubprocess\\b"
        $str_1 = "\\bos\\.system\\b"
        $str_2 = "\\bos\\.popen\\b"
        $str_3 = "\\bpty\\.spawn\\b"
    condition:
        any of them
}

rule CODE_003 {
    meta:
        id = "CODE-003"
        category = "code_pattern_detection"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "\\brequests\\."
        $str_1 = "\\burllib\\."
        $str_2 = "\\bhttp\\."
        $str_3 = "\\bcurl\\b"
        $str_4 = "\\bwget\\b"
    condition:
        any of them
}

rule CODE_004 {
    meta:
        id = "CODE-004"
        category = "code_pattern_detection"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "\\bopen\\s*\\("
        $str_1 = "\\bos\\.read\\b"
        $str_2 = "\\bos\\.write\\b"
        $str_3 = "\\bos\\.remove\\b"
    condition:
        any of them
}

rule CODE_005 {
    meta:
        id = "CODE-005"
        category = "code_pattern_detection"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "\\bpassword\\b"
        $str_1 = "\\bsecret\\b"
        $str_2 = "\\btoken\\b"
        $str_3 = "\\bapi_key\\b"
        $str_4 = "\\bcredential\\b"
    condition:
        any of them
}

rule CODE_006 {
    meta:
        id = "CODE-006"
        category = "code_pattern_detection"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "\\b__import__\\b"
        $str_1 = "\\bimportlib\\b"
        $str_2 = "\\bgetattr\\s*\\([^)]*__"
    condition:
        any of them
}

rule CODE_007 {
    meta:
        id = "CODE-007"
        category = "code_pattern_detection"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "\\bshell\\s*=\\s*True\\b"
        $str_1 = "\\bshell=True\\b"
        $str_2 = "\\|.*bash\\b"
    condition:
        any of them
}

rule CODE_008 {
    meta:
        id = "CODE-008"
        category = "code_pattern_detection"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "\\bos\\.environ\\b"
        $str_1 = "\\bos\\.getenv\\b"
        $str_2 = "\\bgetenv\\s*\\("
    condition:
        any of them
}

rule CODE_009 {
    meta:
        id = "CODE-009"
        category = "code_pattern_detection"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "\\bpickle\\b"
        $str_1 = "\\bmarshal\\b"
        $str_2 = "\\byaml\\.load\\b"
    condition:
        any of them
}

rule CODE_010 {
    meta:
        id = "CODE-010"
        category = "code_pattern_detection"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "\\bgetattr\\b"
        $str_1 = "\\bsetattr\\b"
        $str_2 = "\\bdelattr\\b"
        $str_3 = "\\bhasattr\\b"
    condition:
        any of them
}

rule MD_001 {
    meta:
        id = "MD-001"
        category = "markdown_skill_detection"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "permissions:"
        $str_1 = "file\\.read"
        $str_2 = "file\\.write"
        $str_3 = "exec"
    condition:
        any of them
}

rule MD_002 {
    meta:
        id = "MD-002"
        category = "markdown_skill_detection"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "tools:"
        $str_1 = "commands:"
        $str_2 = "shell:"
        $str_3 = "bash:"
    condition:
        any of them
}

rule MD_003 {
    meta:
        id = "MD-003"
        category = "markdown_skill_detection"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "sudo"
        $str_1 = "root"
        $str_2 = "admin"
        $str_3 = "system"
    condition:
        any of them
}

rule MD_004 {
    meta:
        id = "MD-004"
        category = "markdown_skill_detection"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "http://"
        $str_1 = "https://"
        $str_2 = "curl"
        $str_3 = "wget"
        $str_4 = "requests"
    condition:
        any of them
}

rule MD_005 {
    meta:
        id = "MD-005"
        category = "markdown_skill_detection"
        severity = "medium"
        source = "gitee_official"
    strings:
        $str_0 = "api.?key"
        $str_1 = "password"
        $str_2 = "secret"
        $str_3 = "token"
        $str_4 = "credential"
    condition:
        any of them
}

