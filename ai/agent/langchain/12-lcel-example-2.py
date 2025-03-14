from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI
from os import getenv

# 需求：  提示词1--> llm--> 文本----提示词2---->llm ---评分

llm = ChatOpenAI(
  openai_api_key=getenv("OPENROUTER_API_KEY"),
  openai_api_base="https://openrouter.ai/api/v1",
  model_name="openai/gpt-4o",
)

gather_preferences_prompt = PromptTemplate.from_template(
    "用户输入了一些餐厅偏好：{input1}\n"
    "请将用户的偏好总结为清晰的需求："
)

recommend_restaurants_prompt = PromptTemplate.from_template(
    "基于用户需求：{input2}\n"
    "请推荐 3 家适合的餐厅，并说明推荐理由："
)

# 步骤 3：总结推荐内容供用户快速参考
summarize_recommendations_prompt = PromptTemplate.from_template(
    "以下是餐厅推荐和推荐理由：\n{input3}\n"
    "请总结成 2-3 句话，供用户快速参考："
)

chain = gather_preferences_prompt | llm | recommend_restaurants_prompt | llm | summarize_recommendations_prompt | llm | StrOutputParser()

print(chain.invoke({'input1': '我喜欢安静的地方， 有素食的餐厅更好，而且价格也不贵。'}))
# 推荐的三家餐厅分别是静雅素食餐厅、绿荫美食坊和心灵厨房，均提供安静的就餐环境和健康素食选项，同时价格合理。餐厅不仅重视舒适的用餐氛围，还注重环保理念和食材新鲜，非常适合寻求宁静与健康饮食体验的顾客。