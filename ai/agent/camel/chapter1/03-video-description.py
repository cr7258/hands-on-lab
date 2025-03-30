from os import getenv

from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import ModelPlatformType
from camel.messages import BaseMessage

model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
    model_type="Qwen/QVQ-72B-Preview",
    url='https://api-inference.modelscope.cn/v1/',
    api_key=getenv("MODELSCOPE_API_KEY")
)

# 创建代理
agent = ChatAgent(
    model=model,
    output_language='中文'
)

# 读取本地视频文件
video_path = "03-video.mp4"
with open(video_path, "rb") as video_file:
    video_bytes = video_file.read()

# 创建包含视频的用户消息
user_msg = BaseMessage.make_user_message(
    role_name="User", 
    content="请描述这段视频的内容", 
    video_bytes=video_bytes  # 将视频字节作为参数传入
)

# 获取模型响应
response = agent.step(user_msg)
print(response.msgs[0].content)

# 这是一条神奇的天路啊~

# 我走在一条被雪覆盖的道路上，脚下的雪发出咯吱咯吱的声音。这条路好像没有尽头，一直延伸向远方，两侧是连绵的雪山，山顶上积着厚厚的雪，与天空融为一体。

# 天空是那么的美丽，让我几乎移不开眼睛。它呈现出一种梦幻般的色彩，有粉色、紫色、蓝色和金色交织在一起，像是艺术家的调色板被打翻在了天上。云层厚重而富有质感，仿佛是一片片棉花糖，让人想要伸手触摸。阳光穿过云层，形成一道道光柱，照在雪地上，使得整个场景更加辉煌灿烂。

# 突然，一只小狗从我身边跑过，它毛茸茸的，看起来非常可爱。它在雪地上留下了一串串小脚印，然后欢快地向远方跑去。我忍不住跟着它，想要看看它要去哪里。

# 路上，我遇到了一些其他的旅行者，他们也都被这美景所吸引，纷纷拿出相机和手机，记录下这令人窒息的瞬间。我们虽然互不相识，但都分享着对自然之美的敬畏和感动。

# 随着我继续前行，天空的色彩变得更加绚丽，仿佛整个宇宙的色彩都集中在这里。我感到一种莫名的宁静和平和，仿佛所有的烦恼和忧虑都被这美景所洗涤，只剩下内心的宁静和对生命的感恩。

# 终于，我来到了道路的尽头，那里有一座雄伟的雪山，山顶上有一道彩虹横跨天空，色彩斑斓，美不胜收。我站在那里，仰望着这壮丽的景象，心中充满了敬畏和感慨。

# 这真是一条神奇的天路啊，它不仅带领我穿越了美丽的雪域，更让我体验到了心灵的升华和自然的伟大力量。我希望能够再次踏上这条道路，继续探索这无尽的美丽。

# **总结**

# - **环境**：雪域道路，被雪覆盖，两侧雪山，天空梦幻色彩（粉色、紫色、蓝色、金色）

# - **天气**：云层厚重，阳光穿过云层形成光柱

# - **生物**：小狗，毛茸茸，可爱，留下小脚印

# - **人物活动**：行走，观赏美景，拍照

# - **感受**：宁静、平和、敬畏、感恩

# - **结尾**：到达道路尽头，雄伟雪山，彩虹横跨，心灵升华