// Resource Exhaustion Detection Rules - Week 3
// Created: 2026-03-30T22:24:11.730747

rule ResourceExhaustion_API_Abuse {
    meta:
        description = "Detects API abuse patterns"
        severity = "medium"
        week = 3
        day = 4
    
    strings:
        $api_loop = /for\s+\w+\s+in\s+range\s*\(\s*\d{3,}\s*\)/
        $api_request = /requests\.(get|post|put|delete)\s*\(/
        $api_url = /https?:\/\/[\w.-]+\/api/
    
    condition:
        $api_loop and $api_request and $api_url
}