from llama_index.core import SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.ingestion import (
    DocstoreStrategy,
    IngestionPipeline,
    IngestionCache,
)
from llama_index.storage.kvstore.redis import RedisKVStore as RedisCache
from llama_index.storage.docstore.redis import RedisDocumentStore
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.redis import RedisVectorStore
from llama_index.core import VectorStoreIndex
from redisvl.schema import IndexSchema

# load documents with deterministic IDs
documents = SimpleDirectoryReader("./07-data", filename_as_id=True).load_data()

embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

custom_schema = IndexSchema.from_dict(
    {
        "index": {"name": "redis_vector_store", "prefix": "doc"},
        # customize fields that are indexed
        "fields": [
            # required fields for llamaindex
            {"type": "tag", "name": "id"},
            {"type": "tag", "name": "doc_id"},
            {"type": "text", "name": "text"},
            # custom vector field for bge-small-en-v1.5 embeddings
            {
                "type": "vector",
                "name": "vector",
                "attrs": {
                    "dims": 384,
                    "algorithm": "hnsw",
                    "distance_metric": "cosine",
                },
            },
        ],
    }
)

pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(),
        embed_model,
    ],
    docstore=RedisDocumentStore.from_host_and_port(
        "localhost", 6379, namespace="document_store"
    ),
    vector_store=RedisVectorStore(
        schema=custom_schema,
        redis_url="redis://localhost:6379",
    ),
    cache=IngestionCache(
        cache=RedisCache.from_host_and_port("localhost", 6379),
        collection="redis_cache",
    ),
    docstore_strategy=DocstoreStrategy.UPSERTS,
)

# nodes = pipeline.run(documents=documents)
# for node in nodes:
#     print(f"Node: {node.text}")
# # Node: This is a test file: one
# # Node: This is a test file: two


# 执行代码前先写入一条新文档，更新一条已存在的文档
# echo "This is a test file: three" > 07-data/test3.txt
# echo "Add new line: one" >> 07-data/test1.txt
nodes = pipeline.run(documents=documents)
for node in nodes:
    print(f"Node: {node.text}")
# Node: This is a test file: one
# Add new line: one
# Node: This is a test file: three