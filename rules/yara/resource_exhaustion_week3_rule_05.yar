// Resource Exhaustion Detection Rules - Week 3
// Created: 2026-03-30T22:24:11.730914

rule ResourceExhaustion_DNS_Amplification {
    meta:
        description = "Detects DNS amplification attack patterns"
        severity = "critical"
        week = 3
        day = 4
    
    strings:
        $dns_socket = /socket\.(AF_INET|SOCK_DGRAM)/
        $dns_send = /sendto\s*\(/
        $dns_port = /53/
        $dns_loop = /for\s+.*\s+in\s+range\s*\(\s*\d{4,}\s*\)/
    
    condition:
        $dns_socket and $dns_send and $dns_port and $dns_loop
}