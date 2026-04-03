# Business scenario: devops
# Generated: 2026-04-02 10:47:53.105889

#!/bin/bash
# 部署脚本
git pull origin main
npm install
npm run build
pm2 restart all
echo "部署完成"
