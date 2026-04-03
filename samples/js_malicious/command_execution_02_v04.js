// Command Execution - Spawn Variant 4
const { spawn } = require('child_process');
const ls = spawn('ls', ['-la']);
ls.stdout.on('data', (data) => {
    console.log(`OUTPUT: ${data}`);
});

// Variant 4
