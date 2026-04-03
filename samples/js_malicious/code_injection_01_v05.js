// Code Injection - Function Variant 5
const code = "// log
console.log('Injected')";
const fn = new Function(code);
fn();
