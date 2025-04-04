from camel.embeddings import SentenceTransformerEncoder
from camel.retrievers import VectorRetriever, BM25Retriever
from camel.storages.vectordb_storages import QdrantStorage
from typing import List,Dict

def rrf(vector_results: List[Dict], text_results: List[Dict], k: int=10, m: int=60):
    """
    使用RRF算法对两组检索结果进行重排序
    
    params:
    vector_results (list): 向量召回的结果列表，每个元素是包含'text'的字典
    text_results (list): 文本召回的结果列表，每个元素是包含'text'的字典
    k(int): 排序后返回前k个
    m (int): 超参数
    
    return:
    重排序后的结果列表，每个元素是(文档内容, 融合分数)
    """
    doc_scores = {}
    
    # 遍历向量检索结果
    for rank, result in enumerate(vector_results):
        text = result['text']
        doc_scores[text] = doc_scores.get(text, 0) + 1 / (rank + m)
    
    # 遍历文本检索结果
    for rank, result in enumerate(text_results):
        text = result['text']
        doc_scores[text] = doc_scores.get(text, 0) + 1 / (rank + m)
    
    # 按融合分数排序并返回前k个结果
    sorted_results = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)[:k]
    return sorted_results

# 初始化检索器
embedding_model = SentenceTransformerEncoder(model_name='intfloat/e5-large-v2')
vector_storage = QdrantStorage(
    vector_dim=embedding_model.get_output_dim(),
    collection="demo_collection",
    path="storage_customized_run",
    collection_name="paper"
)

vr = VectorRetriever(embedding_model=embedding_model, storage=vector_storage)
bm25r = BM25Retriever()

# 处理文档
content_path = "local_data/camel_paper.pdf"
vr.process(content=content_path)
bm25r.process(content_input_path=content_path)

# 查询
query = "CAMEL是什么"
vector_results = vr.query(query=query,top_k=10)
bm25_results = bm25r.query(query=query, top_k=10)

# 融合排序
rrf_results = rrf(vector_results, bm25_results)
print(rrf_results)