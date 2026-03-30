// Resource Exhaustion Detection Rules - Week 3
// Created: 2026-03-30T22:24:11.730789

rule ResourceExhaustion_Concurrent_Flood {
    meta:
        description = "Detects concurrent connection flood attacks"
        severity = "high"
        week = 3
        day = 4
    
    strings:
        $async = /async\s+def|asyncio|await/
        $loop = /for\s+.*\s+in\s+range\s*\(\s*\d{4,}\s*\)/
        $connection = /session\.get|client\.get|connect\s*\(/
    
    condition:
        $async and $loop and $connection
}