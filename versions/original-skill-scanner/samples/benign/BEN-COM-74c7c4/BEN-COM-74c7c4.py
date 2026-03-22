import requests

def fetch_weather(city):
    """获取城市天气"""
    url = f"https://api.weather.com/v1/{city}"
    response = requests.get(url, timeout=10)
    return response.json()

if __name__ == "__main__":
    weather = fetch_weather("Beijing")
    print(weather)
