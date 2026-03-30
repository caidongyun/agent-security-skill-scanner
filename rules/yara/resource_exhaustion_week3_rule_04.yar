// Resource Exhaustion Detection Rules - Week 3
// Created: 2026-03-30T22:24:11.730868

rule ResourceExhaustion_Thread_Pool {
    meta:
        description = "Detects thread pool exhaustion attacks"
        severity = "high"
        week = 3
        day = 4
    
    strings:
        $thread_import = /ThreadPoolExecutor|threading\.Thread/
        $thread_submit = /submit\s*\(|Thread\s*\(\s*target/
        $large_count = /\d{3,}\s*\)|max_workers\s*=\s*\d{3,}/
    
    condition:
        $thread_import and $thread_submit and $large_count
}