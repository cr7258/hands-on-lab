import requests
import json

# API端点
url = "http://localhost:5002/get_travel_plan"

# 请求数据
data = {
    "city": "上海",
    "days": 3
}

# 发送POST请求
try:
    response = requests.post(url, json=data)
    
    # 检查响应状态
    if response.status_code == 200:
        result = response.json()
        print("获取到的旅游计划：")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"请求失败: {response.status_code}")
        print(f"错误信息: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"发送请求时发生错误: {e}")