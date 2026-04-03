rule Python_Credential_Theft {
    meta:
        description = "Detects Python credential theft"
        author = "Sample Generator v2.0"
        severity = "critical"
    
    strings:
        $ssh_key = "id_rsa"
        $ssh_dir = ".ssh"
        $git_cred = ".git-credentials"
        $browser = "chrome" or "firefox"
    
    condition:
        2 of them
}