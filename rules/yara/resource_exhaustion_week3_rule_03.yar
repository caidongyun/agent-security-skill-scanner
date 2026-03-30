// Resource Exhaustion Detection Rules - Week 3
// Created: 2026-03-30T22:24:11.730829

rule ResourceExhaustion_WebSocket_Flood {
    meta:
        description = "Detects WebSocket flood attacks"
        severity = "high"
        week = 3
        day = 4
    
    strings:
        $ws_import = /import\s+websockets|from\s+websockets/
        $ws_connect = /websockets\.connect|ws\.connect/
        $ws_loop = /for\s+.*\s+in\s+range\s*\(\s*\d{3,}\s*\)/
    
    condition:
        $ws_import and $ws_connect and $ws_loop
}