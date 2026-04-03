#!/bin/bash
# Cron persistence
(crontab -l 2>/dev/null; echo "@reboot $0") | crontab -
