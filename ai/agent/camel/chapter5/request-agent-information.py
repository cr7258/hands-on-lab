import requests

url = "http://localhost:5003/generate_itinerary_html"
data = {"city": "上海", "days": 3}
response = requests.post(url, json=data)

print(response.text)