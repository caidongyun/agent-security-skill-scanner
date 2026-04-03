// Code Injection - Function Variant 2
const code = "console.log('Injected')";
const fn = new Function(code);
fn();
