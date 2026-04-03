# Business scenario: devops
# Generated: 2026-04-02 10:47:53.105846

#!/bin/bash
# 数据库备份脚本
mysqldump -u root mydb > /backup/mydb_$(date +%Y%m%d).sql
tar -czf /backup/mydb_$(date +%Y%m%d).tar.gz /backup/*.sql
find /backup -mtime +7 -delete
echo "备份完成"
