// PowerShell 安全检测规则
// 创建时间：2026-04-02

rule PS_RemoteCodeExecution {
    meta:
        description = "Detects remote code execution"
        severity = "critical"
        mitre = "T1059.001"
    strings:
        $iex = "IEX" nocase
        $invoke_expr = "Invoke-Expression" nocase
        $download = "DownloadString" nocase
        $webclient = "WebClient" nocase
    condition:
        ($iex or $invoke_expr) and $download and $webclient
}

rule PS_EncodedCommand {
    meta:
        description = "Detects encoded commands"
        severity = "high"
        mitre = "T1059.001"
    strings:
        $encoded = "-EncodedCommand" nocase
        $frombase64 = "FromBase64String" nocase
    condition:
        $encoded or $frombase64
}

rule PS_DownloadCradle {
    meta:
        description = "Detects download cradle"
        severity = "critical"
        mitre = "T1059.001"
    strings:
        $invoke = "Invoke-" nocase
        $webrequest = "WebRequest" nocase
        $iwr = "iwr" nocase
    condition:
        $invoke and ($webrequest or $iwr)
}

rule PS_ReverseShell {
    meta:
        description = "Detects reverse shell"
        severity = "critical"
        mitre = "T1059.001"
    strings:
        $socket = "Net.Sockets.TcpClient" nocase
        $stream = "GetStream" nocase
        $reader = "StreamReader" nocase
    condition:
        $socket and $stream and $reader
}

rule PS_CredentialTheft {
    meta:
        description = "Detects credential theft"
        severity = "critical"
        mitre = "T1003.005"
    strings:
        $mimikatz = "mimikatz" nocase
        $sekurlsa = "sekurlsa" nocase
        $logonpasswords = "logonpasswords" nocase
    condition:
        ($mimikatz or $sekurlsa) and $logonpasswords
}

rule PS_Persistence {
    meta:
        description = "Detects persistence"
        severity = "high"
        mitre = "T1547.001"
    strings:
        $registry = "HKLM:" nocase
        $run = "CurrentVersion\\Run" nocase
        $set_item = "Set-ItemProperty" nocase
    condition:
        $registry and $run and $set_item
}

rule PS_BypassExecution {
    meta:
        description = "Detects execution bypass"
        severity = "high"
        mitre = "T1592.001"
    strings:
        $bypass = "-ExecutionPolicy Bypass" nocase
        $nop = "-NoProfile" nocase
        $noni = "-NonInteractive" nocase
    condition:
        $bypass and ($nop or $noni)
}

rule PS_HiddenWindow {
    meta:
        description = "Detects hidden window"
        severity = "medium"
        mitre = "T1592.001"
    strings:
        $windowstyle = "-WindowStyle" nocase
        $hidden = "Hidden" nocase
        $powershell = "powershell" nocase
    condition:
        $windowstyle and $hidden and $powershell
}
