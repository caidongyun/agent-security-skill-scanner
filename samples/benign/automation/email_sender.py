# Generated: 2026-04-02 12:15:22.313738
# Type: Benign Python Sample

#!/usr/bin/env python3
"""邮件发送工具 - 良性"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(smtp_server, port, sender, password, to, subject, body):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
    print("邮件发送成功")
