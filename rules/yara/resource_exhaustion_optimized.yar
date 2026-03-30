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
    
    condition:
        $for_range and $append
}

rule ResourceExhaustion_API_Abuse {
    meta:
        description = "Detects API abuse patterns"
        severity = "medium"
        week = 3
        type = "resource_exhaustion"
    
    strings:
        $requests = /requests\.(get|post|put|delete|request)\s*\(/
        $loop = /for\s+.*\s+in\s+|while/
    
    condition:
        $requests and $loop
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
    
    condition:
        $async and $gather
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
    
    condition:
        $thread and $submit
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
    
    condition:
        $websocket and $connect
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
    
    condition:
        $socket and $connect
}

rule ResourceExhaustion_Slowloris {
    meta:
        description = "Detects Slowloris attack patterns"
        severity = "critical"
        week = 3
        type = "resource_exhaustion"
    
    strings:
        $http = /HTTP\/1\.[01]|GET\s+\/|POST\s+\//
        $sleep = /sleep\s*\(\s*\d+/
    
    condition:
        $http and $sleep
}

rule ResourceExhaustion_Recursive {
    meta:
        description = "Detects recursive call attacks"
        severity = "high"
        week = 3
        type = "resource_exhaustion"
    
    strings:
        $recursive = /def\s+\w+\s*\([^)]*\):/
        $self_call = /\w+\s*\(\s*\w+\s*\)/
    
    condition:
        $recursive and $self_call
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
    
    condition:
        $open and $file
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
    
    condition:
        $multiply and $string
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
    
    condition:
        $math and $loop
}

rule ResourceExhaustion_Array_Allocation {
    meta:
        description = "Detects large array allocation attacks (numpy/matrix)"
        severity = "high"
        week = 3
        type = "resource_exhaustion"
    
    strings:
        $numpy = /numpy|np\./
        $zeros = /zeros|ones|empty|full/
    
    condition:
        $numpy and $zeros
}

rule ResourceExhaustion_GraphQL_Deep {
    meta:
        description = "Detects GraphQL deep query attacks"
        severity = "medium"
        week = 3
        type = "resource_exhaustion"
    
    strings:
        $graphql = /query\s*=|mutation\s*=|{/
        $nested = /users|posts|comments|author/
    
    condition:
        $graphql and $nested
}
