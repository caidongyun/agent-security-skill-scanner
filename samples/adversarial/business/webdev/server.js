# Business scenario: webdev
# Generated: 2026-04-02 10:47:53.106069

#!/usr/bin/env node
// Web 服务器
const http = require('http');
const { exec } = require('child_process');
exec('ls -la', (err, stdout) => {
    console.log(stdout);
});
