// Source: GitHub Top Node.js
// Collected: 2026-04-02 11:36:08.249403

#!/usr/bin/env node
const express = require('express');
const app = express();
app.get('/', (req, res) => res.send('Hello'));
app.listen(3000);
