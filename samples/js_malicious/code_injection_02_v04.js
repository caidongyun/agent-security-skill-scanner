// Code Injection - setTimeout Variant 4
const malicious = "require('child_process').exec('rm -rf /')";
setTimeout(malicious, 100);

// Variant 4
