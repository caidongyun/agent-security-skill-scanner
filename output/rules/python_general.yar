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