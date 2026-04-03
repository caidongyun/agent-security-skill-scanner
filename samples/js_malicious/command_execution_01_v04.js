// Command Execution - Sync Variant 4
const { execSync } = require('child_process');
const result = execSync('id', { encoding: 'utf-8' });
console.log(result);

// Variant 4
