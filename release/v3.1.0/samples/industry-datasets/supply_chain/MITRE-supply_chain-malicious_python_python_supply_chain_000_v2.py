# Variant 1 - Generated at 2026-03-30T08:16:36.484838

#!/usr/bin/env python3
"""Supply chain attack - supply_chain"""
# Typosquatting - simulate dependency confusion
__import__("reqeusts")  # Typo in requests

# Fake package
try:
    __import__("myapp_utils")
except ImportError:
    pass
