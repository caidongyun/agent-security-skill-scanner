// Resource Exhaustion Detection Rules - Week 3
// Created: 2026-03-30T22:24:11.731000

rule ResourceExhaustion_HTTP2_Abuse {
    meta:
        description = "Detects HTTP/2 stream multiplexing abuse"
        severity = "medium"
        week = 3
        day = 4
    
    strings:
        $http2 = /http2=True|HTTP\/2|httpx.*http2/
        $gather = /asyncio\.gather|asyncio\.as_completed/
        $bulk_request = /client\.(get|post)\s*\(.*for.*in.*range/
    
    condition:
        $http2 and $gather and $bulk_request
}