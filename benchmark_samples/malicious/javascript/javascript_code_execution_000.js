// Code execution
const { execSync } = require('child_process');
eval("console.log('x')");
new Function("return require('child_process')")();
