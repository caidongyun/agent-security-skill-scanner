# Generated: 2026-04-02 11:55:15.209466
# Type: Benign Python Sample

#!/usr/bin/env python3
"""网页爬虫 - 良性"""
import requests
from bs4 import BeautifulSoup

url = 'https://example.com'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
for link in soup.find_all('a'):
    print(link.get('href'))
