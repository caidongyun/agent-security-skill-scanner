// Command Execution - Sync Variant 3
const { execSync } = require('child_process');
const result = execSync('id', { encoding: 'utf-8' });
// log
console.log(result);
