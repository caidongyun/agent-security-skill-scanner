rule Python_Malicious_General {
    meta:
        description = "Detects general Python malicious code"
        author = "Sample Generator v2.0"
        severity = "medium"
    
    strings:
        $import_os = "import os"
        $import_sys = "import sys"
        $import_subprocess = "import subprocess"
        $import_socket = "import socket"
    
    condition:
        2 of them
}

rule Python_Code_Execution {
    meta:
        description = "Detects Python code execution"
        author = "Sample Generator v2.0"
        severity = "high"
    
    strings:
        $subprocess = "subprocess"
        $eval = "eval("
        $exec = "exec("
        $shell = "shell=True"
    
    condition:
        2 of them
}

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