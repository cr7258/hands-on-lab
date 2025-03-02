from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import chat_agent_executor
from os import getenv


# 创建模型
model = ChatOpenAI(
  openai_api_key=getenv("OPENROUTER_API_KEY"),
  openai_api_base="https://openrouter.ai/api/v1",
  model_name="openai/gpt-4o",
)

# 没有任何代理的情况下
# result = model.invoke([HumanMessage(content='北京天气怎么样？')])
# print(result)

# LangChain 内置了一个工具，可以轻松地使用 Tavily 搜索引擎作为工具。
# TODO 需要在 TAVILY_API_KEY 环境变量中设置 Tavily 的 API Key
search = TavilySearchResults(max_results=2)  #  max_results: 只返回两个结果
# print(search.invoke('北京的天气怎么样？'))

# 让模型绑定工具
tools = [search]
# model_with_tools = model.bind_tools(tools)

# 模型可以自动推理：是否需要调用工具去完成用户的答案
# resp = model_with_tools.invoke([HumanMessage(content='中国的首都是哪个城市？')])
#
# print(f'Model_Result_Content: {resp.content}')
# print(f'Tools_Result_Content: {resp.tool_calls}')
#
# resp2 = model_with_tools.invoke([HumanMessage(content='北京天气怎么样？')])
#
# print(f'Model_Result_Content: {resp2.content}')
# print(f'Tools_Result_Content: {resp2.tool_calls}')

#  创建代理

agent_executor = chat_agent_executor.create_tool_calling_executor(model, tools)

resp = agent_executor.invoke({'messages': [HumanMessage(content='中国的首都是哪个城市？')]})
print(resp['messages'][-1].content)
# 中国的首都是北京市。

resp2 = agent_executor.invoke({'messages': [HumanMessage(content='北京天气怎么样？')]})

print(resp2['messages'][-1].content)
# - 2025年2月8日（今天）：白天晴转多云，气温在 -11℃ 到 -1℃ 之间，西北风5级，空气质量为优。
# - 未来几天的预测：
#   - 2月9日：晴，气温 -10℃ 到 1℃，南风微风。
#   - 2月10日：晴转多云，气温 -6℃ 到 4℃，东北风微风。
#   - 2月11日：多云，气温 -5℃ 到 5℃，北风微风。

# 此外，北京市发布了持续低温蓝色预警信号，近期受强冷空气影响，预计本市大部分地区夜间最低气温将持续低于零下10℃。请注意防范低温天气带来的影响。