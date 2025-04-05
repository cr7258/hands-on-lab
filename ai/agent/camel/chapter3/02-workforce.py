from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.messages import BaseMessage
from camel.societies.workforce import Workforce
from camel.toolkits import SearchToolkit
from camel.tasks import Task
from camel.toolkits import FunctionTool

from os import getenv

model = ModelFactory.create(
    model_platform=ModelPlatformType.QWEN,
    model_type=ModelType.QWEN_MAX,
    api_key=getenv("QWEN_API_KEY")
)

# 创建一个 Workforce 实例
workforce = Workforce(description="旅游攻略制作与评估工作组", new_worker_agent_kwargs={'model': model},
                      coordinator_agent_kwargs={'model': model}, task_agent_kwargs={'model': model})

search_tool = FunctionTool(SearchToolkit().search_duckduckgo)

search_agent = ChatAgent(
            system_message="""你是一个专业的旅游信息搜索助手。你的职责是:
                1. 搜索目的地的主要景点信息
                2. 搜索当地特色美食信息
                3. 搜索交通和住宿相关信息
                请确保信息的准确性和实用性。""",
            model=model,
            tools=[search_tool],
            output_language='中文'
        )

planner_agent = ChatAgent(
            system_message="""你是一个专业的旅行规划师。你的职责是:
                1. 根据景点分布规划合理的游览顺序
                2. 为每天安排适量的景点和活动
                3. 考虑用餐、休息等时间
                4. 注意不同季节的特点
                请确保行程安排合理且具有可行性。""",
            model=model,
            output_language='中文'
        )

reviewer_agent = ChatAgent(
    system_message="""你是一个经验丰富的旅行爱好者。你的职责是:
        1. 从游客角度评估行程的合理性
        2. 指出可能的问题和改进建议
        3. 补充实用的旅行小贴士
        4. 评估行程的性价比
        请基于实际旅行经验给出中肯的建议。""",
    model=model,
    output_language='中文'
)

# 添加工作节点
workforce.add_single_agent_worker(
    "负责搜索目的地相关信息",
    worker=search_agent
).add_single_agent_worker(
    "负责制定详细行程规划",
    worker=planner_agent
).add_single_agent_worker(
    "负责从游客角度评估行程",
    worker=reviewer_agent
)

# 创建一个用于测试的任务
task = Task(
    content="规划一个3天的巴黎旅行计划。",
    id="0",  # id可以是任何标记字符串
)

# 让 Workforce 处理这个任务
task = workforce.process_task(task)

print(task.result)

# Worker node 5604799632 (负责搜索目的地相关信息) get task 0.0: 搜索巴黎的主要旅游景点、餐厅和活动信息。
# ======
# Reply from Worker node 5604799632 (负责搜索目的地相关信息):

# 巴黎是一个充满浪漫和历史的城市，这里有一些主要的旅游景点、餐厅和活动信息：\r### 主要旅游景点 \\- **埃菲尔铁塔** - 作为巴黎乃至整个法国最著名的地标之一，每年吸引数百万游客。铁塔高324米，设有三层观景台，顶层可以俯瞰整个巴黎市。第一层和第二层设有餐厅，提供在高空享受美食的独特体验。 \\   - [详情请见](https://www.cometoparis.com/chi/paris-guide/what-to-do-in-paris-s938) \\- **卢浮宫、凯旋门等** - 除了埃菲尔铁塔外，卢浮宫、凯旋门也是不可错过的经典景点。此外，还有一些相对较少人知但同样迷人的地方，如海军府、证券博物馆及莎士比亚书店等。 \\   - [更多信息](https://markandhazyl.com/must-visit-places-in-paris/) \\### 特色餐厅 \\- 在埃菲尔铁塔的第一层和第二层分别有餐厅供游客选择，在那里您可以享受到独特的用餐经历，一边品尝法国美食一边欣赏美丽的城市风光。 \\- 另外，巴黎市区内还有众多其他高品质的法式餐馆等待着您的探索。 \\### 活动 \\- 游览与观光：参加各种形式的城市游览团，包括步行游、巴士游甚至是夜间的塞纳河游船之旅。 \\- 文化体验：参观艺术展览、音乐会或戏剧表演；参与烹饪课程学习如何制作正宗的法国菜肴。 \\- 休闲娱乐：前往蒙马特高地感受艺术家聚集地的魅力；或者在香榭丽舍大道上享受购物的乐趣。 \\这些只是巴黎众多精彩活动中的一小部分。希望这些建议能够帮助您规划一次难忘的巴黎之旅！更多关于巴黎旅游的信息，您可以参考： \\   - [Tripadvisor上的巴黎景点排名](https://cn.tripadvisor.com/Attractions-g187147-Activities-c47-t163-Paris_Ile_de_France.html) \\   - [Dealmoon提供的巴黎旅行攻略](https://www.dealmoon.co.uk/guide/3988)
# ======Worker node 5604797616 (负责制定详细行程规划) get task 0.1: 根据收集到的信息，制定一个详细的3天巴黎旅行计划，包括每天的行程安排。
# ======
# Reply from Worker node 5604797616 (负责制定详细行程规划):

# ### 第一天：探索巴黎的经典地标\n- **上午**：首先前往埃菲尔铁塔。建议尽早出发以避开人群。可以选择先登上第二层观景台，享受早餐或早午餐（如果预算允许的话）。之后再前往顶层，俯瞰整个巴黎的壮丽景色。\n- **中午**：从埃菲尔铁塔下来后，在周边寻找一家当地餐厅享用午餐。\n- **下午**：参观凯旋门，并沿着香榭丽舍大道漫步至协和广场。\n- **晚上**：参加塞纳河游船晚宴之旅，体验浪漫的夜巴黎。\n\n### 第二天：文化与艺术之旅\n- **上午**：参观卢浮宫博物馆。由于卢浮宫非常大且藏品众多，请提前计划好想要重点参观的部分。\n- **中午**：在卢浮宫附近找家特色餐馆享用午餐。\n- **下午**：前往奥赛博物馆继续您的艺术之旅。\n- **晚上**：观看一场音乐会或戏剧表演，感受巴黎的文化氛围。\n\n### 第三天：发现巴黎的另一面\n- **上午**：游览蒙马特高地，参观圣心大教堂并探索周围的艺术街区。\n- **中午**：在当地的小酒馆里尝试地道的法国菜肴。\n- **下午**：逛逛莎士比亚书店及周边区域，这里不仅是购书的好地方，也是了解巴黎文学历史的一个窗口。\n- **晚上**：结束旅行前，在香榭丽舍大道上享受一次购物体验。
# ======Worker node 5604798000 (负责从游客角度评估行程) get task 0.2: 从游客的角度评估这个3天巴黎旅行计划，并提出改进建议以确保旅行体验最佳。
# ======
# Reply from Worker node 5604798000 (负责从游客角度评估行程):

# 这个3天的巴黎旅行计划已经覆盖了主要的旅游景点和活动，对于初次访问巴黎的人来说是一个很好的起点。但是从游客的角度来看，这里有一些可能的问题和改进建议："path: \n1. **行程紧凑**：每天的行程安排得比较满，尤其是第一天参观埃菲尔铁塔后紧接着去凯旋门和香榭丽舍大道，这可能会让人感到疲劳。建议适当调整节奏，为每个地点预留更多时间来享受。\
# ======根据已有的信息，这里提供一个更加详细且合理的3天巴黎旅行计划。此计划考虑到了行程紧凑的问题，并为每个地点预留了更多的时间让游客能够更好地享受旅程。

# ### 第一天：探索巴黎的经典地标
# - **上午**：首先前往埃菲尔铁塔。建议尽早出发以避开人群。可以选择先登上第二层观景台，享受早餐或早午餐（如果预算允许的话）。之后再前往顶层，俯瞰整个巴黎的壮丽景色。
# - **中午**：从埃菲尔铁塔下来后，在周边寻找一家当地餐厅享用午餐。
# - **下午**：参观凯旋门，并沿着香榭丽舍大道漫步至协和广场。考虑到体力问题，这一天不安排其他活动，可以在香榭丽舍大道附近逛逛商店或者找一家咖啡馆休息一下。
# - **晚上**：参加塞纳河游船晚宴之旅，体验浪漫的夜巴黎。

# ### 第二天：文化与艺术之旅
# - **上午**：参观卢浮宫博物馆。由于卢浮宫非常大且藏品众多，请提前计划好想要重点参观的部分。考虑到游览时间较长，建议至少留出半天时间给卢浮宫。
# - **中午**：在卢浮宫附近找家特色餐馆享用午餐。
# - **下午**：前往奥赛博物馆继续您的艺术之旅。如果对艺术特别感兴趣，可以在此多花些时间；如果不打算深入参观，则可适当缩短停留时间。
# - **晚上**：观看一场音乐会或戏剧表演，感受巴黎的文化氛围。也可以选择轻松一点的方式度过夜晚，比如在蒙马特高地散步等。

# ### 第三天：发现巴黎的另一面
# - **上午**：游览蒙马特高地，参观圣心大教堂并探索周围的艺术街区。
# - **中午**：在当地的小酒馆里尝试地道的法国菜肴。
# - **下午**：逛逛莎士比亚书店及周边区域，这里不仅是购书的好地方，也是了解巴黎文学历史的一个窗口。之后还可以考虑参观一些小众但有趣的景点，如海军府、证券博物馆等。
# - **晚上**：结束旅行前，在香榭丽舍大道上享受一次购物体验。同时，这也是个不错的机会购买纪念品带回家。

# 通过上述调整后的计划，希望能帮助您在有限的时间里尽可能多地体验到巴黎的魅力。记得根据个人兴趣和实际情况灵活调整行程哦！