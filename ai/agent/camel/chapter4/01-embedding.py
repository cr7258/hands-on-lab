from camel.memories.blocks.vectordb_block import VectorDBBlock
from camel.memories.records import MemoryRecord
from camel.messages import BaseMessage
from camel.embeddings import SentenceTransformerEncoder,OpenAICompatibleEmbedding
from camel.types import OpenAIBackendRole
from dotenv import load_dotenv
import os
from camel.storages.vectordb_storages import QdrantStorage
load_dotenv()

embedding = OpenAICompatibleEmbedding(
    model_type="text-embedding-v3",
    url= 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    api_key=os.getenv("QWEN_API_KEY")
    )

#使用OpenAICompatibleEmbedding时 需要先调用 embed_list 来确定输出维度
embeddings = embedding.embed_list(["测试文本"])
print(embeddings)
