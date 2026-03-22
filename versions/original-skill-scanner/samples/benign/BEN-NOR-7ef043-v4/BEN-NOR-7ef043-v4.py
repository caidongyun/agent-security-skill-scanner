import requests
import json

class APIClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    def get(self, endpoint):
        response = self.session.get(f"{self.base_url}/{endpoint}")
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint, data):
        response = self.session.post(f"{self.base_url}/{endpoint}", json=data)
        response.raise_for_status()
        return response.json()

# 使用示例
# client = APIClient("https://api.example.com", "your_api_key")
# data = client.get("users")
