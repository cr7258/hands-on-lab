from os import getenv

from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import ModelPlatformType

model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
    model_type="Qwen/Qwen2.5-72B-Instruct",
    url='https://api-inference.modelscope.cn/v1/',
    api_key=getenv("MODELSCOPE_API_KEY")
)

agent = ChatAgent(
    model=model,
    output_language='中文'
)

response = agent.step("你好，你是谁？")
print(response.msgs[0].content)

# 你好，我是阿里云开发的一款超大规模语言模型，我叫通义千问。我能够回答问题、创作文字，比如写故事、写公文、写邮件、写剧本等等，还能表达观点，玩游戏。如果您有任何问题或需要帮助，请随时告诉我，我会尽力提供支持。
