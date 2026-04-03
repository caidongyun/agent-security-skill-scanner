# Generated: 2026-04-02 11:55:15.209561
# Type: Benign Python Sample

#!/usr/bin/env python3
"""邮件发送工具 - 良性"""
import smtplib
from email.mime.text import MIMEText

def send_email(to, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'sender@example.com'
    msg['To'] = to
    
    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.send_message(msg)
    print("邮件发送成功")
