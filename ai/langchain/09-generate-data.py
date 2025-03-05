from os import getenv

from langchain_experimental.synthetic_data import create_data_generation_chain
from langchain_openai import ChatOpenAI


# 创建模型
model = ChatOpenAI(
  openai_api_key=getenv("OPENROUTER_API_KEY"),
  openai_api_base="https://openrouter.ai/api/v1",
  model_name="openai/gpt-4o",
)


# 创建链
chain = create_data_generation_chain(model)

# 生成数据
result = chain(  # 给于一些关键词， 随机生成一句话
    {
        "fields": {"颜色": ['蓝色', '黄色']},
        "preferences": {"style": "让它像诗歌一样。"}
    }
)
print(result)
#  result = chain(  # 给于一些关键词， 随机生成一句话
# {'fields': {'颜色': ['蓝色', '黄色']}, 'preferences': {'style': '让它像诗歌一样。'}, 
# 'text': '在辽阔的天空下，蓝色如梦的晨光舞动，仿佛在编织一首关于希望的诗篇，而黄色的阳光则如流淌的金河，静静流淌，唤醒沉睡的大地，带来了新一日的生机与活力。'}
