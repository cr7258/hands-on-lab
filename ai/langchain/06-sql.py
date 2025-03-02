from os import getenv
from operator import itemgetter

from langchain.chains.sql_database.query import create_sql_query_chain
from langchain_community.tools import QuerySQLDataBaseTool
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

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

# 测试连接是否成功
# print(db.get_usable_table_names())
# print(db.run('select * from t_emp limit 10;'))

# 直接使用大模型和数据库整合, 只能根据你的问题生成SQL
# 初始化生成SQL的chain
test_chain = create_sql_query_chain(model, db)
# resp = test_chain.invoke({'question': '请问：员工表中有多少条数据？'})
# print(resp)
# SELECT COUNT(*) AS total_records FROM `employee`;

answer_prompt = PromptTemplate.from_template(
    """给定以下用户问题、SQL语句和SQL执行后的结果，回答用户问题。
    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    回答: """
)
# 创建一个执行sql语句的工具
execute_sql_tool = QuerySQLDataBaseTool(db=db)

# 这段代码创建了一个完整的处理链（chain），它按以下步骤执行：
# 1. RunnablePassthrough.assign(query=test_chain) - 首先，它接收输入（包含'question'键的字典），并使用之前定义的test_chain（SQL查询生成链）生成SQL查询语句。这个生成的SQL查询被赋值给一个名为'query'的新键。
# 2. assign(result=itemgetter('query') | execute_sql_tool) - 然后，它从上一步的结果中提取'query'键的值（使用itemgetter('query')），并将这个SQL查询传递给execute_sql_tool工具执行。执行结果被赋值给一个名为'result'的新键。
# 3. answer_prompt - 接下来，整个包含question、query和result的字典被传递给answer_prompt模板，生成一个提示文本。
# 4. model - 这个提示文本被传递给之前定义的语言模型（gpt-3.5-turbo）进行处理。
# 5. StrOutputParser() - 最后，模型的输出被解析为字符串形式。
chain = (RunnablePassthrough.assign(query=test_chain).assign(result=itemgetter('query') | execute_sql_tool)
         | answer_prompt
         | model
         | StrOutputParser()
         )


rep = chain.invoke(input={'question': '请问：员工表中有多少条数据？'})
print(rep)
# 员工表中共有4条数据。
