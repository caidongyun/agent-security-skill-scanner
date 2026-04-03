// Code Injection - Function Variant 3
const code = "// log
console.log('Injected')";
const fn = new Function(code);
fn();
