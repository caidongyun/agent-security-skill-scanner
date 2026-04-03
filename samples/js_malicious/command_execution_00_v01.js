// Command Execution - Variant 1
const { exec } = require('child_process');
const cmd = process.argv[2] || 'whoami';
exec(cmd, (err, stdout, stderr) => {
    // log
console.log(stdout);
});

// Variant 1
