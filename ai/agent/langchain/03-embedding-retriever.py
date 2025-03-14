from os import getenv
from langchain_community.embeddings.huggingface import HuggingFaceInferenceAPIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
  openai_api_key=getenv("OPENROUTER_API_KEY"),
  openai_api_base="https://openrouter.ai/api/v1",
  model_name="openai/gpt-4o",
)

huggingface_embedding = HuggingFaceInferenceAPIEmbeddings(
    api_key=getenv("HUGGINGFACE_API_TOKEN"),
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# vector = huggingface_embedding.embed_query("Hello, world!")
# print(vector)

# 准备测试数据，假设我们提供的文档数据如下：
documents = [
    Document(
        page_content="狗是伟大的伴侣，以其忠诚和友好而闻名。",
        metadata={"source": "哺乳动物宠物文档"},
    ),
    Document(
        page_content="猫是独立的宠物，通常喜欢自己的空间。",
        metadata={"source": "哺乳动物宠物文档"},
    ),
    Document(
        page_content="金鱼是初学者的流行宠物，需要相对简单的护理。",
        metadata={"source": "鱼类宠物文档"},
    ),
    Document(
        page_content="鹦鹉是聪明的鸟类，能够模仿人类的语言。",
        metadata={"source": "鸟类宠物文档"},
    ),
    Document(
        page_content="兔子是社交动物，需要足够的空间跳跃。",
        metadata={"source": "哺乳动物宠物文档"},
    ),
]


# 实例化一个向量数空间
vector_store = Chroma.from_documents(documents, embedding=huggingface_embedding)

# 相似度的查询: 返回相似的分数， 分数越低相似度越高
# print(vector_store.similarity_search_with_score('咖啡猫'))

# 检索器: bind(k=1) 返回相似度最高的第一个
retriever = RunnableLambda(vector_store.similarity_search).bind(k=1)

# print(retriever.batch(['咖啡猫', '金鱼']))
# [[Document(id='ea0053c1-c013-4fcc-97a3-722e6a0881e5', metadata={'source': '哺乳动物宠物文档'}, page_content='猫是独立的宠物，通常喜欢自己的空间。')], 
# [Document(id='2f8394cc-6463-4bd9-93e4-ee6a91b17b35', metadata={'source': '鱼类宠物文档'}, page_content='金鱼是初学者的流行宠物，需要相对简单的护理。')]]

# 提示模板
message = """
使用提供的上下文仅回答这个问题:
{question}
上下文:
{context}
"""

prompt_temp = ChatPromptTemplate.from_messages([('human', message)])

# RunnablePassthrough 允许我们将用户的问题之后再传递给 prompt 和 model
chain = {'question': RunnablePassthrough(), 'context': retriever} | prompt_temp | model

resp = chain.invoke('请介绍一下猫？')

print(resp.content)
# 猫是独立的宠物，通常喜欢自己的空间。
