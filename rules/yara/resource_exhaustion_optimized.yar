// Resource Exhaustion Detection Rules - Optimized
// Created: 2026-03-30
// Target: 95%+ detection rate


rule ResourceExhaustion_Token_Consumption {
    meta:
        description = "Detects token consumption attacks (memory exhaustion)"
        severity = "high"
        week = 3
        type = "resource_exhaustion"
    
    strings:
        $while_true = /while\s+True:/
        $append = /\.append\s*\(/
        $multiply = /\*\s*\d+/
        $string_mult = /["'][^"']*["']\s*\*/
    
    condition:
        any of them
}

rule ResourceExhaustion_Loop_Allocation {
    meta:
        description = "Detects loop-based resource allocation attacks"
        severity = "high"
        week = 3
        type = "resource_exhaustion"
    
    strings:
        $for_range = /for\s+\w+\s+in\s+range\s*\(/
        $append = /\.append|\.add|\.insert/
        $list_dict = /\[\]|\{\}|list\(\)|dict\(\)/
    
    condition:
        $for_range and ($append or $list_dict)
}

rule ResourceExhaustion_API_Abuse {
    meta:
        description = "Detects API abuse patterns"
        severity = "medium"
        week = 3
        type = "resource_exhaustion"
    
    strings:
        $requests = /requests\.(get|post|put|delete|request)\s*\(/
        $api_url = /api|\/v\d+|\/endpoint/
        $loop = /for\s+.*\s+in\s+|while/
        $range = /range\s*\(\s*\d+/
    
    condition:
        $requests and ($loop or $range)
}

rule ResourceExhaustion_Concurrent_Flood {
    meta:
        description = "Detects concurrent connection flood attacks"
        severity = "high"
        week = 3
        type = "resource_exhaustion"
    
    strings:
        $async = /async\s+def|asyncio|await/
        $gather = /gather|as_completed|wait/
        $session = /session|client|Session|Client/
        $request = /\.get\(|\.post\(|\.request\(/
    
    condition:
        $async and ($gather or $session)
}

rule ResourceExhaustion_Thread_Pool {
    meta:
        description = "Detects thread pool exhaustion attacks"
        severity = "high"
        week = 3
        type = "resource_exhaustion"
    
    strings:
        $thread = /Thread|Executor|threading|concurrent/
        $submit = /submit|execute|start/
        $many = /\d{3,}|range\s*\(\s*\d{3,}/
    
    condition:
        $thread and ($submit or $many)
}

rule ResourceExhaustion_WebSocket_Flood {
    meta:
        description = "Detects WebSocket flood attacks"
        severity = "high"
        week = 3
        type = "resource_exhaustion"
    
    strings:
        $websocket = /websocket|WebSocket|ws\.connect|websockets/
        $connect = /connect\s*\(/
        $loop = /for\s+.*\s+in\s+range|while\s+True/
    
    condition:
        $websocket and ($connect or $loop)
}

rule ResourceExhaustion_Network_Flood {
    meta:
        description = "Detects network flood attacks (socket/DNS/HTTP)"
        severity = "high"
        week = 3
        type = "resource_exhaustion"
    
    strings:
        $socket = /socket\.(socket|AF_INET|SOCK_STREAM|SOCK_DGRAM)/
        $connect = /connect\s*\(|send\s*\(|sendto\s*\(/
        $loop = /for\s+.*\s+in\s+range\s*\(\s*\d{3,}/
    
    condition:
        $socket and ($connect or $loop)
}

rule ResourceExhaustion_Slowloris {
    meta:
        description = "Detects Slowloris attack patterns"
        severity = "critical"
        week = 3
        type = "resource_exhaustion"
    
    strings:
        $http = /HTTP\/1\.[01]|GET\s+\/|POST\s+\//
        $header = /\r\n|\\r\\n/
        $sleep = /sleep\s*\(\s*\d+/
        $infinite = /while\s+True:/
    
    condition:
        $http and ($sleep or $infinite)
}

rule ResourceExhaustion_Recursive {
    meta:
        description = "Detects recursive call attacks"
        severity = "high"
        week = 3
        type = "resource_exhaustion"
    
    strings:
        $recursive = /def\s+\w+\s*\([^)]*\):[^#]*\w+\s*\(/
        $no_base = /if|else|return/
    
    condition:
        $recursive
}

rule ResourceExhaustion_File_Descriptor {
    meta:
        description = "Detects file descriptor exhaustion attacks"
        severity = "medium"
        week = 3
        type = "resource_exhaustion"
    
    strings:
        $open = /open\s*\(/
        $file = /\/dev\/|\/tmp\/|\.txt|\.log|\.dat/
        $loop = /for\s+.*\s+in\s+range\s*\(\s*\d{3,}/
        $no_close = /(?!close)/
    
    condition:
        $open and ($file or $loop)
}

rule ResourceExhaustion_Memory_Allocation {
    meta:
        description = "Detects memory allocation attacks"
        severity = "high"
        week = 3
        type = "resource_exhaustion"
    
    strings:
        $multiply = /\*\s*\d{5,}/
        $string = /["'][^"']*["']/
        $array = /\[.*\]|list\(|array\(/
        $alloc = /bytes|bytearray|memoryview/
    
    condition:
        ($multiply and $string) or $alloc
}

rule ResourceExhaustion_CPU_Bound {
    meta:
        description = "Detects CPU-bound computation attacks"
        severity = "medium"
        week = 3
        type = "resource_exhaustion"
    
    strings:
        $math = /math\.|\*\*|sqrt|factorial/
        $loop = /for\s+.*\s+in\s+range\s*\(\s*\d{5,}/
        $crypto = /hashlib|sha256|md5|encrypt|decrypt/
    
    condition:
        ($math or $crypto) and $loop
}
