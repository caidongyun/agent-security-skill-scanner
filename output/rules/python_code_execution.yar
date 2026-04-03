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