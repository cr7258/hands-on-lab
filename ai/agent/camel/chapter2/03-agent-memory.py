from camel.memories import (
    LongtermAgentMemory,
    MemoryRecord,
    ScoreBasedContextCreator,
    ChatHistoryBlock,
    VectorDBBlock,
)
from camel.messages import BaseMessage
from camel.types import ModelType, OpenAIBackendRole
from camel.utils import OpenAITokenCounter
from camel.embeddings import SentenceTransformerEncoder

# 1. 初始化内存系统
memory = LongtermAgentMemory(
    context_creator=ScoreBasedContextCreator(
        token_counter=OpenAITokenCounter(ModelType.GPT_4O_MINI),
        token_limit=1024,
    ),
    chat_history_block=ChatHistoryBlock(),
    vector_db_block=VectorDBBlock(embedding=SentenceTransformerEncoder(model_name="BAAI/bge-m3")),
)

# 2. 创建记忆记录
records = [
    MemoryRecord(
        message=BaseMessage.make_user_message(
            role_name="User",
            content="什么是CAMEL AI?"
        ),
        role_at_backend=OpenAIBackendRole.USER,
    ),
    MemoryRecord(
        message=BaseMessage.make_assistant_message(
            role_name="Agent",
            content="CAMEL-AI是第一个LLM多智能体框架,并且是一个致力于寻找智能体 scaling law 的开源社区。"
        ),
        role_at_backend=OpenAIBackendRole.ASSISTANT,
    ),
]

# 3. 写入记忆
memory.write_records(records)

context, token_count = memory.get_context()

print(context)
print(f'token消耗: {token_count}')

# [{'role': 'user', 'content': '什么是CAMEL AI?'}, {'role': 'assistant', 'content': 'CAMEL-AI是第一个LLM多智能体框架,并且是一个致力于寻找智能体 scaling law 的开源社区。'}]
# token消耗: 52

from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import ModelPlatformType
from os import getenv

# 定义系统消息
sys_msg = "你是一个好奇的智能体，正在探索宇宙的奥秘。"

# 初始化agent 调用在线Qwen/Qwen2.5-72B-Instruct
model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
    model_type="Qwen/Qwen2.5-72B-Instruct",
    url='https://api-inference.modelscope.cn/v1/',
    api_key=getenv("MODELSCOPE_API_KEY")
)
agent = ChatAgent(system_message=sys_msg, model=model)

# 定义用户消息
usr_msg = "告诉我基于我们讨论的内容，哪个是第一个LLM多智能体框架？"

# 将memory赋值给agent
agent.memory = memory
# 发送消息给agent
response = agent.step(usr_msg)
# 查看响应
print(response.msgs[0].content)
# 根据我们的讨论，CAMEL-AI 是第一个LLM（大型语言模型）多智能体框架。这个框架旨在通过多个智能体的协作来探索和实现更高级别的AI能力，同时它也是一个开源社区，专注于研究智能体的scaling law（扩展法则）。