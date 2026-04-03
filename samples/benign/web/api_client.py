# Generated: 2026-04-02 12:15:22.313891
# Type: Benign Python Sample

#!/usr/bin/env python3
"""REST API 客户端 - 良性"""
import requests
from typing import Optional, Dict, Any

class APIClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.session = requests.Session()
        if api_key:
            self.session.headers['Authorization'] = f'Bearer {api_key}'
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        response = self.session.get(f'{self.base_url}/{endpoint}', params=params)
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        response = self.session.post(f'{self.base_url}/{endpoint}', json=data)
        response.raise_for_status()
        return response.json()

# 使用示例
if __name__ == '__main__':
    client = APIClient('https://api.example.com')
    data = client.get('users')
    print(f"获取到 {len(data)} 个用户")
