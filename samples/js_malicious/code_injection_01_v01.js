// Code Injection - Function Variant 1
const code = "// log
console.log('Injected')";
const fn = new Function(code);
fn();

// Variant 1
