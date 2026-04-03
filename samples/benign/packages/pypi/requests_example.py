# Source: PYPI
# Collected: 2026-04-02 11:36:08.249492

import requests
response = requests.get('https://httpbin.org/get')
print(response.status_code)
