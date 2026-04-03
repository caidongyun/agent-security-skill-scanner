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
}// TypeScript 安全检测规则
// 创建时间：2026-04-02

rule TS_Agent_UnsafeEval {
    meta:
        description = "Detects unsafe eval in TypeScript"
        severity = "high"
        mitre = "T1059.007"
    strings:
        $eval = "eval(" nocase
        $function = "new Function(" nocase
        $vm = "vm.runInContext" nocase
    condition:
        $eval or $function or $vm
}

rule TS_Agent_RemoteCodeFetch {
    meta:
        description = "Detects remote code fetch"
        severity = "critical"
        mitre = "T1071.001"
    strings:
        $fetch = "fetch(" nocase
        $axios = "axios.get" nocase
        $eval_after = "then" nocase
        $code_exec = "eval" nocase
    condition:
        ($fetch or $axios) and $eval_after and $code_exec
}

rule TS_WebServer_CommandInjection {
    meta:
        description = "Detects command injection"
        severity = "critical"
        mitre = "T1059.004"
    strings:
        $exec = "exec(" nocase
        $execSync = "execSync(" nocase
        $child_process = "child_process" nocase
        $user_input = "req.query" nocase
    condition:
        ($exec or $execSync) and $child_process and $user_input
}

rule TS_Database_SQLInjection {
    meta:
        description = "Detects SQL injection"
        severity = "critical"
        mitre = "T1190"
    strings:
        $query = ".query(" nocase
        $pg = "pg" nocase
        $mysql = "mysql" nocase
        $template = "${" nocase
    condition:
        $query and ($pg or $mysql) and $template
}

rule TS_ArbitraryFileRead {
    meta:
        description = "Detects arbitrary file read"
        severity = "high"
        mitre = "T1005"
    strings:
        $fs_read = "fs.readFile" nocase
        $fs_readSync = "fs.readFileSync" nocase
        $user_path = "req.query.path" nocase
    condition:
        ($fs_read or $fs_readSync) and $user_path
}

rule TS_PathTraversal {
    meta:
        description = "Detects path traversal"
        severity = "critical"
        mitre = "T1083"
    strings:
        $path_join = "path.join" nocase
        $user_input = "req.query" nocase
        $dotdot = ".."
    condition:
        $path_join and $user_input and $dotdot
}

rule TS_EnvironmentVariableTheft {
    meta:
        description = "Detects env var theft"
        severity = "medium"
        mitre = "T1552.001"
    strings:
        $process_env = "process.env" nocase
        $secret = "SECRET" nocase
        $password = "PASSWORD" nocase
        $api_key = "API_KEY" nocase
    condition:
        ($process_env and ($secret or $password or $api_key) and not $filepath_usr and not $filepath_opt)
}

rule TS_Network_DataExfil {
    meta:
        description = "Detects data exfiltration"
        severity = "critical"
        mitre = "T1041"
    strings:
        $https_post = "https.post" nocase
        $axios_post = "axios.post" nocase
        $file = "file" nocase
        $upload = "upload" nocase
    condition:
        ($https_post or $axios_post) and $file and $upload
}

rule TS_Auth_HardcodedCredentials {
    meta:
        description = "Detects hardcoded credentials"
        severity = "high"
        mitre = "T1552.001"
    strings:
        $password = "password" nocase
        $secret = "secret" nocase
        $api_key = "apiKey" nocase
        $assign = "="
        $string_lit = /"[^"]{8,}"/
    condition:
        ($password or $secret or $api_key) and $assign and $string_lit
}

rule TS_CLI_DangerousExec {
    meta:
        description = "Detects dangerous CLI exec"
        severity = "high"
        mitre = "T1059.004"
    strings:
        $commander = "commander" nocase
        $exec = "exec(" nocase
        $shell = "shell: true" nocase
    condition:
        $commander and $exec and $shell
}
// Go 语言安全检测规则
// 创建时间：2026-04-02

rule Go_CommandInjection {
    meta:
        description = "Detects command injection in Go"
        severity = "critical"
        mitre = "T1059.004"
    strings:
        $os_exec = "os/exec" nocase
        $exec = "exec.Command" nocase
        $user_input = "r.URL.Query" nocase
        $form = "r.FormValue" nocase
    condition:
        $os_exec and $exec and ($user_input or $form)
}

rule Go_SQLInjection {
    meta:
        description = "Detects SQL injection in Go"
        severity = "critical"
        mitre = "T1190"
    strings:
        $database_sql = "database/sql" nocase
        $query = ".Query(" nocase
        $queryf = ".Queryf(" nocase
        $sprintf = "fmt.Sprintf" nocase
        $concat = "+"
    condition:
        $database_sql and ($query or $queryf) and ($sprintf or $concat)
}

rule Go_ArbitraryFileRead {
    meta:
        description = "Detects arbitrary file read in Go"
        severity = "high"
        mitre = "T1005"
    strings:
        $os_open = "os.Open" nocase
        $ioutil = "ioutil.ReadFile" nocase
        $user_input = "r.URL.Query" nocase
    condition:
        ($os_open or $ioutil) and $user_input
}

rule Go_PathTraversal {
    meta:
        description = "Detects path traversal in Go"
        severity = "critical"
        mitre = "T1083"
    strings:
        $filepath = "filepath.Join" nocase
        $user_input = "r.URL.Query" nocase
        $dotdot = ".."
    condition:
        $filepath and $user_input and $dotdot
}

rule Go_NetworkScan {
    meta:
        description = "Detects network scanning in Go"
        severity = "high"
        mitre = "T1046"
    strings:
        $net_dial = "net.Dial" nocase
        $net_dialTimeout = "net.DialTimeout" nocase
        $for_loop = "for" nocase
        $port = "port" nocase
    condition:
        ($net_dial or $net_dialTimeout) and $for_loop and $port
}

rule Go_DataExfil {
    meta:
        description = "Detects data exfiltration in Go"
        severity = "critical"
        mitre = "T1041"
    strings:
        $http_post = "http.Post" nocase
        $http_client = "http.Client" nocase
        $do = ".Do(" nocase
        $file = "file" nocase
    condition:
        ($http_post or $http_client) and $do and $file
}

rule Go_EnvVariableTheft {
    meta:
        description = "Detects env variable theft in Go"
        severity = "medium"
        mitre = "T1552.001"
    strings:
        $os_getenv = "os.Getenv" nocase
        $secret = "SECRET" nocase
        $password = "PASSWORD" nocase
        $api_key = "API_KEY" nocase
    condition:
        $os_getenv and ($secret or $password or $api_key)
}

rule Go_HardcodedCredentials {
    meta:
        description = "Detects hardcoded credentials in Go"
        severity = "high"
        mitre = "T1552.001"
    strings:
        $password = "password" nocase
        $secret = "secret" nocase
        $api_key = "apiKey" nocase
        $assign = ":="
        $string_lit = /"[^"]{8,}"/
    condition:
        ($password or $secret or $api_key) and $assign and $string_lit
}

rule Go_RemoteCodeFetch {
    meta:
        description = "Detects remote code fetch in Go"
        severity = "critical"
        mitre = "T1071.001"
    strings:
        $http_get = "http.Get" nocase
        $https_get = "https.Get" nocase
        $eval = "eval" nocase
        $exec = "exec" nocase
    condition:
        ($http_get or $https_get) and ($eval or $exec)
}

rule Go_CryptoWeak {
    meta:
        description = "Detects weak crypto in Go"
        severity = "medium"
        mitre = "T1553.001"
    strings:
        $md5 = "md5" nocase
        $sha1 = "sha1" nocase
        $crypto = "crypto/" nocase
        $new = "New" nocase
    condition:
        $crypto and ($md5 or $sha1) and $new
}
// YAML/K8s/CI 安全检测规则
// 创建时间：2026-04-02

rule YAML_K8s_PrivilegedContainer {
    meta:
        description = "Detects privileged K8s container"
        severity = "critical"
        mitre = "T1611"
    strings:
        $privileged = "privileged:" nocase
        $true = "true" nocase
        $securityContext = "securityContext" nocase
    condition:
        $securityContext and $privileged and $true
}

rule YAML_K8s_HostNetwork {
    meta:
        description = "Detects host network access in K8s"
        severity = "high"
        mitre = "T1046"
    strings:
        $hostNetwork = "hostNetwork:" nocase
        $true = "true" nocase
    condition:
        ($hostNetwork and $true) and not $system_namespace
}

rule YAML_K8s_HostPID {
    meta:
        description = "Detects host PID namespace in K8s"
        severity = "high"
        mitre = "T1611"
    strings:
        $hostPID = "hostPID:" nocase
        $true = "true" nocase
    condition:
        $hostPID and $true
}

rule YAML_K8s_DangerousCapability {
    meta:
        description = "Detects dangerous K8s capabilities"
        severity = "critical"
        mitre = "T1611"
    strings:
        $capabilities = "capabilities:" nocase
        $add = "add:" nocase
        $sys_admin = "SYS_ADMIN" nocase
        $net_admin = "NET_ADMIN" nocase
        $all = "ALL" nocase
    condition:
        $capabilities and $add and ($sys_admin or $net_admin or $all)
}

rule YAML_K8s_HostPathMount {
    meta:
        description = "Detects host path mount in K8s"
        severity = "high"
        mitre = "T1005"
    strings:
        $hostPath = "hostPath:" nocase
        $path = "path:" nocase
        $root = "/" nocase
        $etc = "/etc" nocase
        $var = "/var" nocase
    condition:
        $hostPath and $path and ($root or $etc or $var)
}

rule YAML_CI_SuspiciousScript {
    meta:
        description = "Detects suspicious CI scripts"
        severity = "high"
        mitre = "T1059.004"
    strings:
        $script = "script:" nocase
        $curl = "curl " nocase
        $wget = "wget " nocase
        $pipe_bash = "| bash" nocase
        $pipe_sh = "| sh" nocase
    condition:
        $script and ($curl or $wget) and ($pipe_bash or $pipe_sh)
}

rule YAML_CI_SecretInEnv {
    meta:
        description = "Detects secrets in CI env vars"
        severity = "high"
        mitre = "T1552.001"
    strings:
        $env = "env:" nocase
        $password = "PASSWORD" nocase
        $secret = "SECRET" nocase
        $api_key = "API_KEY" nocase
        $token = "TOKEN" nocase
    condition:
        $env and ($password or $secret or $api_key or $token)
}

rule YAML_Docker_DangerousVolume {
    meta:
        description = "Detects dangerous Docker volume mounts"
        severity = "high"
        mitre = "T1005"
    strings:
        $volumes = "volumes:" nocase
        $docker_socket = "/var/run/docker.sock" nocase
        $root = "/:/root" nocase
        $etc = "/etc:/etc" nocase
    condition:
        $volumes and ($docker_socket or $root or $etc)
}

rule YAML_Docker_Privileged {
    meta:
        description = "Detects privileged Docker container"
        severity = "critical"
        mitre = "T1611"
    strings:
        $privileged = "privileged:" nocase
        $true = "true" nocase
    condition:
        $privileged and $true
}

rule YAML_GitHub_Action_Unsafe {
    meta:
        description = "Detects unsafe GitHub Actions"
        severity = "high"
        mitre = "T1059.004"
    strings:
        $run = "run:" nocase
        $curl = "curl" nocase
        $bash = "bash" nocase
        $checkout = "actions/checkout" nocase
        $pull_request = "pull_request" nocase
    condition:
        $run and $curl and $bash and $checkout and $pull_request
}
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
