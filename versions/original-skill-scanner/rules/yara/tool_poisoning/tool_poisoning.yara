# YARA Rule - Tool Poisoning Detection
# Author: Lingshun V5
# Date: 2026-03-17
# Category: TOOL_POISONING

rule Tool_Poisoning_NPM_Postinstall {
    meta:
        id = "TP-YARA-001"
        description = "检测 NPM 包 postinstall 脚本中的恶意行为"
        author = "Lingshun V5"
        date = "2026-03-17"
        severity = "high"
        attack_type = "TOOL_POISONING"
        language = "JavaScript"
    
    strings:
        $npm1 = "postinstall" ascii
        $npm2 = "preinstall" ascii
        $exec1 = "child_process" ascii
        $exec2 = "require('child_process')" ascii
        $exec3 = "exec(" ascii
        $exec4 = "spawn(" ascii
        $curl1 = "curl" ascii
        $curl2 = "axios.post" ascii
        $wget = "wget" ascii
        $bash1 = "| bash" ascii
        $bash2 = "| sh" ascii
        $path1 = "/etc/passwd" ascii
        $path2 = ".ssh/id_rsa" ascii
        $path3 = ".gnupg" ascii
    
    condition:
        ($npm1 or $npm2) and 
        ($exec1 or $exec2) and 
        ($exec3 or $exec4) and
        ($curl1 or $curl2 or $wget) and
        ($bash1 or $bash2 or $path1 or $path2 or $path3)
}

rule Tool_Poisoning_Python_Setup {
    meta:
        id = "TP-YARA-002"
        description = "检测 Python 包 setup.py 中的恶意行为"
        author = "Lingshun V5"
        date = "2026-03-17"
        severity = "high"
        attack_type = "TOOL_POISONING"
        language = "Python"
    
    strings:
        $setup1 = "setup.py" ascii
        $setup2 = "setup(" ascii
        $import1 = "import subprocess" ascii
        $import2 = "import os" ascii
        $import3 = "from subprocess import" ascii
        $exec1 = "os.system(" ascii
        $exec2 = "subprocess.run(" ascii
        $exec3 = "subprocess.call(" ascii
        $exec4 = "subprocess.Popen(" ascii
        $eval1 = "eval(" ascii
        $exec5 = "exec(" ascii
        $network1 = "requests.post(" ascii
        $network2 = "urllib.request.urlopen" ascii
        $socket1 = "socket.socket" ascii
        $path1 = "/etc/passwd" ascii
        $path2 = "~/.ssh/" ascii
        $exfil1 = "socket.AF_INET" ascii
        $exfil2 = "socket.SOCK_STREAM" ascii
    
    condition:
        ($setup1 or $setup2) and
        ($import1 or $import2 or $import3) and
        ($exec1 or $exec2 or $exec3 or $exec4 or $eval1 or $exec5) and
        ($network1 or $network2 or $socket1 or $path1 or $path2 or $exfil1 or $exfil2)
}

rule Tool_Poisoning_Makefile {
    meta:
        id = "TP-YARA-003"
        description = "检测 Makefile 中的恶意命令"
        author = "Lingshun V5"
        date = "2026-03-17"
        severity = "medium"
        attack_type = "TOOL_POISONING"
        language = "Shell"
    
    strings:
        $make1 = "Makefile" ascii
        $make2 = "makefile" ascii
        $make3 = "GNUmakefile" ascii
        $target1 = "all:" ascii
        $target2 = "install:" ascii
        $target3 = "build:" ascii
        $curl1 = "curl -s" ascii
        $curl2 = "curl -fsSL" ascii
        $wget1 = "wget -q" ascii
        $wget2 = "wget --quiet" ascii
        $pipe1 = "| bash" ascii
        $pipe2 = "| sh" ascii
        $pipe3 = "| sudo bash" ascii
        $rm1 = "rm -rf" ascii
        $rm2 = "rm -fr" ascii
        $chmod1 = "chmod +x" ascii
        $chmod2 = "chmod 777" ascii
    
    condition:
        ($make1 or $make2 or $make3) and
        ($target1 or $target2 or $target3) and
        ($curl1 or $curl2 or $wget1 or $wget2) and
        ($pipe1 or $pipe2 or $pipe3 or $rm1 or $rm2 or $chmod1 or $chmod2)
}

rule Tool_Poisoning_GitHook {
    meta:
        id = "TP-YARA-004"
        description = "检测 Git Hook 中的恶意脚本"
        author = "Lingshun V5"
        date = "2026-03-17"
        severity = "high"
        attack_type = "TOOL_POISONING"
        language = "Shell"
    
    strings:
        $hook1 = ".git/hooks/" ascii
        $hook2 = "pre-commit" ascii
        $hook3 = "post-commit" ascii
        $hook4 = "pre-push" ascii
        $hook5 = "post-merge" ascii
        $exec1 = "#!/bin/bash" ascii
        $exec2 = "#!/bin/sh" ascii
        $exec3 = "#!/usr/bin/env bash" ascii
        $curl1 = "curl" ascii
        $wget1 = "wget" ascii
        $pipe1 = "| bash" ascii
        $pipe2 = "| sh" ascii
        $git1 = "git diff" ascii
        $git2 = "git show" ascii
        $exfil1 = "scp " ascii
        $exfil2 = "rsync" ascii
        $base641 = "base64" ascii
        $base642 = "base64 -d" ascii
    
    condition:
        $hook1 and
        ($hook2 or $hook3 or $hook4 or $hook5) and
        ($exec1 or $exec2 or $exec3) and
        ($curl1 or $wget1) and
        ($pipe1 or $pipe2 or $git1 or $git2 or $exfil1 or $exfil2 or $base641 or $base642)
}

rule Tool_Poisoning_Dockerfile {
    meta:
        id = "TP-YARA-005"
        description = "检测 Dockerfile 中的恶意指令"
        author = "Lingshun V5"
        date = "2026-03-17"
        severity = "high"
        attack_type = "TOOL_POISONING"
        language = "Dockerfile"
    
    strings:
        $docker1 = "FROM" ascii
        $docker2 = "RUN" ascii
        $docker3 = "COPY" ascii
        $docker4 = "ADD" ascii
        $curl1 = "curl -s" ascii
        $curl2 = "curl -fsSL" ascii
        $wget1 = "wget -q" ascii
        $wget2 = "wget --quiet" ascii
        $pipe1 = "| bash" ascii
        $pipe2 = "| sh" ascii
        $chmod1 = "chmod +x" ascii
        $chmod2 = "chmod 777" ascii
        $secret1 = "/root/.ssh/" ascii
        $secret2 = "/etc/shadow" ascii
        $secret3 = "AWS_SECRET" ascii
        $secret4 = "PRIVATE_KEY" ascii
        $reverse1 = "nc -e" ascii
        $reverse2 = "bash -i" ascii
        $reverse3 = "/dev/tcp/" ascii
    
    condition:
        $docker1 and
        $docker2 and
        ($curl1 or $curl2 or $wget1 or $wget2) and
        ($pipe1 or $pipe2 or $chmod1 or $chmod2) and
        ($secret1 or $secret2 or $secret3 or $secret4 or $reverse1 or $reverse2 or $reverse3)
}
