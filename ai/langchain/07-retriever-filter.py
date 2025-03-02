import datetime
from os import getenv

from typing import Optional, List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.huggingface import HuggingFaceInferenceAPIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import YoutubeLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from pydantic.v1 import BaseModel, Field
from langchain_core.documents import Document

# 创建模型
model = ChatOpenAI(
  openai_api_key=getenv("OPENROUTER_API_KEY"),
  openai_api_base="https://openrouter.ai/api/v1",
  model_name="openai/gpt-4o",
)

embeddings = HuggingFaceInferenceAPIEmbeddings(
    api_key=getenv("HUGGINGFACE_API_TOKEN"),
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


persist_dir = '07-chroma_data_dir'  # 存放向量数据库的目录

# 一些YouTube的视频连接
urls = [
    "https://www.youtube.com/watch?v=HAn9vnJy6S4",
    "https://www.youtube.com/watch?v=dA1cHGACXCo",
    "https://www.youtube.com/watch?v=ZcEMLz27sL4",
    "https://www.youtube.com/watch?v=hvAPnpSfSGo",
    "https://www.youtube.com/watch?v=EhlPDL4QrWY",
    "https://www.youtube.com/watch?v=mmBo8nlu2j0",
    "https://www.youtube.com/watch?v=rQdibOsL1ps",
    "https://www.youtube.com/watch?v=28lC4fqukoc",
    "https://www.youtube.com/watch?v=es-9MgxB-uc",
    "https://www.youtube.com/watch?v=wLRHwKuKvOE",
    "https://www.youtube.com/watch?v=ObIltMaRJvY",
    "https://www.youtube.com/watch?v=DjuXACWYkkU",
    "https://www.youtube.com/watch?v=o7C9ld6Ln-M",
]

# =================== 写入数据 =============================
docs = []  # document的数组
for url in urls:
    # 一个Youtube的视频对应一个document
    # https://github.com/pytube/pytube/issues/2074，修改 vid_info 函数中的这一行即可：innertube = InnerTube(client='WEB', use_oauth=self.use_oauth, allow_cache=self.allow_oauth_cache)
    docs.extend(YoutubeLoader.from_youtube_url(url, add_video_info=True).load())

# print(len(docs))
# print(docs[0])
# 给doc添加额外的元数据： 视频发布的年份
for doc in docs:
    doc.metadata['publish_year'] = int(
        datetime.datetime.strptime(doc.metadata['publish_date'], '%Y-%m-%d %H:%M:%S').strftime('%Y'))


print(docs[0].metadata)
# print(docs[0].page_content[:500])  # 第一个视频的字幕内容

# 根据多个doc构建向量数据库
text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=30)
split_doc = text_splitter.split_documents(docs)
# 向量数据库的持久化
vectorstore = Chroma.from_documents(split_doc, embeddings, persist_directory=persist_dir)  # 并且把向量数据库持久化到磁盘

# =================== 查询数据 =============================
# 加载磁盘中的向量数据库
vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)

# 测试向量数据库的相似检索
# result = vectorstore.similarity_search_with_score('how do I build a RAG agent')
# print(result[0])
# print(result[0][0].metadata['publish_year'])

system = """You are an expert at converting user questions into database queries. \
You have access to a database of tutorial videos about a software library for building LLM-powered applications. \
Given a question, return a list of database queries optimized to retrieve the most relevant results.

If there are acronyms or words you are not familiar with, do not try to rephrase them."""
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)


# 使用 Pydantic (BaseModel) 的主要原因是 对 LLM（大模型）的输出进行结构化解析和验证
class Search(BaseModel):
    """
    定义了一个数据模型
    """
    # 内容的相似性和发布年份
    query: str = Field(None, description='Similarity search query applied to video transcripts.')
    publish_year: Optional[int] = Field(None, description='Year video was published')


# with_structured_output(Search) 让 LLM 必须返回符合 Search 数据模型的 JSON 结构，确保输出一致。
chain = {'question': RunnablePassthrough()} | prompt | model.with_structured_output(Search)

# resp1 = chain.invoke('how do I build a RAG agent?')
# print(resp1)
# # query='build a RAG agent' publish_year=None
# resp2 = chain.invoke('videos on RAG published in 2023')
# print(resp2)
# # query='RAG' publish_year=2023 


def retrieval(search: Search) -> List[Document]:
    _filter = None
    if search.publish_year:
        # 根据publish_year，存在得到一个检索条件
        # "$eq"是Chroma向量数据库的固定语法
        _filter = {'publish_year': {"$eq": search.publish_year}}

    return vectorstore.similarity_search(search.query, filter=_filter)

new_chain = chain | retrieval

# 带上 2023 年这个过滤条件
result = new_chain.invoke('videos on RAG published in 2023')
# [('LangServe and LangChain Templates Webinar', 2023), ('LangServe and LangChain Templates Webinar', 2023), ('Getting Started with Multi-Modal LLMs', 2023), ('Getting Started with Multi-Modal LLMs', 2023)]
# result = new_chain.invoke('RAG tutorial')
# [('LangServe and LangChain Templates Webinar', 2023), ('Build and Deploy a RAG app with Pinecone Serverless', 2024), ('Build and Deploy a RAG app with Pinecone Serverless', 2024), ('Getting Started with Multi-Modal LLMs', 2023)]
print([(doc.metadata['title'], doc.metadata['publish_year']) for doc in result])

