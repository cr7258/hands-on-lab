from langchain.agents import initialize_agent, AgentType
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_core.tools import tool, StructuredTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from os import getenv

# 自定义工具：https://python.langchain.com/v0.1/docs/modules/tools/custom_tools

llm = ChatOpenAI(
  openai_api_key=getenv("OPENROUTER_API_KEY"),
  openai_api_base="https://openrouter.ai/api/v1",
  model_name="openai/gpt-4o",
)

class SearchInput(BaseModel):
    query: str = Field(description='你搜索的关键词')


# 方法一：使用 @tool 装饰器
@tool('my_search_tool', args_schema=SearchInput, return_direct=True)
def my_search(query: str) -> str:
    """用来搜索老肖电脑上的数据"""
    return '我是一个搜索的工具'


# 方法二：使用 StructuredTool
def sort_num(num: str):
    """把所有的数字的数字重新排序"""
    return sorted(eval(num))

class SortToolInput(BaseModel):
    num: str = Field(description='待排序的类别字符串')

sort_tool = StructuredTool.from_function(
    func=sort_num,  # 工具的函数
    name='sort_num',
    description='排序列表中的数字',
    args_schema=SortToolInput,
    return_direct=True
)

# langchain 内置的工具
tools = load_tools(['llm-math', 'arxiv'], llm)
tools = [sort_tool, my_search] + tools

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True,  # 如果解析报错，继续
    verbose=True,
)

agent.run('计算 2 ** 5 + 4， 并且给`[3, 6, 9, 23, 1,]`排一下序')
# > Entering new AgentExecutor chain...
# To solve the problem, I need to perform two tasks: calculate the expression \(2^{5} + 4\) and sort the list \([3, 6, 9, 23, 1]\).

# 1. **Calculate \(2^{5} + 4\)**: I will use the calculator tool for this.
# 2. **Sort the list \([3, 6, 9, 23, 1]\)**: I will use the sort_num tool.

# Let's begin with the calculation.

# Action: Calculator
# Action Input: 2**5 + 4
# Observation: Answer: 36
# Thought:The result of the calculation \(2^{5} + 4\) is 36. Now, I will sort the given list \([3, 6, 9, 23, 1]\).

# Action: sort_num
# Action Input: [3, 6, 9, 23, 1]
# Observation: [1, 3, 6, 9, 23]


# > Finished chain.