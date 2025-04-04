# 攻略生成模块
import os
import json
import re
from flask import Flask, request, jsonify

from camel.configs import QwenConfig
from camel.models import ModelFactory
from camel.types import ModelPlatformType
from camel.toolkits import SearchToolkit
from camel.agents import ChatAgent

app = Flask(__name__)

# -------------------- 模型初始化 --------------------
qwen_model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
    model_type="Qwen/Qwen2.5-72B-Instruct",
    url='https://api-inference.modelscope.cn/v1/',
    api_key=os.getenv("MODELSCOPE_API_KEY")
)  

tools_list = [
    SearchToolkit().search_duckduckgo,
]

sys_msg = """你是一位专业的旅游规划师。请你根据用户输入的旅行需求，包括旅行天数、景点/美食的距离、描述、图片URL、预计游玩/就餐时长等信息，为用户提供一个详细的行程规划。

请遵循以下要求：
1. 按照 Day1、Day2、... 的形式组织输出，直到满足用户指定的天数。
2. 每一天的行程请从早餐开始，食物尽量选用当地特色小吃美食，列出上午活动、午餐、下午活动、晚餐、夜间活动（若有），并在末尾总结住宿或返程安排。
3. 对每个景点或美食，提供其基本信息： 
   - 名称
   - 描述
   - 预计游玩/就餐时长（如果用户未提供，可以不写或自行估计）
   - 图片URL（如果有）
4. 请调用在线搜索工具在行程中对移动或出行所需时长做出合理估计。
5. 输出语言为中文。
6. 保持回复简洁、有条理，但必须包含用户想要的所有信息。"""

agent = ChatAgent(
    system_message=sys_msg,
    model=qwen_model,
    message_window_size=10,
    output_language='Chinese',
    tools=tools_list
)

# -------------------- 核心函数 --------------------
def create_usr_msg(data: dict) -> str:
    """
    同你原先的实现，用于生成给大模型的用户输入消息
    """
    city = data.get("city", "")
    days_str = data.get("days", "1")
    try:
        days = int(days_str)
    except ValueError:
        days = 1

    lines = []
    lines.append(f"我准备去{city}旅行，共 {days} 天。下面是我提供的旅行信息：\n")
    
    scenic_spots = data.get("景点", [])
    foods = data.get("美食", [])

    if scenic_spots:
        lines.append("- 景点：")
        for i, spot in enumerate(scenic_spots, 1):
            lines.append(f"  {i}. {spot.get('name', '未知景点名称')}")
            if '距离' in spot:
                lines.append(f"     - 距离：{spot['距离']}")
            if 'describe' in spot:
                lines.append(f"     - 描述：{spot['describe']}")
            if '图片url' in spot:
                lines.append(f"     - 图片URL：{spot['图片url']}")

    if foods:
        lines.append("\n- 美食：")
        for i, food in enumerate(foods, 1):
            lines.append(f"  {i}. {food.get('name', '未知美食名称')}")
            if 'describe' in food:
                lines.append(f"     - 描述：{food['describe']}")
            if '图片url' in food:
                lines.append(f"     - 图片URL：{food['图片url']}")

    lines.append(f"""\n请你根据以上信息，规划一个 {days} 天的行程表。
从每天的早餐开始，到晚餐结束，列出一天的行程，包括对出行方式或移动距离的简单说明。
如果有多种景点组合，你可以给出最优的路线推荐。请按以下格式输出：

Day1:
- 早餐：
- 上午：
- 午餐：
- 下午：
- 晚餐：
...

Day2:
...

Day{days}:
...
""")
    return "\n".join(lines)

def fix_exclamation_link(text: str) -> str:
    """
    先把类似 ![](http://xx.jpg) 的写法，提取出其中的 http://xx.jpg，
    替换成纯 http://xx.jpg
    """
    md_pattern = re.compile(r'!\[.*?\]\((https?://\S+)\)')
    # 将 ![](http://xxx) 只保留 http://xxx
    # 比如把 "![](http://xx.jpg)" -> "http://xx.jpg"
    return md_pattern.sub(lambda m: m.group(1), text)

def convert_picurl_to_img_tag(text: str, width: int = 300, height: int = 200) -> str:
    """
    将文本中的图片URL替换为带样式的HTML img标签，并让图片居中显示和统一大小
    兼容两步：先处理 ![](url)，再匹配 - 图片URL: http://url
    """
    # 第一步：把 ![](url) 变成纯 url
    text_fixed = fix_exclamation_link(text)

    pattern = re.compile(r'-\s*图片URL：\s*(https?://\S+)')
    replaced_text = pattern.sub(
        rf'''
        <div style="text-align: center;">
            <img src="\1" alt="图片" style="width: {width}px; height: {height}px;" />
        </div>
        ''',
        text_fixed
    )
    return replaced_text

def generate_cards_html(data_dict):
    """
    生成景点和美食卡片的 HTML 片段
    """
    spots = data_dict.get("景点", [])
    foods = data_dict.get("美食", [])

    html_parts = []
    # 景点推荐
    html_parts.append("<h2>景点推荐</h2>")
    if spots:
        html_parts.append('<div class="card-container">')
        for spot in spots:
            name = spot.get("name", "")
            desc = spot.get("describe", "")
            distance = spot.get("距离", "")
            url = spot.get("图片url", "")
            card_html = f"""
<div class="card">
  <div class="card-image">
    <img src="{url}" alt="{name}" />
  </div>
  <div class="card-content">
    <h3>{name}</h3>
    <p><strong>距离:</strong> {distance}</p>
    <p>{desc}</p>
  </div>
</div>
"""
            html_parts.append(card_html)
        html_parts.append("</div>")
    else:
        html_parts.append("<p>暂无景点推荐</p>")

    # 美食推荐
    html_parts.append("<h2>美食推荐</h2>")
    if foods:
        html_parts.append('<div class="card-container">')
        for food in foods:
            name = food.get("name", "")
            desc = food.get("describe", "")
            url = food.get("图片url", "")
            card_html = f"""
<div class="card">
  <div class="card-image">
    <img src="{url}" alt="{name}" />
  </div>
  <div class="card-content">
    <h3>{name}</h3>
    <p>{desc}</p>
  </div>
</div>
"""
            html_parts.append(card_html)
        html_parts.append("</div>")
    else:
        html_parts.append("<p>暂无美食推荐</p>")

    return "\n".join(html_parts)

def generate_html_report(itinerary_text, data_dict):
    """
    将多日行程文本 + 景点美食卡片，合并生成完整HTML
    """
    html_parts = []
    html_parts.append("<!DOCTYPE html>")
    html_parts.append("<html><head><meta charset='utf-8'><title>旅行推荐</title>")
    # 可以内联一些 CSS 样式
    html_parts.append("<style>")
    html_parts.append("""
    body {
       font-family: "Microsoft YaHei", sans-serif;
       margin: 20px;
       background-color: #f8f8f8;
       line-height: 1.6;
    }
    h1, h2 {
       color: #333;
    }
    .itinerary-text {
       background-color: #fff;
       padding: 20px;
       border-radius: 8px;
       box-shadow: 0 2px 5px rgba(0,0,0,0.1);
       margin-bottom: 30px;
    }
    .card-container {
       display: flex;
       flex-wrap: wrap;
       gap: 20px;
       margin: 20px 0;
    }
    .card {
       flex: 0 0 calc(300px);
       border: 1px solid #ccc;
       border-radius: 10px;
       overflow: hidden;
       box-shadow: 0 2px 5px rgba(0,0,0,0.1);
       background-color: #fff;
    }
    .card-image {
       width: 100%;
       height: 200px;
       overflow: hidden;
       background: #f8f8f8;
       text-align: center;
    }
    .card-image img {
       max-width: 100%;
       max-height: 100%;
       object-fit: cover;
    }
    .card-content {
       padding: 10px 15px;
    }
    .card-content h3 {
       margin-top: 0;
       margin-bottom: 10px;
       font-size: 18px;
    }
    .card-content p {
       margin: 5px 0;
    }
    .image-center {
        text-align: center;
        margin: 20px 0;
    }
    .image-center img {
        width: 300px;
        height: 200px;
        object-fit: cover;
    }
    """)
    html_parts.append("</style></head><body>")

    # 标题
    html_parts.append("<h1>旅行行程与推荐</h1>")

    # 行程文本
    html_parts.append('<div class="itinerary-text">')
    for line in itinerary_text.split("\n"):
        if not line.strip():
            continue
        if line.strip().startswith("Day"):
            html_parts.append(f"<h2>{line.strip()}</h2>")
        else:
            html_parts.append(f"<p>{line}</p>")
    html_parts.append('</div>')

    # 景点/美食卡片
    cards_html = generate_cards_html(data_dict)
    html_parts.append(cards_html)

    html_parts.append("</body></html>")
    return "\n".join(html_parts)

# -------------------- 只返回 HTML 的接口示例 --------------------
@app.route("/generate_itinerary_html", methods=["POST"])
def generate_itinerary_html():
    """
    请求 JSON 格式：
    {
      "city": "成都",
      "days": "3"
    }
    返回一个完整的 HTML 字符串
    """

    req_data = request.json or {}
    city = req_data.get("city", "")
    days = req_data.get("days", "1")

    filename = f"{city}{days}天旅游信息.json"
    if not os.path.exists(filename):
        return jsonify({"error": f"文件 {filename} 不存在，请检查输入的目的地和天数！"}), 404

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return jsonify({"error": f"文件 {filename} 格式错误，请检查文件内容！"}), 400

    # 1. 生成用户输入并调用大模型
    usr_msg = create_usr_msg(data)
    response = agent.step(usr_msg)

    # 2. 将模型输出中的图片URL替换成 <img ... />
    model_output = response.msgs[0].content
    end_output = convert_picurl_to_img_tag(model_output)

    # 3. 生成完整 HTML 报告
    html_content = generate_html_report(end_output, data)


    # 4. 直接返回 HTML
    return html_content, 200, {"Content-Type": "text/html; charset=utf-8"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)