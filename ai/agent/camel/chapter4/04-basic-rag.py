import os
import requests

os.makedirs('local_data', exist_ok=True)

url = "https://arxiv.org/pdf/2303.17760.pdf"
response = requests.get(url)
with open('local_data/camel_paper.pdf', 'wb') as file:
    file.write(response.content)

from camel.embeddings import SentenceTransformerEncoder
from camel.retrievers import VectorRetriever

embedding_model=SentenceTransformerEncoder(model_name='intfloat/e5-large-v2')

# 创建并初始化一个向量数据库 (以QdrantStorage为例)
from camel.storages.vectordb_storages import QdrantStorage

vector_storage = QdrantStorage(
    vector_dim=embedding_model.get_output_dim(),
    collection="demo_collection",
    path="storage_customized_run",
    collection_name="论文"
)
# 初始化VectorRetriever实例并使用本地模型作为嵌入模型
vr = VectorRetriever(embedding_model= embedding_model,storage=vector_storage)
# 将文件读取、切块、嵌入并储存在向量数据库中，这大概需要1-2分钟
vr.process(
    content="local_data/camel_paper.pdf"
)

# 设定一个查询语句
query = "CAMEL是什么"

# 执行查询并获取结果
results = vr.query(query=query, top_k=1)
print(results)
# [{'similarity score': '0.8193795757674041', 'content path': 'local_data/camel_paper.pdf', 
# 'metadata': {'filetype': 'application/pdf', 'languages': ['eng'], 'page_number': 1, 'piece_num': 1}, 
# 'extra_info': {}, 'text': '3 2 0 2\n\nv o N 2\n\n] I\n\nA . s c [\n\n2 v 0 6 7 7 1 . 3 0 3 2 : v i X r a\n\n
# CAMEL: Communicative Agents for “Mind” Exploration of Large Language Model Society https://www.camel-ai.org\n\nGuohao Li∗ Hasan Abed Al Kader Hammoud*\n\nHani Itani*\n\nDmitrii Khizbullin\n\nBernard Ghanem\n\nKing Abdullah University of Science and Technology (KAUST)\n\nAbstract'}]

retrieved_info_irrevelant = vr.query(
    query="Compared with dumpling and rice, which should I take for dinner?",
    top_k=1,
    similarity_threshold=0.8
)

print(retrieved_info_irrevelant)
# [{'text': 'No suitable information retrieved from local_data/camel_paper.pdf with similarity_threshold = 0.8.'}]