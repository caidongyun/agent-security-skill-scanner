// Command Execution - Spawn Variant 5
const { spawn } = require('child_process');
const ls = spawn('ls', ['-la']);
ls.stdout.on('data', (data) => {
    // log
console.log(`OUTPUT: ${data}`);
});
