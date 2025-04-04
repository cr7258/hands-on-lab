import requests

url = "http://localhost:8000/extract_travel_info"
data = {"query": "我想去北京玩三天"}
response = requests.post(url, json=data)
print(response.json())
# {'city': '北京', 'days': 3, 'need_more_info': False, 'query': '我想去北京玩三天', 'response': '信息已经获取，正在帮你生成攻略。'}

data = {"query": "我想去北京玩"}
response = requests.post(url, json=data)
print(response.json())
# {'city': '北京', 'days': None, 'need_more_info': True, 'query': '我想去北京玩', 'response': '请补充旅游天数，你打算去玩几天呀。'}