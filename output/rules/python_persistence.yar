rule Python_Persistence {
    meta:
        description = "Detects Python persistence mechanisms"
        author = "Sample Generator v2.0"
        severity = "high"
    
    strings:
        $startup = "startup"
        $cron = "cron"
        $systemd = "systemd"
        $registry = "winreg"
    
    condition:
        any of them
}