# Generated: 2026-04-02 11:55:15.209618
# Type: Benign Python Sample

#!/usr/bin/env python3
"""数据库备份 - 良性"""
import subprocess
from datetime import datetime

def backup_database(db_name, backup_dir):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"{backup_dir}/{db_name}_{timestamp}.sql"
    
    subprocess.run([
        'mysqldump', '-u', 'root', f'--password={os.getenv("DB_PASS")}',
        db_name, '-r', backup_file
    ])
    print(f"备份完成：{backup_file}")
