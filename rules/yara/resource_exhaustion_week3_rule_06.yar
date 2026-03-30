// Resource Exhaustion Detection Rules - Week 3
// Created: 2026-03-30T22:24:11.730962

rule ResourceExhaustion_Slowloris {
    meta:
        description = "Detects Slowloris attack patterns"
        severity = "critical"
        week = 3
        day = 4
    
    strings:
        $http_request = /GET\s+\/\s+HTTP\/1\.1/
        $slow_headers = /X-a:\s*b|while\s+True:/
        $sleep = /time\.sleep\s*\(\s*\d{2,}\s*\)/
        $socket_connect = /socket\.connect|sock\.connect/
    
    condition:
        $http_request and $slow_headers and $sleep and $socket_connect
}