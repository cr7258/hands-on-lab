from camel.memories.blocks.vectordb_block import VectorDBBlock
from camel.memories.records import MemoryRecord
from camel.messages import BaseMessage
from camel.embeddings import SentenceTransformerEncoder
from camel.types import OpenAIBackendRole

# 创建一个 VectorDBBlock 实例
vector_db_block = VectorDBBlock(embedding=SentenceTransformerEncoder(model_name="BAAI/bge-m3"))

# 创建一些示例聊天记录
records = [
    MemoryRecord(message=BaseMessage.make_user_message(role_name="user", content="今天天气真好！"), role_at_backend=OpenAIBackendRole.USER),
    MemoryRecord(message=BaseMessage.make_user_message(role_name="user", content="你喜欢什么运动？"), role_at_backend=OpenAIBackendRole.USER),
    MemoryRecord(message=BaseMessage.make_user_message(role_name="user", content="今天天气不错，我们去散步吧。"), role_at_backend=OpenAIBackendRole.USER),
]

# 将记录写入向量数据库
vector_db_block.write_records(records)

# 使用关键词进行检索
keyword = "天气"
retrieved_records = vector_db_block.retrieve(keyword=keyword, limit=3)

for record in retrieved_records:
    print(f"UUID: {record.memory_record.uuid}, Message: {record.memory_record.message.content}, Score: {record.score}")

# UUID: 72616148-476f-472b-a077-dd137c8e0eb8, Message: 今天天气真好！, Score: 0.7798632418076265
# UUID: 2555b978-e53b-4141-8d64-2f3173437f40, Message: 今天天气不错，我们去散步吧。, Score: 0.6920891004089285
# UUID: 979d701c-e541-4bd4-8993-fead63537dec, Message: 你喜欢什么运动？, Score: 0.5345360551139158
