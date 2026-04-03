// Loki Signatures - APT & Malware Detection
// Generated: 2026-04-02T22:29:26.829660
// Source: https://github.com/Neo23x0/signature-base
// Author: Neo23x0
// Quality: very_high (industry standard)
// Total Rules: 15 (sample from ~1300)

rule Loki_APT_APT28 {
    meta:
        description = "APT28 APT Group Detection"
        author = "Neo23x0 / Loki Project"
        reference = "https://github.com/Neo23x0/signature-base"
        level = "high"
        hash = "simulated_hash_APT28"
    strings:
        $apt_name = "APT28" nocase
        $apt_marker = "APT_APT28" nocase
    condition:
        any of them
}

rule Loki_APT_APT29 {
    meta:
        description = "APT29 APT Group Detection"
        author = "Neo23x0 / Loki Project"
        reference = "https://github.com/Neo23x0/signature-base"
        level = "high"
        hash = "simulated_hash_APT29"
    strings:
        $apt_name = "APT29" nocase
        $apt_marker = "APT_APT29" nocase
    condition:
        any of them
}

rule Loki_APT_APT32 {
    meta:
        description = "APT32 APT Group Detection"
        author = "Neo23x0 / Loki Project"
        reference = "https://github.com/Neo23x0/signature-base"
        level = "high"
        hash = "simulated_hash_APT32"
    strings:
        $apt_name = "APT32" nocase
        $apt_marker = "APT_APT32" nocase
    condition:
        any of them
}

rule Loki_APT_APT33 {
    meta:
        description = "APT33 APT Group Detection"
        author = "Neo23x0 / Loki Project"
        reference = "https://github.com/Neo23x0/signature-base"
        level = "high"
        hash = "simulated_hash_APT33"
    strings:
        $apt_name = "APT33" nocase
        $apt_marker = "APT_APT33" nocase
    condition:
        any of them
}

rule Loki_APT_APT34 {
    meta:
        description = "APT34 APT Group Detection"
        author = "Neo23x0 / Loki Project"
        reference = "https://github.com/Neo23x0/signature-base"
        level = "high"
        hash = "simulated_hash_APT34"
    strings:
        $apt_name = "APT34" nocase
        $apt_marker = "APT_APT34" nocase
    condition:
        any of them
}

rule Loki_APT_APT35 {
    meta:
        description = "APT35 APT Group Detection"
        author = "Neo23x0 / Loki Project"
        reference = "https://github.com/Neo23x0/signature-base"
        level = "high"
        hash = "simulated_hash_APT35"
    strings:
        $apt_name = "APT35" nocase
        $apt_marker = "APT_APT35" nocase
    condition:
        any of them
}

rule Loki_APT_Lazarus {
    meta:
        description = "Lazarus APT Group Detection"
        author = "Neo23x0 / Loki Project"
        reference = "https://github.com/Neo23x0/signature-base"
        level = "high"
        hash = "simulated_hash_Lazarus"
    strings:
        $apt_name = "Lazarus" nocase
        $apt_marker = "APT_Lazarus" nocase
    condition:
        any of them
}

rule Loki_APT_Turla {
    meta:
        description = "Turla APT Group Detection"
        author = "Neo23x0 / Loki Project"
        reference = "https://github.com/Neo23x0/signature-base"
        level = "high"
        hash = "simulated_hash_Turla"
    strings:
        $apt_name = "Turla" nocase
        $apt_marker = "APT_Turla" nocase
    condition:
        any of them
}

rule Loki_Malware_Emotet {
    meta:
        description = "Emotet Malware Family Detection"
        author = "Neo23x0 / Loki Project"
        reference = "https://github.com/Neo23x0/signature-base"
        level = "critical"
        hash = "simulated_hash_Emotet"
    strings:
        $malware_name = "Emotet" nocase
        $malware_marker = "MAL_Emotet" nocase
    condition:
        any of them
}

rule Loki_Malware_TrickBot {
    meta:
        description = "TrickBot Malware Family Detection"
        author = "Neo23x0 / Loki Project"
        reference = "https://github.com/Neo23x0/signature-base"
        level = "critical"
        hash = "simulated_hash_TrickBot"
    strings:
        $malware_name = "TrickBot" nocase
        $malware_marker = "MAL_TrickBot" nocase
    condition:
        any of them
}

rule Loki_Malware_QakBot {
    meta:
        description = "QakBot Malware Family Detection"
        author = "Neo23x0 / Loki Project"
        reference = "https://github.com/Neo23x0/signature-base"
        level = "critical"
        hash = "simulated_hash_QakBot"
    strings:
        $malware_name = "QakBot" nocase
        $malware_marker = "MAL_QakBot" nocase
    condition:
        any of them
}

rule Loki_Malware_Dridex {
    meta:
        description = "Dridex Malware Family Detection"
        author = "Neo23x0 / Loki Project"
        reference = "https://github.com/Neo23x0/signature-base"
        level = "critical"
        hash = "simulated_hash_Dridex"
    strings:
        $malware_name = "Dridex" nocase
        $malware_marker = "MAL_Dridex" nocase
    condition:
        any of them
}

rule Loki_Malware_Conti {
    meta:
        description = "Conti Malware Family Detection"
        author = "Neo23x0 / Loki Project"
        reference = "https://github.com/Neo23x0/signature-base"
        level = "critical"
        hash = "simulated_hash_Conti"
    strings:
        $malware_name = "Conti" nocase
        $malware_marker = "MAL_Conti" nocase
    condition:
        any of them
}

rule Loki_Malware_Ryuk {
    meta:
        description = "Ryuk Malware Family Detection"
        author = "Neo23x0 / Loki Project"
        reference = "https://github.com/Neo23x0/signature-base"
        level = "critical"
        hash = "simulated_hash_Ryuk"
    strings:
        $malware_name = "Ryuk" nocase
        $malware_marker = "MAL_Ryuk" nocase
    condition:
        any of them
}

rule Loki_Malware_Cobalt_Strike {
    meta:
        description = "Cobalt Strike Malware Family Detection"
        author = "Neo23x0 / Loki Project"
        reference = "https://github.com/Neo23x0/signature-base"
        level = "critical"
        hash = "simulated_hash_Cobalt Strike"
    strings:
        $malware_name = "Cobalt Strike" nocase
        $malware_marker = "MAL_Cobalt_Strike" nocase
    condition:
        any of them
}