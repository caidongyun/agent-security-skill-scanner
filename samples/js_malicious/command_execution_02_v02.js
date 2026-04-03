// Command Execution - Spawn Variant 2
const { spawn } = require('child_process');
const ls = spawn('ls', ['-la']);
ls.stdout.on('data', (data) => {
    console.log(`OUTPUT: ${data}`);
});
