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
        $hostNetwork and $true
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
