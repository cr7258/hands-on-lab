from camel.retrievers import AutoRetriever
from camel.types import StorageType
from camel.embeddings import SentenceTransformerEncoder

embedding_model=SentenceTransformerEncoder(model_name='intfloat/e5-large-v2')

# 初始化 AutoRetriever
ar = AutoRetriever(
    vector_storage_local_path="retrievers",  # 向量存储本地路径
    storage_type=StorageType.QDRANT,               # 使用 Qdrant 作为存储类型
    embedding_model=embedding_model
)

# 使用 Auto Retriever 执行嵌入、存储和查询
retrieved_info = ar.run_vector_retriever(
    contents=[
        "https://www.camel-ai.org/",  # 示例 URL
    ],
    query="What is CAMEL-AI",         # 查询字符串
    return_detailed_info=True         # 是否返回详细信息，包括元数据
)

# 打印检索结果
print(retrieved_info)