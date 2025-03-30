from camel.embeddings import SentenceTransformerEncoder
from camel.retrievers import VectorRetriever

embedding_model=SentenceTransformerEncoder(model_name='intfloat/e5-large-v2')

# 指定内容来源路径，可以是文件路径或 URL
content_input_path = "https://www.camel-ai.org/"

# 创建或初始化向量存储（例如 QdrantStorage）
from camel.storages.vectordb_storages import QdrantStorage

vector_storage = QdrantStorage(
    vector_dim=embedding_model.get_output_dim(),  # 嵌入向量的维度
    collection_name="my first collection",          # 向量存储的集合名称
    path="storage_customized_run",                  # 向量存储的位置
)
# 初始化 VectorRetriever
vr = VectorRetriever(embedding_model=embedding_model,storage=vector_storage)
# 将内容嵌入并存储到向量存储中
vr.process(content_input_path, chunk_type="chunk_by_title")

# 指定查询字符串
query = "What is CAMEL"

# 执行查询并检索结果
results = vr.query(query)

# 打印检索结果
print(results)

# [{'similarity score': '0.8443561982958085', 'content path': 'https://www.camel-ai.org/',
# 'metadata': {'filetype': 'text/html', 'languages': ['eng'], 'link_texts': ['Chain-of-Thought (CoT) Data Generation', 'Self-Instruct: Instruction Generation'],
# 'link_urls': ['https://github.com/camel-ai/camel/blob/master/camel/datagen/cot_datagen.py', 'https://github.com/camel-ai/camel/tree/master/camel/datagen/self_instruct'],
# 'url': 'https://www.camel-ai.org/', 'piece_num': 8}, 'extra_info': {},
# 'text': "You Can Use CAMEL to Build\n\nCAMEL is the world's first multi-agent system. It is designed to be data-driven, stateful, and agent-friendly.\n\n1. Data Generation\n\nChain-of-Thought (CoT) Data Generation\n\nThe Chain of Thought (CoT) data generation module implements a sophisticated system for generating high-quality reasoning paths through chat agent interactions. It combines several advanced algorithms to produce and validate reasoning chains.\n\nSelf-Instruct: Instruction Generation"}]
