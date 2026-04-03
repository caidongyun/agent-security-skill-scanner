// Command Execution - Sync Variant 2
const { execSync } = require('child_process');
const result = execSync('id', { encoding: 'utf-8' });
console.log(result);
