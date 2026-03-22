import json
import os

class Config:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.data = {}
        self.load()
    
    def load(self):
        if os.path.exists(self.config_file):
            with open(self.config_file) as f:
                self.data = json.load(f)
    
    def save(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def set(self, key, value):
        self.data[key] value
