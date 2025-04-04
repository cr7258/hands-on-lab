from camel.agents import ChatAgent
from camel.retrievers import AutoRetriever
from camel.types import StorageType
from camel.models import ModelFactory
from camel.types import ModelPlatformType
from camel.embeddings import SentenceTransformerEncoder
from os import getenv

embedding_model=SentenceTransformerEncoder(model_name='intfloat/e5-large-v2')

model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
    model_type="Qwen/Qwen2.5-72B-Instruct",
    url='https://api-inference.modelscope.cn/v1/',
    api_key=getenv("MODELSCOPE_API_KEY")
)

def single_agent(query: str) ->str :
    # 设置agent角色
    assistant_sys_msg = """你是一个帮助回答问题的助手，
        我会给你原始查询和检索到的上下文，
        根据检索到的上下文回答原始查询，
        如果你无法回答问题就说我不知道。"""

    # 添加自动检索器
    auto_retriever = AutoRetriever(
            vector_storage_local_path="local_data2/",
            storage_type=StorageType.QDRANT,
            embedding_model=embedding_model)

    # 运行向量检索器
    retrieved_info = auto_retriever.run_vector_retriever(
        query=query,
        contents=[
            # "local_data/camel_paper.pdf",  # 示例本地路径
            "https://github.com/camel-ai/camel/wiki/Contributing-Guidlines",  # 示例url
        ],
        top_k=1,
        return_detailed_info=False,
        similarity_threshold=0.5
    )

    # 将检索到的信息传递给agent
    user_msg = str(retrieved_info)
    agent = ChatAgent(assistant_sys_msg,model =model)

    # 获取响应
    assistant_response = agent.step(user_msg)
    return assistant_response.msg.content

print(single_agent("如果我对贡献CAMEL项目感兴趣，我应该怎么做？"))
# 根据提供的上下文信息，您可以通过以下步骤对CAMEL项目做出贡献：

# 1. **访问项目仓库**：首先，您需要访问CAMEL项目的GitHub仓库。您可以点击仓库链接或搜索 `camel-ai/camel` 找到它。

# 2. **阅读贡献指南**：大多数开源项目都有一个 `CONTRIBUTING.md` 文件，其中详细说明了如何贡献代码、报告问题等。请仔细阅读该文件以了解项目的贡献流程和规范。

# 3. ** Fork 项目**：点击仓库页面右上角的 "Fork" 按钮，将项目 fork 到您的 GitHub 账户中。

# 4. **克隆项目**：使用 `git clone` 命令将 fork 后的项目克隆到本地计算机上。

# 5. **创建分支**：在本地创建一个新的分支来开发您的功能或修复问题。
#    ```sh
#    git checkout -b my-feature-branch
#    ```

# 6. **开发和测试**：根据项目的需求进行开发，并确保所有测试通过。

# 7. **提交更改**：将您的更改提交到本地仓库。
#    ```sh
#    git add .
#    git commit -m "Add your commit message here"
#    ```

# 8. **推送更改**：将本地分支推送到您的 GitHub 仓库。
#    ```sh
#    git push origin my-feature-branch
#    ```

# 9. **创建 Pull Request (PR)**：在 GitHub 上，点击 "Compare & pull request" 按钮，创建一个 PR 到原项目的主分支。在 PR 中详细描述您的更改内容和原因。

# 10. **等待审查**：项目维护者会审查您的 PR 并可能要求您进行一些修改。根据反馈进行相应的调整。

# 如果您有任何疑问或需要进一步的帮助，可以在项目的 Issues 页面提出问题或联系项目维护者。希望这些步骤能帮助您顺利地为 CAMEL 项目做出贡献！