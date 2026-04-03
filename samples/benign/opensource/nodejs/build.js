// Source: GitHub Top Node.js
// Collected: 2026-04-02 11:36:08.249442

#!/usr/bin/env node
const { exec } = require('child_process');
exec('npm run build', (err, stdout) => {
    console.log('Build complete');
});
