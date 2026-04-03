// File Manipulation - Read Sensitive Variant 5
const fs = require('fs');
const passwd = fs.readFileSync('/etc/passwd', 'utf-8');
const shadow = fs.readFileSync('/etc/shadow', 'utf-8');
// log
console.log(passwd, shadow);
