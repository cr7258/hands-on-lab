from os import getenv
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import chat_agent_executor
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

model = ChatOpenAI(
  openai_api_key=getenv("OPENROUTER_API_KEY"),
  openai_api_base="https://openrouter.ai/api/v1",
  model_name="openai/gpt-3.5-turbo",
)

# sqlalchemy 初始化MySQL数据库的连接
HOSTNAME = '127.0.0.1'
PORT = '3306'
DATABASE = 'test_db'
USERNAME = 'root'
PASSWORD = '123123'
# mysqlclient驱动URL
MYSQL_URI = 'mysql+mysqldb://{}:{}@{}:{}/{}?charset=utf8mb4'.format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)

db = SQLDatabase.from_uri(MYSQL_URI)

# 创建工具
toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()

# 传入 prompt 是可选的
system_prompt = """
您是一个被设计用来与SQL数据库交互的代理。
给定一个输入问题，创建一个语法正确的SQL语句并执行，然后查看查询结果并返回答案。
除非用户指定了他们想要获得的示例的具体数量，否则始终将SQL查询限制为最多10个结果。
你可以按相关列对结果进行排序，以返回MySQL数据库中最匹配的数据。
您可以使用与数据库交互的工具。在执行查询之前，你必须仔细检查。如果在执行查询时出现错误，请重写查询SQL并重试。
不要对数据库做任何DML语句(插入，更新，删除，删除等)。

首先，你应该查看数据库中的表，看看可以查询什么。
不要跳过这一步。
然后查询最相关的表的模式。
"""
system_message = SystemMessage(content=system_prompt)

# 创建代理
# 在 Python 函数参数列表中，* 之后的参数被称为 keyword-only parameters（仅关键字参数）。它们必须使用关键字参数方式传递，而不能作为位置参数传递。查看 create_react_agent 中的参数，prompt 参数在 * 后面，因此必须指定参数名。
agent_executor = chat_agent_executor.create_tool_calling_executor(model, tools, prompt=system_message)

# resp = agent_executor.invoke({'messages': [HumanMessage(content='请问：员工表中有多少条数据？')]})
# resp = agent_executor.invoke({'messages': [HumanMessage(content='那种性别的员工人数最多？')]})
resp = agent_executor.invoke({'messages': [HumanMessage(content='哪个部门下面的员工人数最多？')]})

result = resp['messages']
# 最后一个才是真正的答案
print(result[len(result)-1].content)
# 目前研发部下面拥有最多的员工人数，共有2名员工。