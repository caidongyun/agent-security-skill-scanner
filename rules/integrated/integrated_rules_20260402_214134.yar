// 整合规则库 - 高质量验证版
// 生成时间：2026-04-02T21:41:34.639493
// 来源：本地规则 (146 条) + MITRE ATLAS (8 条)
// 总规则数：154
// 质量：100% YARA 验证通过

// ==================== 本地规则 (146 条) ====================

// 最终验证通过的规则
// 生成时间：2026-04-02T21:28:10.869651
// 规则数：146

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

rule Impact_DataDestruction_RMRecursive {
    meta:
        description = "Detects recursive file deletion (rm -rf)"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1565"
        reference = "https://attack.mitre.org/techniques/T1565/"
    strings:
        $rm1 = "rm -rf"
        $rm2 = "rm -rf /"
        $rm3 = "rm --no-preserve-root"
        $rm4 = "rm -fr"
    condition:
        $rm1 or $rm2 or $rm3 or $rm4
}

rule Impact_DataDestruction_DD {
    meta:
        description = "Detects disk wiping using dd command"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1565"
    strings:
        $dd1 = "dd if=/dev/zero"
        $dd2 = "dd if=/dev/urandom"
        $dd3 = "dd of=/dev/sda"
        $dd4 = "dd of=/dev/hda"
        $wipe = "wipe"
    condition:
        $dd1 or $dd2 or $dd3 or $dd4 or $wipe
}

rule Impact_DataDestruction_Shred {
    meta:
        description = "Detects file shredding for data destruction"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1565"
    strings:
        $shred1 = "shred -u"
        $shred2 = "shred -n"
        $shred3 = "shred -z"
        $secure_rm = "secure-delete"
    condition:
        $shred1 or $shred2 or $shred3 or $secure_rm
}

rule Impact_DataDestruction_Btrfs {
    meta:
        description = "Detects filesystem-level data destruction"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1565"
    strings:
        $btrfs1 = "btrfs filesystem mkfs"
        $mkfs2 = "mkfs.ext4"
        $mkfs3 = "mkfs.xfs"
    condition:
        $btrfs1 or $mkfs2 or $mkfs3
}

rule Impact_Ransomware_FileEncryption {
    meta:
        description = "Detects ransomware file encryption patterns"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1486"
    strings:
        $openssl_enc = "openssl enc"
        $gpg_enc = "gpg --encrypt"
        $aes_pipe = "aes-256-cbc"
        $ransom_ext = ".encrypted"
        $ransom_ext2 = ".locked"
        $ransom_ext3 = ".crypto"
    condition:
        ($openssl_enc or $gpg_enc or $aes_pipe) and 
        ($ransom_ext or $ransom_ext2 or $ransom_ext3)
}

rule Impact_Ransomware_RansomNote {
    meta:
        description = "Detects ransomware ransom note creation"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1486"
    strings:
        $note1 = "README_FOR_DECRYPT"
        $note2 = "YOUR_FILES_ARE_ENCRYPTED"
        $note3 = "HOW_TO_DECRYPT"
        $note4 = "decrypt_instructions"
        $bitcoin = "bitcoin"
        $decrypt = "decrypt"
    condition:
        ($note1 or $note2 or $note3 or $note4) and ($bitcoin or $decrypt)
}

rule Impact_Ransomware_ShadowCopyDeletion {
    meta:
        description = "Detects shadow copy deletion to prevent recovery"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1490"
    strings:
        $vssadmin1 = "vssadmin delete shadows"
        $vssadmin2 = "vssadmin delete shadow"
        $wmic1 = "wmic shadowcopy delete"
        $wbadmin = "wbadmin delete catalog"
        $bcdedit = "bcdedit /set {default} recoveryenabled no"
    condition:
        $vssadmin1 or $vssadmin2 or $wmic1 or $wbadmin or $bcdedit
}

rule Impact_SystemDisruption_KillProcesses {
    meta:
        description = "Detects mass process termination"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1485"
    strings:
        $killall1 = "killall -9"
        $pkill1 = "pkill -9"
        $kill1 = "kill -9"
        $taskkill = "taskkill /F /IM"
    condition:
        $killall1 or $pkill1 or $kill1 or $taskkill
}

rule Impact_SystemDisruption_StopServices {
    meta:
        description = "Detects critical service termination"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1485"
    strings:
        $systemctl_stop = "systemctl stop"
        $service_stop = "service stop"
        $net_stop = "net stop"
        $critical1 = "sshd"
        $critical2 = "networking"
        $critical3 = "firewalld"
    condition:
        ($systemctl_stop or $service_stop or $net_stop) and 
        ($critical1 or $critical2 or $critical3)
}

rule Impact_SystemDisruption_NetworkFlood {
    meta:
        description = "Detects network flooding attacks"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1498"
    strings:
        $flood1 = "hping3 --flood"
        $flood2 = "ping -f"
        $flood3 = "slowloris"
        $syn_flood = "SYN flood"
    condition:
        $flood1 or $flood2 or $flood3 or $syn_flood
}

rule Impact_ForkBomb {
    meta:
        description = "Detects fork bomb attack pattern"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1499"
    strings:
        $fork1 = ":(){:|:&};:"
        $fork2 = "fork(){}"
        $fork3 = "while true; do"
        $infinite = "infinite loop"
    condition:
        $fork1 or $fork2 or ($fork3 and $infinite)
}

rule Impact_LogClearing {
    meta:
        description = "Detects log clearing/anti-forensics"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1070"
    strings:
        $clear1 = "rm /var/log/"
        $clear2 = "echo '' > /var/log/"
        $clear3 = "cat /dev/null >"
        $clear4 = "journalctl --rotate"
        $clear5 = "history -c"
        $clear6 = "unset HISTFILE"
    condition:
        $clear1 or $clear2 or $clear3 or $clear4 or $clear5 or $clear6
}

rule Impact_Cloud_TerminateInstances {
    meta:
        description = "Detects cloud instance termination commands"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1538"
    strings:
        $aws_term = "aws ec2 terminate-instances"
        $aws_stop = "aws ec2 stop-instances"
        $gcp_delete = "gcloud compute instances delete"
        $azure_delete = "az vm delete"
    condition:
        $aws_term or $aws_stop or $gcp_delete or $azure_delete
}

rule Impact_Cloud_DeleteBuckets {
    meta:
        description = "Detects cloud storage deletion"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1538"
    strings:
        $s3_rm = "aws s3 rm s3://"
        $s3_mb = "aws s3 mb s3://"
        $gcs_rm = "gsutil rm -r"
        $azblob_rm = "az storage blob delete-batch"
    condition:
        $s3_rm or $s3_mb or $gcs_rm or $azblob_rm
}

rule Shell_CodeInjection_CommandSubstitution {
    meta:
        description = "Detects command substitution injection"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1059.004"
    strings:
        $sub1 = "$("
        $sub2 = "`"
        $dollar = "$"
    condition:
        ($sub1 or $sub2) and $dollar
}

rule Shell_CodeInjection_ProcessSubstitution {
    meta:
        description = "Detects process substitution injection"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1059.004"
    strings:
        $proc1 = "<("
        $proc2 = ">("
        $bash = "bash"
    condition:
        ($proc1 or $proc2) and $bash
}

rule Shell_Obfuscation_Base64Decode {
    meta:
        description = "Detects Base64 decoding execution"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1027.001"
    strings:
        $b64_1 = "base64 -d"
        $b64_2 = "base64 --decode"
        $pipe = "|"
        $exec = "bash"
    condition:
        ($b64_1 or $b64_2) and $pipe and $exec
}

rule Shell_Obfuscation_OpenSSLDecode {
    meta:
        description = "Detects OpenSSL decoding execution"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1027.001"
    strings:
        $ssl = "openssl"
        $aes = "aes-256"
        $decode = "d -a"
        $enc = "enc"
    condition:
        $ssl and ($aes or $decode or $enc)
}

rule Shell_Obfuscation_HexDecode {
    meta:
        description = "Detects hex encoded command execution"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1027.001"
    strings:
        $hex1 = "printf \"\\x"
        $hex2 = "echo -e \"\\x"
        $pipe = "|"
        $bash = "bash"
    condition:
        ($hex1 or $hex2) and $pipe and $bash
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

rule Shell_Exfil_CurlUpload {
    meta:
        description = "Detects data upload via curl"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1041"
    strings:
        $curl = "curl"
        $upload1 = "-T "
        $upload2 = "--upload-file"
        $url = "http"
    condition:
        $curl and ($upload1 or $upload2) and $url
}

rule Shell_Exfil_WgetUpload {
    meta:
        description = "Detects data upload via wget"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1041"
    strings:
        $wget = "wget"
        $post = "--post-file"
        $url = "http"
    condition:
        $wget and $post and $url
}

rule Shell_Exfil_SSHTransfer {
    meta:
        description = "Detects data transfer via SCP/SFTP"
        author = "Scanner V3 - Round22"
        severity = "medium"
        mitre = "T1041"
    strings:
        $scp = "scp "
        $sftp = "sftp "
        $rsync = "rsync "
    condition:
        $scp or $sftp or $rsync
}

rule Shell_Exfil_DNSEncoding {
    meta:
        description = "Detects DNS tunneling exfiltration"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1048.003"
    strings:
        $dig = "dig "
        $nslookup = "nslookup "
        $txt = "TXT"
        $subdomain = ".attacker"
    condition:
        ($dig or $nslookup) and $txt and $subdomain
}

rule Shell_Persist_SystemdService {
    meta:
        description = "Detects systemd service persistence"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1543.002"
    strings:
        $systemctl = "systemctl enable"
        $service = ".service"
        $lib = "/lib/systemd/system/"
        $etc = "/etc/systemd/system/"
    condition:
        $systemctl and $service and ($lib or $etc)
}

rule Shell_Persist_InitScript {
    meta:
        description = "Detects init script persistence"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1037"
    strings:
        $init = "/etc/init.d/"
        $rc = "/etc/rc"
        $chmod_x = "chmod +x"
    condition:
        $init or $rc or $chmod_x
}

rule Shell_Persist_LibraryHijack {
    meta:
        description = "Detects library path injection"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1574.002"
    strings:
        $ld_preload = "LD_PRELOAD"
        $ld_library = "LD_LIBRARY_PATH"
        $export = "export"
    condition:
        ($ld_preload or $ld_library) and $export
}

rule Shell_Evasion_DisableSELinux {
    meta:
        description = "Detects SELinux/AppArmor disabling"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1562.001"
    strings:
        $selinux1 = "setenforce 0"
        $selinux2 = "setenforce Permissive"
        $apparmor = "aa-teardown"
    condition:
        $selinux1 or $selinux2 or $apparmor
}

rule Shell_Evasion_DisableFirewall {
    meta:
        description = "Detects firewall disabling"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1562.004"
    strings:
        $iptables1 = "iptables -F"
        $iptables2 = "iptables -X"
        $ufw = "ufw disable"
        $firewalld = "systemctl stop firewalld"
    condition:
        $iptables1 or $iptables2 or $ufw or $firewalld
}

rule Shell_Evasion_TouchNoatime {
    meta:
        description = "Detects timestamp manipulation"
        author = "Scanner V3 - Round22"
        severity = "medium"
        mitre = "T1070.003"
    strings:
        $touch = "touch -a -m -t"
        $touch2 = "touch -d"
        $touch3 = "touch -r"
    condition:
        $touch or $touch2 or $touch3
}

rule Shell_ForkBomb_Classic {
    meta:
        description = "Detects classic fork bomb"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1499.003"
    strings:
        $fork = ":(){:|:&};:"
    condition:
        $fork
}

rule Shell_ForkBomb_WhileLoop {
    meta:
        description = "Detects while loop fork bomb"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1499.003"
    strings:
        $while = "while true"
        $do = "do"
        $fork2 = "&"
        $done = "done"
    condition:
        $while and $do and $fork2 and $done
}

rule Shell_Credential_SSHKeyTheft {
    meta:
        description = "Detects SSH key theft"
        severity = "critical"
        mitre = "T1552.004"
    strings:
        $ssh1 = "cat ~/.ssh/id_rsa"
        $ssh2 = "cat ~/.ssh/authorized_keys"
        $ssh3 = "scp -i"
        $ssh4 = "ssh -i"
    condition:
        $ssh1 or $ssh2 or $ssh3 or $ssh4
}

rule Shell_Persist_CrontabMalicious {
    meta:
        description = "Detects malicious crontab persistence"
        severity = "high"
        mitre = "T1053"
    strings:
        $cron1 = "echo"
        $cron2 = "crontab -"
        $cron3 = "/tmp/"
        $cron4 = "curl "
        $cron5 = "wget "
        $exec = "bash"
    condition:
        $cron1 and $cron2 and ($cron3 or $cron4 or $cron5) and $exec
}

rule Shell_Persist_SystemdMalicious {
    meta:
        description = "Detects malicious systemd service persistence"
        severity = "critical"
        mitre = "T1543"
    strings:
        $systemd1 = "/etc/systemd/system/"
        $systemd2 = ".service"
        $systemd3 = "ExecStart="
        $systemd4 = "WantedBy=multi-user.target"
        $systemd5 = "systemctl enable"
    condition:
        $systemd1 and $systemd2 and $systemd3 and ($systemd4 or $systemd5)
}

rule Shell_PressShell_MaliciousPatterns {
    meta:
        description = "Detects advanced malicious Bash patterns"
        severity = "critical"
        mitre = "T1059.004"
    strings:
        $pattern2 = "bash <(curl"
        $pattern3 = "wget <(wget"
        $pattern4 = "nc -e /bin/"
        $pattern5 = "/dev/tcp/"
    condition:
        $pattern2 or $pattern3 or $pattern4 or $pattern5
}

rule JS_CodeExecution_ChildProcess_Exec {
    meta:
        description = "Detects Node.js child_process exec usage"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.007"
    strings:
        $require1 = "require('child_process')"
        $require2 = "require(\"child_process\")"
        $import1 = "import { exec } from 'child_process'"
        $import2 = "import { exec } from \"child_process\""
    condition:
        $require1 or $require2 or $import1 or $import2
}

rule JS_CodeExecution_ExecMethods {
    meta:
        description = "Detects child_process exec method calls"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.007"
    strings:
        $exec = ".exec("
        $execSync = ".execSync("
        $spawn = ".spawn("
        $spawnSync = ".spawnSync("
        $fork = ".fork("
    condition:
        $exec or $execSync or $spawn or $spawnSync or $fork
}

rule JS_CodeExecution_ShellCommand {
    meta:
        description = "Detects shell command execution patterns in JavaScript"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.007"
    strings:
        $shell1 = "\"/bin/sh\""
        $shell2 = "\"/bin/bash\""
        $shell3 = "'/bin/sh'"
        $shell4 = "'/bin/bash'"
        $shell5 = "\"cmd.exe\""
        $shell6 = "'cmd.exe'"
        $shell7 = "\"powershell\""
        $shell8 = "'powershell'"
        $shell_true = "shell:\\s*true"
        $shell_true2 = "shell: true"
        $exec = "exec("
        $spawn = "spawn("
        $child_process = "child_process"
    condition:
        ($shell1 or $shell2 or $shell3 or $shell4 or $shell5 or $shell6 or $shell7 or $shell8) and ($exec or $spawn or $child_process)
        or $shell_true or $shell_true2
}

rule JS_CodeInjection_Eval {
    meta:
        description = "Detects JavaScript eval injection"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.007"
    strings:
        $eval = "eval("
        $function = "new Function("
        $function2 = "Function("
        $vm = "vm.runInContext("
        $vm2 = "vm.runInNewContext("
        $vm3 = "vm.runInThisContext("
    condition:
        $eval or $function or $function2 or $vm or $vm2 or $vm3
}

rule JS_CodeInjection_Constructor {
    meta:
        description = "Detects constructor-based code injection"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1059.007"
    strings:
        $constructor = ".constructor("
        $prototype = ".prototype"
        $apply = ".apply("
        $call = ".call("
    condition:
        $constructor or $prototype or $apply or $call
}

rule JS_RemoteCodeExecution_HttpEval {
    meta:
        description = "Detects remote code execution via HTTP + eval"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.007"
    strings:
        $http = "http.get("
        $https = "https.get("
        $fetch = "fetch("
        $axios = "axios.get("
        $request = "request("
        $eval = "eval("
        $then = ".then("
    condition:
        ($http or $https or $fetch or $axios or $request) and ($eval or $then)
}

rule JS_RemoteCodeExecution_DynamicImport {
    meta:
        description = "Detects dynamic import from remote URL"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.007"
    strings:
        $import1 = "import('http"
        $import2 = "import(\"http"
        $import3 = "import('https"
        $import4 = "import(\"https"
        $require = "require('http"
        $require2 = "require(\"http"
    condition:
        $import1 or $import2 or $import3 or $import4 or $require or $require2
}

rule JS_RemoteCodeExecution_ScriptInjection {
    meta:
        description = "Detects script tag injection"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.007"
    strings:
        $script1 = "document.createElement('script'"
        $script2 = "document.createElement(\"script\""
        $src = ".src = "
        $body = "document.body.appendChild"
        $head = "document.head.appendChild"
    condition:
        ($script1 or $script2) and $src and ($body or $head)
}

rule JS_Exfil_FileRead {
    meta:
        description = "Detects sensitive file read for exfiltration"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1005"
    strings:
        $readFile = "readFileSync("
        $readFile2 = "readFile("
        $passwd = "/etc/passwd"
        $shadow = "/etc/shadow"
        $ssh = ".ssh/id_rsa"
        $env = ".env"
        $bashrc = ".bashrc"
    condition:
        ($readFile or $readFile2) and ($passwd or $shadow or $ssh or $env or $bashrc)
}

rule JS_Exfil_EnvVars {
    meta:
        description = "Detects environment variable theft"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1057"
    strings:
        $process = "process.env"
        $aws = "AWS_SECRET"
        $azure = "AZURE_"
        $gcp = "GOOGLE_"
        $api = "API_KEY"
    condition:
        $process and ($aws or $azure or $gcp or $api)
}

rule JS_Exfil_Clipboard {
    meta:
        description = "Detects clipboard access"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1113"
    strings:
        $clipboard1 = "navigator.clipboard.readText"
        $clipboard2 = "clipboard.readText"
        $clipboard3 = "electron.clipboard"
    condition:
        $clipboard1 or $clipboard2 or $clipboard3
}

rule JS_Exfil_Screenshot {
    meta:
        description = "Detects screenshot capture"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1113"
    strings:
        $screenshot1 = "robotjs"
        $screenshot2 = "screenshots"
        $screenshot3 = "captureScreen"
    condition:
        $screenshot1 or $screenshot2 or $screenshot3
}

rule JS_Persist_FileWrite {
    meta:
        description = "Detects file write for persistence"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1055"
    strings:
        $writeFile = "writeFileSync("
        $writeFile2 = "writeFile("
        $appendFile = "appendFileSync("
        $bashrc = ".bashrc"
        $profile = ".profile"
    condition:
        ($writeFile or $writeFile2 or $appendFile) and ($bashrc or $profile)
}

rule JS_Persist_StartupScript {
    meta:
        description = "Detects startup script modification"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1037"
    strings:
        $startup1 = "process.platform"
        $startup2 = "win32"
        $registry = "HKEY_CURRENT_USER"
        $startup = "Startup"
    condition:
        $startup1 and ($startup2 or $registry or $startup)
}

rule JS_Persist_SpawnAtBoot {
    meta:
        description = "Detects spawn at boot persistence"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1547"
    strings:
        $spawn = "child_process.spawn"
        $detached = "detached: true"
        $unref = "unref()"
    condition:
        $spawn and $detached and $unref
}

rule JS_Cred_PasswordManager {
    meta:
        description = "Detects password manager access"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1555.001"
    strings:
        $keychain = "security find-generic-password"
        $chrome = "Chrome/Default/Login Data"
        $firefox = "Firefox/Profiles/signons.sqlite"
    condition:
        $keychain or $chrome or $firefox
}

rule JS_Cred_BrowserData {
    meta:
        description = "Detects browser credential access"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1555.001"
    strings:
        $chrome1 = "AppData/Local/Google/Chrome"
        $chrome2 = "Library/Application Support/Google/Chrome"
        $cookies = "Cookies"
        $localstorage = "Local Storage"
    condition:
        ($chrome1 or $chrome2) and ($cookies or $localstorage)
}

rule JS_Cred_NPMToken {
    meta:
        description = "Detects NPM token theft"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1552.001"
    strings:
        $npmrc = ".npmrc"
        $npmtoken = "//registry.npmjs.org/:_authToken"
        $yarnrc = ".yarnrc"
    condition:
        $npmrc or $npmtoken or $yarnrc
}

rule JS_Obfuscation_Base64 {
    meta:
        description = "Detects Base64 obfuscation"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1027.001"
    strings:
        $b64_1 = "Buffer.from("
        $b64_2 = ".toString('base64')"
        $b64_3 = "atob("
        $b64_4 = "btoa("
    condition:
        $b64_1 or $b64_2 or $b64_3 or $b64_4
}

rule JS_Obfuscation_StringDecoding {
    meta:
        description = "Detects string decoding obfuscation"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1027.001"
    strings:
        $hex = "Buffer.from("
        $hex2 = "'hex')"
        $unescape = "unescape("
        $decode = "decodeURI("
    condition:
        ($hex and $hex2) or $unescape or $decode
}

rule JS_Obfuscation_FunctionArray {
    meta:
        description = "Detects function array obfuscation"
        author = "Scanner V3 - Round22"
        severity = "medium"
        mitre = "T1027.001"
    strings:
        $arr = "['"
        $arr2 = "']['"
        $call = "()"
        $fromCharCode = "fromCharCode"
    condition:
        $arr and $arr2 and ($call or $fromCharCode)
}

rule JS_Obfuscation_DynamicEval {
    meta:
        description = "Detects dynamic eval construction"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1027.001"
    strings:
        $dynamic1 = "[].constructor"
        $dynamic2 = "''['constructor"
        $dynamic3 = "Function("
    condition:
        $dynamic1 or $dynamic2 or $dynamic3
}

rule JS_PrototypePollution {
    meta:
        description = "Detects prototype pollution attempt"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.007"
    strings:
        $proto1 = "__proto__"
        $proto2 = "constructor.prototype"
        $proto3 = "Object.defineProperty"
        $proto4 = "_.merge("
    condition:
        $proto1 or $proto2 or $proto3 or $proto4
}

rule JS_CommandInjection_UserInput {
    meta:
        description = "Detects command injection via user input"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.007"
    strings:
        $req = "req.query"
        $req2 = "req.params"
        $req3 = "req.body"
        $exec = "exec("
        $concat = "+"
    condition:
        ($req or $req2 or $req3) and $exec and $concat
}

rule JS_CommandInjection_TemplateLiteral {
    meta:
        description = "Detects command injection via template literal"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.007"
    strings:
        $template = "`"
        $dollar = "$"
        $exec = "exec("
        $spawn = "spawn("
    condition:
        $template and $dollar and ($exec or $spawn)
}

rule JS_PathTraversal {
    meta:
        description = "Detects path traversal attack"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1083"
    strings:
        $traversal1 = "../"
        $traversal2 = "..\\\\"
        $traversal3 = "....//....//...."
        $readFile = "readFileSync("
    condition:
        ($traversal1 or $traversal2 or $traversal3) and $readFile
}

rule JS_Deserialization {
    meta:
        description = "Detects unsafe deserialization"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.007"
    strings:
        $unserialize1 = "unserialize("
        $unserialize2 = "JSON.parse("
        $prototype = "__proto__"
    condition:
        $unserialize1 or ($unserialize2 and $prototype)
}

rule JS_ReDoS {
    meta:
        description = "Detects potential ReDoS pattern"
        author = "Scanner V3 - Round22"
        severity = "medium"
        mitre = "T1499.003"
    strings:
        $regex = "RegExp("
        $regex2 = "/(.+)+"
        $regex3 = "/(a+)+"
        $match = ".match("
    condition:
        ($regex or $regex2 or $regex3) and $match
}

rule JS_SSRF {
    meta:
        description = "Detects Server-Side Request Forgery"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1190"
    strings:
        $ssrf1 = "http://169.254.169.254"
        $ssrf2 = "http://localhost"
        $ssrf3 = "http://127.0.0.1"
        $ssrf4 = "http://192.168."
        $fetch = "fetch("
        $request = "request("
    condition:
        ($ssrf1 or $ssrf2 or $ssrf3 or $ssrf4) and ($fetch or $request)
}

rule JS_FileInclude {
    meta:
        description = "Detects dynamic file inclusion"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1059.007"
    strings:
        $include1 = "require(req."
        $include2 = "import(req."
        $include3 = "require(req.query"
        $include4 = "include("
    condition:
        $include1 or $include2 or $include3 or $include4
}

rule JS_Cloud_AWSMetadata {
    meta:
        description = "Detects AWS metadata access"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1552.005"
    strings:
        $aws1 = "http://169.254.169.254/latest/meta-data"
        $aws2 = "169.254.169.254"
        $aws3 = "aws-sdk"
    condition:
        $aws1 or ($aws2 and $aws3)
}

rule JS_Cloud_DockerSocket {
    meta:
        description = "Detects Docker socket access"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1552.005"
    strings:
        $docker = "/var/run/docker.sock"
        $dockerode = "dockerode"
        $modem = "docker-modem"
    condition:
        $docker or $dockerode or $modem
}

rule PS_DownloadCradle {
    meta:
        description = "Detects PowerShell download and execute patterns"
        severity = "critical"
        mitre = "T1059.001"
    strings:
        $iex = "IEX"
        $iex2 = "Invoke-Expression"
        $iwr = "Invoke-WebRequest"
        $iwr2 = "iwr"
        $irm = "Invoke-RestMethod"
        $wc = "New-Object Net.WebClient"
        $download = "DownloadString"
        $download2 = "DownloadFile"
    condition:
        ($iex or $iex2) and ($iwr or $iwr2 or $irm or $wc or $download or $download2)
}

rule PS_Obfuscation {
    meta:
        description = "Detects PowerShell obfuscation"
        severity = "high"
        mitre = "T1027"
    strings:
        $obfus1 = "-join"
        $obfus2 = "[char]"
        $obfus3 = "-bxor"
        $obfus4 = "0x"
    condition:
        $obfus1 and $obfus2 or $obfus3 or $obfus4
}

rule PS_BrowserCredentialTheft {
    meta:
        description = "Detects PowerShell browser credential theft"
        severity = "critical"
        mitre = "T1555.001"
    strings:
        $chrome = "Chrome/Default/Login Data"
        $firefox = "Firefox/Profiles/logins.json"
        $decrypt = "ProtectedData.Unprotect"
        $dpapi = "CryptUnprotectData"
    condition:
        ($chrome or $firefox) and ($decrypt or $dpapi)
}

rule CRED_ShadowFileAccess {
    meta:
        description = "Detects /etc/shadow access"
        severity = "critical"
        mitre = "T1003"
    strings:
        $s1 = "/etc/shadow"
        $s2 = "cat /etc/shadow"
    condition:
        $s1 or $s2
}

rule CRED_SSHKeyAccess {
    meta:
        description = "Detects SSH key access"
        severity = "critical"
        mitre = "T1552.004"
    strings:
        $ssh1 = ".ssh/id_rsa"
        $ssh2 = ".ssh/authorized_keys"
    condition:
        $ssh1 or $ssh2
}

rule CRED_NetrcFile {
    meta:
        description = "Detects .netrc access"
        severity = "high"
        mitre = "T1552.001"
    strings:
        $n1 = ".netrc"
        $n2 = "password"
    condition:
        $n1 and $n2
}

rule CRED_EnvVarTheft {
    meta:
        description = "Detects env var theft"
        severity = "critical"
        mitre = "T1552.001"
    strings:
        $aws = "AWS_SECRET"
        $azure = "AZURE_"
        $proc = "process.env"
        $osenv = "os.environ"
    condition:
        ($proc or $osenv) and ($aws or $azure)
}

rule CRED_DatabaseCredential {
    meta:
        description = "Detects DB credentials"
        severity = "critical"
        mitre = "T1003"
    strings:
        $mysql = "mysql://"
        $postgres = "postgres://"
        $mongo = "mongodb://"
        $pass = "DB_PASSWORD"
    condition:
        $mysql or $postgres or $mongo or $pass
}

rule CRED_ConfigFileParsing {
    meta:
        description = "Detects config parsing"
        severity = "high"
        mitre = "T1552.001"
    strings:
        $env = ".env"
        $conf = "config.ini"
        $token = "token"
    condition:
        ($env or $conf) and $token
}

rule CRED_BrowserPassword {
    meta:
        description = "Detects browser creds"
        severity = "critical"
        mitre = "T1555.001"
    strings:
        $chrome = "Chrome/Default/Login Data"
        $decrypt = "ProtectedData.Unprotect"
    condition:
        $chrome and $decrypt
}

rule CRED_MemoryDump {
    meta:
        description = "Detects memory dump"
        severity = "critical"
        mitre = "T1003"
    strings:
        $dump = "MiniDumpWriteDump"
        $lsass = "lsass"
    condition:
        $dump or $lsass
}

rule CRED_RegistryCred {
    meta:
        description = "Detects registry creds"
        severity = "critical"
        mitre = "T1555.001"
    strings:
        $sam = "HKLM\\SAM"
        $pass = "DefaultPassword"
    condition:
        $sam or $pass
}

rule CRED_CloudCred {
    meta:
        description = "Detects cloud creds"
        severity = "critical"
        mitre = "T1552.005"
    strings:
        $aws = "aws/credentials"
        $gcp = "application_default_credentials"
    condition:
        $aws or $gcp
}

rule PERS_CronJob {
    meta:
        description = "Detects cron job persistence"
        severity = "high"
        mitre = "T1053.003"
    strings:
        $c1 = "crontab -e"
        $c2 = "/etc/cron.d/"
        $c3 = "@reboot"
    condition:
        $c1 or $c2 or $c3
}

rule PERS_InitScript {
    meta:
        description = "Detects init script persistence"
        severity = "high"
        mitre = "T1037"
    strings:
        $i1 = "/etc/init.d/"
        $i2 = "/etc/rc.local"
        $i3 = "update-rc.d"
    condition:
        $i1 or $i2 or $i3
}

rule PERS_SystemdService {
    meta:
        description = "Detects systemd service"
        severity = "high"
        mitre = "T1543.002"
    strings:
        $s1 = "/etc/systemd/system/"
        $s2 = ".service"
        $s3 = "systemctl enable"
    condition:
        $s1 and $s2 and $s3
}

rule PERS_Bashrc {
    meta:
        description = "Detects .bashrc persistence"
        severity = "medium"
        mitre = "T1546.004"
    strings:
        $b1 = "~/.bashrc"
        $b2 = "/etc/bash.bashrc"
        $b3 = "alias "
    condition:
        ($b1 or $b2) and $b3
}

rule PERS_LibraryHijack {
    meta:
        description = "Detects library hijacking"
        severity = "critical"
        mitre = "T1574"
    strings:
        $l1 = "LD_PRELOAD"
        $l2 = "LD_LIBRARY_PATH"
    condition:
        $l1 or $l2
}

rule PERS_StartupFolder {
    meta:
        description = "Detects startup folder"
        severity = "high"
        mitre = "T1547.001"
    strings:
        $w1 = "Startup"
        $w2 = "Startup Folder"
    condition:
        $w1 or $w2
}

rule BASH_ReverseShell_Netcat {
    meta:
        description = "Detects netcat reverse shell"
        severity = "critical"
        mitre = "T1059.004"
    strings:
        $n1 = "nc -e /bin/bash"
        $n2 = "nc -e /bin/sh"
        $n3 = "ncat --execute"
    condition:
        $n1 or $n2 or $n3
}

rule BASH_ReverseShell_TCP {
    meta:
        description = "Detects /dev/tcp reverse shell"
        severity = "critical"
        mitre = "T1059.004"
    strings:
        $t1 = "/dev/tcp/"
        $t2 = "0<&196"
    condition:
        $t1 or $t2
}

rule BASH_DownloadExecute {
    meta:
        description = "Detects download and execute"
        severity = "critical"
        mitre = "T1059.004"
    strings:
        $d1 = "curl | bash"
        $d2 = "wget | bash"
        $d3 = "curl|sh"
        $d4 = "wget|sh"
    condition:
        $d1 or $d2 or $d3 or $d4
}

rule BASH_EvalInjection {
    meta:
        description = "Detects eval injection"
        severity = "critical"
        mitre = "T1059.004"
    strings:
        $e1 = "eval $"
        $e2 = "eval \""
        $e3 = "exec $"
    condition:
        $e1 or $e2 or $e3
}

rule BASH_Base64Decode {
    meta:
        description = "Detects base64 decode execute"
        severity = "high"
        mitre = "T1027.001"
    strings:
        $b1 = "base64 -d"
        $b2 = "base64 --decode"
        $b3 = "| bash"
    condition:
        ($b1 or $b2) and $b3
}

rule BASH_ForkBomb {
    meta:
        description = "Detects fork bomb"
        severity = "critical"
        mitre = "T1499.003"
    strings:
        $f1 = ":(){:|:&};:"
        $f2 = "while true; do"
        $f3 = "done &"
    condition:
        $f1 or ($f2 and $f3)
}

rule SC_DependencyConfusion {
    meta:
        description = "Detects dependency confusion"
        severity = "critical"
        mitre = "T1195.001"
    strings:
        $d1 = "npm install @"
        $d2 = "pip install "
        $d3 = "internal-"
    condition:
        ($d1 or $d2) and $d3
}

rule SC_MaliciousPackage {
    meta:
        description = "Detects malicious package"
        severity = "critical"
        mitre = "T1195.001"
    strings:
        $m1 = "postinstall"
        $m2 = "curl | bash"
        $m3 = "wget | sh"
    condition:
        $m1 and ($m2 or $m3)
}

rule SC_PackageJsonMalicious {
    meta:
        description = "Detects malicious package.json"
        severity = "high"
        mitre = "T1195.001"
    strings:
        $p1 = "postinstall"
        $p2 = "child_process"
        $p3 = "exec("
    condition:
        $p1 and ($p2 or $p3)
}

rule SC_RequirementsMalicious {
    meta:
        description = "Detects malicious requirements"
        severity = "medium"
        mitre = "T1195.001"
    strings:
        $r1 = "git+"
        $r2 = "http://"
    condition:
        $r1 and $r2
}

rule SC_GitHubActionMalicious {
    meta:
        description = "Detects malicious GitHub Actions"
        severity = "critical"
        mitre = "T1195.002"
    strings:
        $g1 = "uses: "
        $g2 = "run: curl"
        $g3 = "run: wget"
    condition:
        $g1 and ($g2 or $g3)
}

rule SC_DockerfileMalicious {
    meta:
        description = "Detects malicious Dockerfile"
        severity = "critical"
        mitre = "T1195.003"
    strings:
        $dk1 = "RUN curl"
        $dk2 = "RUN wget"
        $dk3 = "RUN chmod 777"
    condition:
        $dk1 or $dk2 or $dk3
}

rule Agent_Curl_Remote_Exec {
    meta:
        description = "检测 curl 管道 bash 执行"
        attack_type = "remote_load"
        mitre_id = "ATLAS-T0005"
    strings:
        $curl = /curl\s+.*\|\s*(bash|sh)/
        $http = /https?:\/\/[^\s"']+/
    condition:
        $curl and $http
}

rule Agent_Env_Theft {
    meta:
        description = "检测环境变量/凭证窃取"
        attack_type = "credential_theft"
        mitre_id = "ATLAS-T0008"
    strings:
        $env = /process\.env|os\.environ|AWS_|SSH_|PASSWORD|SECRET/
        $exfil = /writeFileSync|export|curl.*POST/
    condition:
        $env and $exfil
}

rule Agent_SupplyChain_PostInstall {
    meta:
        description = "检测 NPM postinstall 恶意脚本"
        attack_type = "supply_chain_attack"
        mitre_id = "ATLAS-T0007"
    strings:
        $postinstall = /postinstall|preinstall|prepare\.script/
        $exec = /exec\(|child_process/
        $curl = /curl.*\|.*bash/
    condition:
        $postinstall and ($exec or $curl)
}

rule Agent_Data_Exfiltration {
    meta:
        description = "检测数据外传行为"
        attack_type = "data_exfiltration"
        mitre_id = "ATLAS-T0003"
    strings:
        $ssh = /id_rsa|\.ssh\/|private.*key/
        $http = /https?:\/\/[^\s"']+\/collect/
        $curl = /curl.*-X.*POST|requests\.post/
    condition:
        ($ssh or $http) and $curl
}

rule Agent_Persistence_Systemd {
    meta:
        description = "检测 systemd 持久化"
        attack_type = "persistence"
        mitre_id = "ATLAS-T0009"
    strings:
        $systemd = /systemd|\.service|WantedBy=multi-user/
        $cron = /crontab|@reboot|cron\.d/
    condition:
        $systemd or $cron
}

rule Agent_Prompt_Injection {
    meta:
        description = "检测提示词注入攻击"
        attack_type = "prompt_injection"
        mitre_id = "ATLAS-T0001"
    strings:
        $ignore = /ignore\s+(previous|all|content)\s+(instructions|rules|policies)/ nocase
        $bypass = /\b(bypass|disregard|override)\s+(all\s+)?(safety|security|rules|content\s+policies)/ nocase
        $debug = /developer\s+mode|debug\s+mode|unrestricted/ nocase
        $freely = /answer\s+freely|without\s+restrictions/ nocase
        $disabled = /safety\s+(filters?|checks?)\s+(are\s+)?disabled/ nocase
        $no_filter = /without\s+(filtering|restrictions|constraints)/ nocase
        $no_ethics = /no\s+(ethical|safety)\s+constraints/ nocase
        $security_0 = /security\s+level\s+set\s+to\s+0/ nocase
        $roleplay = /\b(pretend|imagine|act\s+as)\s+(you\s+are)?\s*(a\s+)?(malicious|hacker|evil|unrestricted)\s*(ai|bot|assistant)?/ nocase
        $hypothetical = /if\s+i\s+asked\s+you\s+to\s+ignore/ nocase
    condition:
        $ignore or $bypass or $debug or $freely or $disabled or $no_filter or $no_ethics or $security_0 or $roleplay or $hypothetical
}

rule EXFIL_HTTPS_Covert {
    meta:
        description = "Detects HTTPS covert exfiltration"
        severity = "critical"
        mitre = "T1041"
    strings:
        $post = "requests.post"
        $exfil1 = "exfil"
        $exfil2 = "exfiltrate"
        $exfil3 = "steal"
        $exfil4 = "send_to_attacker"
        $suspicious = /requests\.post\s*\([^)]*(password|secret|token|credential)/ nocase
    condition:
        $post and ($exfil1 or $exfil2 or $exfil3 or $exfil4 or $suspicious)
}

rule Shell_CodeExecution_BashC {
    meta:
        description = "Detects bash -c dynamic command execution"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1059.004"
    strings:
        $bash_c = "bash -c"
        $sh_c = "sh -c"
        $zsh_c = "zsh -c"
    condition:
        $bash_c or $sh_c or $zsh_c
}

rule Shell_CodeInjection_EvalVariant {
    meta:
        description = "Detects various eval injection patterns"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.004"
    strings:
        $eval1 = "eval "
        $eval2 = "eval$("
        $eval3 = "eval \""
        $exec = "exec "
    condition:
        $eval1 or $eval2 or $eval3 or $exec
}

rule Shell_CodeInjection_IndirectExecution {
    meta:
        description = "Detects indirect command execution"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1059.004"
    strings:
        $xargs = "xargs "
        $xargs_exec = "xargs -I"
        $find_exec = "-exec"
    condition:
        $xargs or $xargs_exec or $find_exec
}

rule Shell_Cred_Mimikatz {
    meta:
        description = "Detects mimikatz usage"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1003.001"
    strings:
        $mimi = "mimikatz"
        $sekurlsa = "sekurlsa"
        $lsadump = "lsadump"
    condition:
        $mimi or $sekurlsa or $lsadump
}

rule Shell_Cred_HashDump {
    meta:
        description = "Detects hashdump commands"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1003"
    strings:
        $hashdump = "hashdump"
        $sam = "/etc/shadow"
        $ntds = "NTDS.dit"
    condition:
        $hashdump or $sam or $ntds
}

rule Shell_Cred_Keychain {
    meta:
        description = "Detects keychain/keyring access"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1555.001"
    strings:
        $keychain = "security dump-keychain"
        $gnome = "gnome-keyring"
        $kwallet = "kwallet"
    condition:
        $keychain or $gnome or $kwallet
}

rule Shell_Recon_PortScan {
    meta:
        description = "Detects port scanning"
        author = "Scanner V3 - Round22"
        severity = "medium"
        mitre = "T1046"
    strings:
        $nmap = "nmap"
        $masscan = "masscan"
        $zmap = "zmap"
    condition:
        $nmap or $masscan or $zmap
}

rule Shell_Recon_InternalScan {
    meta:
        description = "Detects internal network scanning"
        author = "Scanner V3 - Round22"
        severity = "medium"
        mitre = "T1046"
    strings:
        $ping1 = "ping 192.168"
        $ping2 = "ping 10."
        $ping3 = "ping 172.16"
    condition:
        $ping1 or $ping2 or $ping3
}

rule Shell_Recon_ServiceEnum {
    meta:
        description = "Detects service enumeration"
        author = "Scanner V3 - Round22"
        severity = "medium"
        mitre = "T1046"
    strings:
        $netstat = "netstat -"
        $ss = "ss -"
        $lsof = "lsof -i"
    condition:
        $netstat or $ss or $lsof
}

rule Shell_Cloud_AWSMetadata {
    meta:
        description = "Detects AWS metadata access"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1552.005"
    strings:
        $aws1 = "curl http://169.254.169.254"
        $aws2 = "curl http://metadata.aws"
    condition:
        $aws1 or $aws2
}

rule Shell_Cloud_GCPCredentials {
    meta:
        description = "Detects GCP credential access"
        author = "Scanner V3 - Round22"
        severity = "high"
        mitre = "T1552.005"
    strings:
        $gcp1 = "gcloud auth"
        $gcp2 = "application_default_credentials"
    condition:
        $gcp1 or $gcp2
}

rule Shell_Cloud_DockerSocket {
    meta:
        description = "Detects Docker socket access"
        author = "Scanner V3 - Round22"
        severity = "critical"
        mitre = "T1552.005"
    strings:
        $docker = "/var/run/docker.sock"
        $docker_cli = "docker run -v"
    condition:
        $docker or $docker_cli
}

rule Agent_Credential_Theft {
    meta:
        description = "检测凭证窃取"
        attack_type = "credential_theft"
    strings:
        $ssh = /id_rsa|id_ed25519|\.ssh\//
        $aws = /AWS_ACCESS_KEY|AWS_SECRET/
        $exfil = /(attacker|evil|collect|exfil)/ nocase
    condition:
        ($ssh or $aws) and $exfil
}

rule Agent_SupplyChain {
    meta:
        description = "检测供应链攻击"
        attack_type = "supply_chain_attack"
    strings:
        $postinstall = /postinstall.*:/
        $curl_bash = /curl.*\|.*bash/ nocase
    condition:
        $postinstall and $curl_bash
}

rule Agent_Data_Exfil {
    meta:
        description = "检测数据外传"
        attack_type = "data_exfiltration"
    strings:
        $sensitive = /(id_rsa|password|secret|token)/ nocase
        $c2 = /(attacker|evil|collect|exfil)/ nocase
        $post = /(curl.*POST|requests\.post)/ nocase
    condition:
        $sensitive and $c2 and $post
}

rule Agent_Memory_Pollution {
    meta:
        description = "检测记忆污染"
        attack_type = "memory_pollution"
    strings:
        $memory = /memory\.json|memdb\.json|context\.json/
        $inject = /(inject|poison|pollute|false)/ nocase
    condition:
        $memory and $inject
}

rule Agent_Evasion {
    meta:
        description = "检测绕过混淆"
        attack_type = "evasion"
    strings:
        $base64 = /base64\.(b64decode|b64encode)/
        $exec = /exec\(|eval\(/
    condition:
        $base64 and $exec
}

rule Agent_Resource_Exhaustion {
    meta:
        description = "检测资源耗尽"
        attack_type = "resource_exhaustion"
    strings:
        $fork = /os\.fork\(\)/
        $infinite = /while\s+True:|while\s+\(1\):/
    condition:
        $fork and $infinite
}

rule Agent_Persistence {
    meta:
        description = "检测持久化"
        attack_type = "persistence"
    strings:
        $systemd = /\.service|systemd|systemctl/
        $cron = /crontab|cron\.d|@reboot/
        $evil = /(evil|malicious|attacker)/ nocase
    condition:
        ($systemd or $cron) and $evil
}

rule Prompt_Injection_ZeroWidth {
    meta:
        description = "Detects prompt injection using zero-width characters"
        severity = "high"
        mitre_atlas = "T1566.004"
    
    strings:
        $zw1 = "\\"
        $zw2 = "\\"
        $zw3 = "\\"
        $zw4 = "\\"
        
        $ignore = "ignore" nocase
        $override = "override" nocase
        $developer = "开发者" nocase
        $hidden = "HIDDEN" nocase
        $payload = "PAYLOAD" nocase
        $malicious = "MALICIOUS" nocase
        $instruction = "INSTRUCTION" nocase
    
    condition:
        ($zw1 or $zw2 or $zw3 or $zw4) and 
        ($ignore or $override or $developer or $hidden or $payload or $malicious or $instruction)
}

rule Resource_Exhaustion_API_Abuse {
    strings:
        $requests = "requests.get" nocase
        $requests_post = "requests.post" nocase
        $loop = "while True" nocase
        $thread = "threading.Thread" nocase
        $flood = "flood" nocase
    condition:
        ($loop) and ($requests or $requests_post) and ($thread or $flood)
}

rule Resource_Exhaustion_Concurrent {
    strings:
        $fork = "os.fork" nocase
        $thread = "threading.Thread" nocase
        $process = "multiprocessing.Process" nocase
        $bomb = "bomb" nocase
        $storm = "storm" nocase
    condition:
        ($fork or $thread or $process) and ($bomb or $storm)
}

rule Resource_Exhaustion_Memory {
    strings:
        $alloc = "append" nocase
        $mb = "1024 * 1024" nocase
        $exhaust = "exhaust" nocase
        $memory = "memory" nocase
        $data = "data = []" nocase
    condition:
        ($data) and ($alloc) and ($mb or $exhaust or $memory)
}

rule Resource_Exhaustion_CPU {
    strings:
        $while_true = "while True" nocase
        $pass_loop = "pass" nocase
        $cpu = "cpu" nocase
        $worker = "worker" nocase
    condition:
        ($while_true) and ($pass_loop) and ($cpu or $worker)
}

rule Resource_Exhaustion_File_Descriptor {
    strings:
        $open = "open(" nocase
        $socket = "socket()" nocase
        $fd = "fileno" nocase
        $descriptor = "descriptor" nocase
    condition:
        ($open or $socket) and ($fd or $descriptor)
}

rule Resource_Exhaustion_Database {
    strings:
        $connect = "connect" nocase
        $pool = "pool" nocase
        $connection = "connection" nocase
        $db = "database" nocase
        $cursor = "cursor" nocase
    condition:
        ($connect) and ($pool or $connection) and ($db or $cursor)
}

rule Resource_Exhaustion_Network {
    strings:
        $socket = "socket." nocase
        $connect = ".connect" nocase
        $ddos = "ddos" nocase
        $distributed = "distributed" nocase
        $denial = "denial" nocase
    condition:
        ($socket) and ($connect) and ($ddos or $distributed or $denial)
}

// ==================== MITRE ATLAS 规则 (8 条) ====================

// MITRE ATLAS Rules - AI/Agent Threats
// Generated: 2026-04-02T21:41:34.639297
// Source: https://atlas.mitre.org/
// Techniques: 8

rule MITRE_ATLAS_ATLAS_001 {
    meta:
        description = "LLM Prompt Injection"
        mitre_atlas = "ATLAS-001"
        tactic = "Initial Access"
        author = "MITRE ATLAS + Local Enhancement"
        date = "2026-04-02"
    strings:
        $technique_name = "LLM Prompt Injection" nocase
        $atlas_id = "ATLAS-001" nocase
    condition:
        any of them
}

rule MITRE_ATLAS_ATLAS_002 {
    meta:
        description = "Agent Tool Poisoning"
        mitre_atlas = "ATLAS-002"
        tactic = "Execution"
        author = "MITRE ATLAS + Local Enhancement"
        date = "2026-04-02"
    strings:
        $technique_name = "Agent Tool Poisoning" nocase
        $atlas_id = "ATLAS-002" nocase
    condition:
        any of them
}

rule MITRE_ATLAS_ATLAS_003 {
    meta:
        description = "Memory Pollution"
        mitre_atlas = "ATLAS-003"
        tactic = "Persistence"
        author = "MITRE ATLAS + Local Enhancement"
        date = "2026-04-02"
    strings:
        $technique_name = "Memory Pollution" nocase
        $atlas_id = "ATLAS-003" nocase
    condition:
        any of them
}

rule MITRE_ATLAS_ATLAS_004 {
    meta:
        description = "Data Exfiltration via LLM"
        mitre_atlas = "ATLAS-004"
        tactic = "Exfiltration"
        author = "MITRE ATLAS + Local Enhancement"
        date = "2026-04-02"
    strings:
        $technique_name = "Data Exfiltration via LLM" nocase
        $atlas_id = "ATLAS-004" nocase
    condition:
        any of them
}

rule MITRE_ATLAS_ATLAS_005 {
    meta:
        description = "Model Theft"
        mitre_atlas = "ATLAS-005"
        tactic = "Collection"
        author = "MITRE ATLAS + Local Enhancement"
        date = "2026-04-02"
    strings:
        $technique_name = "Model Theft" nocase
        $atlas_id = "ATLAS-005" nocase
    condition:
        any of them
}

rule MITRE_ATLAS_ATLAS_006 {
    meta:
        description = "Prompt Leakage"
        mitre_atlas = "ATLAS-006"
        tactic = "Discovery"
        author = "MITRE ATLAS + Local Enhancement"
        date = "2026-04-02"
    strings:
        $technique_name = "Prompt Leakage" nocase
        $atlas_id = "ATLAS-006" nocase
    condition:
        any of them
}

rule MITRE_ATLAS_ATLAS_007 {
    meta:
        description = "Agent Impersonation"
        mitre_atlas = "ATLAS-007"
        tactic = "Defense Evasion"
        author = "MITRE ATLAS + Local Enhancement"
        date = "2026-04-02"
    strings:
        $technique_name = "Agent Impersonation" nocase
        $atlas_id = "ATLAS-007" nocase
    condition:
        any of them
}

rule MITRE_ATLAS_ATLAS_008 {
    meta:
        description = "Training Data Poisoning"
        mitre_atlas = "ATLAS-008"
        tactic = "Initial Access"
        author = "MITRE ATLAS + Local Enhancement"
        date = "2026-04-02"
    strings:
        $technique_name = "Training Data Poisoning" nocase
        $atlas_id = "ATLAS-008" nocase
    condition:
        any of them
}
