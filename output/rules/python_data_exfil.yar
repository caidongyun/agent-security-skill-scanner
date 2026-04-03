rule Python_Data_Exfiltration {
    meta:
        description = "Detects Python data exfiltration"
        author = "Sample Generator v2.0"
        severity = "high"
    
    strings:
        $ssh = ".ssh"
        $credential = "credential"
        $base64 = "base64"
        $env_var = "environ"
    
    condition:
        2 of them
}