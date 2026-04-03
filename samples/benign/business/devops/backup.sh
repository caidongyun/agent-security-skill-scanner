# Business: DevOps
# Collected: 2026-04-02 11:36:08.249663

#!/bin/bash
# 备份脚本
mysqldump -u root mydb > backup.sql
tar -czf backup.tar.gz backup.sql
echo "备份完成"
