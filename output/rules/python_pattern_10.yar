rule Python_Malicious_Pattern_10 {
    meta:
        description = "Detects Python malicious pattern 10"
        author = "Sample Generator v2.0"
        severity = "medium"
    
    strings:
        $s1 = "import"
        $s2 = "def "
        $s3 = "if __name__"
    
    condition:
        all of them
}