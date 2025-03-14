from os import getenv
import bs4
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# 创建模型
model = ChatOpenAI(
  openai_api_key=getenv("OPENROUTER_API_KEY"),
  openai_api_base="https://openrouter.ai/api/v1",
  model_name="openai/gpt-4o",
)


# 1、加载数据: 一篇博客内容数据
loader = WebBaseLoader(
    web_paths=['https://lilianweng.github.io/posts/2023-06-23-agent/'],
    bs_kwargs=dict(
        parse_only=bs4.SoupStrainer(class_=('post-header', 'post-title', 'post-content'))
    )
)

docs = loader.load()

# print(len(docs))
# print(docs)

# 2、大文本的切割
# text = "hello world, how about you? thanks, I am fine.  the machine learning class. So what I wanna do today is just spend a little time going over the logistics of the class, and then we'll start to talk a bit about machine learning"
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

splits = splitter.split_documents(docs)

# 2、存储
vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

# 3、检索器
retriever = vectorstore.as_retriever()

# 整合

# 创建一个问题的模板
system_prompt = """You are an assistant for question-answering tasks. 
Use the following pieces of retrieved context to answer 
the question. If you don't know the answer, say that you 
don't know. Use three sentences maximum and keep the answer concise.\n

{context}
"""
prompt = ChatPromptTemplate.from_messages(  # 提问和回答的 历史记录 模板
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

# 得到chain
chain1 = create_stuff_documents_chain(model, prompt)

# chain2 = create_retrieval_chain(retriever, chain1)

# resp = chain2.invoke({'input': "What is Task Decomposition?"})
#
# print(resp['answer'])

'''
注意：
一般情况下，我们构建的链（chain）直接使用输入问答记录来关联上下文。但在此案例中，查询检索器也需要对话上下文才能被理解。

解决办法：
添加一个子链(chain)，它采用最新用户问题和聊天历史，并在它引用历史信息中的任何信息时重新表述问题。这可以被简单地认为是构建一个新的“历史感知”检索器。
这个子链的目的：让检索过程融入了对话的上下文。
'''

# 创建一个子链
# 子链的提示模板
contextualize_q_system_prompt = """Given a chat history and the latest user question 
which might reference context in the chat history, 
formulate a standalone question which can be understood 
without the chat history. Do NOT answer the question, 
just reformulate it if needed and otherwise return it as is."""

retriever_history_temp = ChatPromptTemplate.from_messages(
    [
        ('system', contextualize_q_system_prompt),
        MessagesPlaceholder('chat_history'),
        ("human", "{input}"),
    ]
)

# 创建一个子链
history_chain = create_history_aware_retriever(model, retriever, retriever_history_temp)

# 保持问答的历史记录
store = {}


def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


# 创建父链chain: 把前两个链整合
chain = create_retrieval_chain(history_chain, chain1)

result_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key='input',
    history_messages_key='chat_history',
    output_messages_key='answer'
)

# 第一轮对话
resp1 = result_chain.invoke(
    {'input': 'What is Task Decomposition?'},
    config={'configurable': {'session_id': 'zs123456'}}
)

print("第一个问题的答案：")
print(resp1['answer'])
# Task Decomposition is a process that involves breaking down a complex task into smaller, more manageable subtasks. 
# This approach allows for a clearer understanding and execution of the task by addressing each component step-by-step. 
# Techniques like Chain of Thought (CoT) and Tree of Thoughts extend this concept by exploring multiple reasoning possibilities and generating a structured tree of thoughts for better decision-making.

# 第二轮对话
# 要保证 session_id 一致，才能获取到正确的聊天历史记录 
resp2 = result_chain.invoke(
    {'input': 'What are common ways of doing it?'},
    config={'configurable': {'session_id': 'zs123456'}}
)

print("第二个问题的答案：")
print(resp2['answer'])
# Common ways of performing task decomposition include: using simple prompting with a large language model (LLM) such as "Steps for XYZ.\n1." 
# or "What are the subgoals for achieving XYZ?"; utilizing task-specific instructions like "Write a story outline." for tasks like writing a novel; 
# and incorporating inputs from humans to guide the decomposition process.