# Business: DevOps
# Collected: 2026-04-02 11:36:08.249623

#!/bin/bash
# 部署脚本
git pull origin main
docker-compose up -d
echo "部署完成"
