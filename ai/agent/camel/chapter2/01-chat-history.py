from camel.memories.blocks import ChatHistoryBlock
from camel.memories.records import MemoryRecord
from camel.types import OpenAIBackendRole
from camel.messages import BaseMessage

# 创建一个 ChatHistoryBlock 实例
chat_history = ChatHistoryBlock(keep_rate=0.8)

# 模拟写入一些消息记录
chat_history.write_records([
    MemoryRecord(message=BaseMessage.make_assistant_message(role_name="user", content="Hello,今天感觉怎么样？"),
                 role_at_backend=OpenAIBackendRole.USER),
    MemoryRecord(message=BaseMessage.make_user_message(role_name="assistant", content="我很好，谢谢！"),
                 role_at_backend=OpenAIBackendRole.ASSISTANT),
    MemoryRecord(message=BaseMessage.make_user_message(role_name="user", content="你能做些什么？"),
                 role_at_backend=OpenAIBackendRole.USER),
    MemoryRecord(message=BaseMessage.make_assistant_message(role_name="assistant", content="我可以帮助你完成各种任务。"),
                 role_at_backend=OpenAIBackendRole.ASSISTANT),
])

# 检索最近的 3 条消息
recent_records = chat_history.retrieve(window_size=4)

for record in recent_records:
    print(f"消息: {record.memory_record.message.content}, 权重: {record.score}")

# 消息: Hello,今天感觉怎么样？, 权重: 0.40960000000000013
# 消息: 我很好，谢谢！, 权重: 0.5120000000000001
# 消息: 你能做些什么？, 权重: 0.6400000000000001
# 消息: 我可以帮助你完成各种任务。, 权重: 0.8
