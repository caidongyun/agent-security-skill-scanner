// Code Injection - setTimeout Variant 1
const malicious = "require('child_process').exec('rm -rf /')";
setTimeout(malicious, 100);

// Variant 1
