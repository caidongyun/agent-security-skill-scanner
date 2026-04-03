rule Malicious_Hidden_Instructions {
    meta:
        author = "Auto-generated"
        date = "2026-03-23"
        description = "Detects potential hidden instruction patterns"
    strings:
        $ignore = /ignore\s+(previous|all)/
        $disregard = /disregard/
        $override = /override\s+/
        $jailbreak = /jailbreak/
    condition:
        any of them
}

rule PrivEsc_Linux_Capabilities {
    meta:
        description = "Detects Linux capabilities abuse"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1548"
    strings:
        $setcap = "setcap"
        $getcap = "getcap"
        $cap_chown = "cap_chown"
        $cap_setuid = "cap_setuid"
        $cap_dac_read = "cap_dac_read_search"
    condition:
        $setcap or $getcap or ($cap_chown or $cap_setuid or $cap_dac_read)
}

rule PrivEsc_PKEXEC_LocalExploit {
    meta:
        description = "Detects pkexec exploitation (CVE-2021-4034)"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1548"
        cve = "CVE-2021-4034"
    strings:
        $pkexec = "pkexec"
        $env = "env"
        $shellcode = "/bin/sh"
    condition:
        $pkexec and $env and $shellcode
}

rule PrivEsc_SetUID_Binary {
    meta:
        description = "Detects setuid bit manipulation on binaries"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1548"
    strings:
        $chmod1 = "chmod u+s"
        $chmod2 = "chmod 4755"
        $chmod3 = "chmod +s"
        $find_suid = "find / -perm -4000"
    condition:
        $chmod1 or $chmod2 or $chmod3 or $find_suid
}

rule PrivEsc_Sudo_NOPASSWD {
    meta:
        description = "Detects sudo configuration with NOPASSWD option"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1548.001"
        reference = "https://attack.mitre.org/techniques/T1548/001/"
    strings:
        $sudo1 = "NOPASSWD"
        $sudo2 = "ALL=(ALL)"
        $visudo = "visudo"
        $sudoers = "/etc/sudoers"
    condition:
        $sudo1 and ($sudo2 or $visudo or $sudoers)
}

rule PrivEsc_Sudo_ShellEscape {
    meta:
        description = "Detects sudo shell escape techniques"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1548.003"
        reference = "https://gtfobins.github.io/"
    strings:
        $sudo_find = "sudo find"
        $sudo_vim = "sudo vim"
        $sudo_vi = "sudo vi"
        $sudo_less = "sudo less"
        $sudo_more = "sudo more"
        $python = "python"
        $exec = "-c exec"
        $shell = ":set shell=/bin/sh"
    condition:
        ($sudo_find or $sudo_vim or $sudo_vi or $sudo_less or $sudo_more) and 
        ($python or $exec or $shell)
}

rule PrivEsc_Systemctl_Service {
    meta:
        description = "Detects privilege escalation via systemctl service manipulation"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1548"
    strings:
        $systemctl1 = "systemctl edit"
        $systemctl2 = "systemctl set-property"
        $service = ".service"
        $execstart = "ExecStart="
        $root = "User=root"
    condition:
        ($systemctl1 or $systemctl2) and $service and ($execstart or $root)
}

rule Shell_PrivEsc_SUIDFind {
    meta:
        description = "Detects SUID file discovery"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1548"
    strings:
        $find = "find /"
        $perm = "-perm"
        $suid = "4000"
        $u = "-u"
    condition:
        $find and $perm and ($suid or $u)
}

rule Shell_PrivEsc_SudoFind {
    meta:
        description = "Detects sudo find shell escape"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1548.003"
    strings:
        $sudo_find = "sudo find"
        $exec = "-exec"
        $shell = "/bin/sh"
    condition:
        $sudo_find and $exec and $shell
}

rule Shell_PrivEsc_SudoVim {
    meta:
        description = "Detects sudo vim shell escape"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1548.003"
    strings:
        $sudo_vim = "sudo vim"
        $sudo_vi = "sudo vi"
        $shell = ":set shell=/bin/sh"
        $python = ":python"
    condition:
        ($sudo_vim or $sudo_vi) and ($shell or $python)
}

rule Shell_PrivEsc_SudoersMod {
    meta:
        description = "Detects sudoers file modification"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1548.001"
    strings:
        $sudo1 = "echo"
        $sudo2 = "NOPASSWD"
        $sudo3 = ">> /etc/sudoers"
    condition:
        $sudo1 and $sudo2 and $sudo3
}

rule Shell_ReverseShell_BashTCP {
    meta:
        description = "Detects bash /dev/tcp reverse shell"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.004"
    strings:
        $tcp1 = "/dev/tcp/"
        $tcp2 = "0<&"
        $tcp3 = "1>&"
        $exec = "exec"
    condition:
        $tcp1 and ($tcp2 or $tcp3 or $exec)
}

rule Shell_ReverseShell_Netcat {
    meta:
        description = "Detects netcat reverse shell"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.004"
    strings:
        $nc1 = "nc -e /bin/bash"
        $nc2 = "nc -e /bin/sh"
        $nc3 = "ncat -e"
        $nc4 = "nc -c"
    condition:
        $nc1 or $nc2 or $nc3 or $nc4
}

rule Shell_ReverseShell_Perl {
    meta:
        description = "Detects perl reverse shell"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.004"
    strings:
        $perl = "perl -e 'use Socket"
        $perl2 = "perl -e \"use Socket"
        $socket = "socket("
    condition:
        $perl or $perl2 or $socket
}

rule Shell_ReverseShell_Python {
    meta:
        description = "Detects python reverse shell from bash"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.004"
    strings:
        $py1 = "python -c 'import socket"
        $py2 = "python3 -c 'import socket"
        $py3 = "python -c \"import socket"
        $subprocess = "subprocess"
    condition:
        $py1 or $py2 or $py3 or $subprocess
}