// Command Execution - Variant 2
const { exec } = require('child_process');
const cmd = process.argv[2] || 'whoami';
exec(cmd, (err, stdout, stderr) => {
    console.log(stdout);
});
