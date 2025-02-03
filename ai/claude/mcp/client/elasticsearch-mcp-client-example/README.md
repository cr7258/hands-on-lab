# 快速上手：实现你的第一个 MCP Client

在 [MCP Server 开发实战：无缝对接 LLM 和 Elasticsearch](https://mp.weixin.qq.com/s/38HiPOOKVKz3C76d_SGkmw) 一文中，我们详细介绍了如何利用 [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) 编写一个 Elasticsearch MCP 服务器，并通过 Claude Desktop 作为 MCP 客户端进行交互。本文将进一步介绍如何使用 MCP Python SDK 编写一个 MCP 客户端，以便更加灵活地与 MCP 服务器进行通信和集成。本文的完整代码可以在 Github 上找到：https://github.com/cr7258/hands-on-lab/tree/main/ai/claude/mcp/client/elasticsearch-mcp-client-example

MCP 系列文章：

- [一文带你入门 MCP（模型上下文协议）](https://mp.weixin.qq.com/s/rcOi7e8F5qGVVF2noCk46Q)
- [MCP Server 开发实战：无缝对接 LLM 和 Elasticsearch](https://mp.weixin.qq.com/s/rcOi7e8F5qGVVF2noCk46Q)
- 快速上手：实现你的第一个 MCP Client（本文）

## MCP 客户端的作用

MCP 客户端充当 LLM 和 MCP 服务器之间的桥梁，MCP 客户端的工作流程如下：

- MCP 客户端首先从 MCP 服务器获取可用的工具列表。
- 将用户的查询连同工具描述通过 [function calling](https://platform.openai.com/docs/guides/function-calling) 一起发送给 LLM。
- LLM 决定是否需要使用工具以及使用哪些工具。
- 如果需要使用工具，MCP 客户端会通过 MCP 服务器执行相应的工具调用。
- 工具调用的结果会被发送回 LLM。
- LLM 基于所有信息生成自然语言响应。
- 最后将响应展示给用户。

## MCP 通信方式

MCP 支持两种通信方式：

- **标准输入输出（Standard Input/Output, stdio）**：客户端通过启动服务器子进程并使用标准输入（stdin）和标准输出（stdout）建立双向通信，一个服务器进程只能与启动它的客户端通信（1:1 关系）。stdio 适用于本地快速集成的场景，在本文中，我们将使用这种方式来编写 MCP 客户端。

- **服务器发送事件（Server-Sent Events, SSE）**：服务器作为独立进程运行，客户端和服务器代码完全解耦，支持多个客户端随时连接和断开。这种方式将在后续的系列文章中单独进行介绍。

## 简单的示例

在开始构建复杂的应用之前，让我们先创建一个最简单的 MCP 客户端。这个基础示例将展示如何连接到 MCP 服务器并使用其提供的工具。

MCP 服务器的代码以及 Elasticsearch 集群的配置文件请参考 [MCP Server 开发实战：无缝对接 LLM 和 Elasticsearch](https://mp.weixin.qq.com/s/38HiPOOKVKz3C76d_SGkmw) 一文。

### 添加依赖

在本教程中，我们将使用 [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) 来编写项目，使用 [uv](https://docs.astral.sh/uv/) 来管理 Python 项目依赖。需要添加如下依赖：

```bash
uv add mcp elasticsearch openai
```

### 设置服务器连接参数

在使用 `stdio` 方式进行通信时，MCP 服务器的进程由 MCP 客户端程序负责启动。因此，我们通过 `StdioServerParameters` 来配置服务器进程的启动参数，包括运行 MCP 服务器的命令及其对应的参数。其中，`sys.argv[1]` 代表客户端程序运行时传入的第一个参数，用于指定服务器脚本的路径，从而确保 MCP 客户端能够正确启动并连接到 MCP 服务器。

```python
server_params = StdioServerParameters(
    command="python",           # 运行命令
    args=[sys.argv[1]],        # 服务器脚本路径
    env=None                   # 可选的环境变量
)
```

### 建立服务器连接

`stdio_client` 负责启动服务器进程并建立双向通信通道，它返回用于读写数据的流对象。`ClientSession` 则在这些流的基础上提供高层的会话管理，包括初始化连接、维护会话状态等。

```python
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
         await session.initialize()
```

### 调用工具

在 MCP 客户端中，我们使用了以下两个函数来与 MCP 服务器进行交互。

- `list_tools()`：获取 MCP 服务器提供的所有可用工具。
- `call_tool(name, args)`：调用指定的工具并获取结果，这里调用 `list_indices` 来获取 Elasticsearch 集群中的索引信息。

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run():
    # 建立连接
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化连接
            await session.initialize()

            # 列出可用工具
            tools = await session.list_tools()
            print("Tools:", tools)

            # 调用工具
            indices = await session.call_tool("list_indices")
            print("Indices:", indices)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
```

### 运行程序

使用以下命令运行 MCP 客户端：

```bash
uv run simple.py <MCP 服务器的代码路径>
```

程序首先会列出所有可用的工具，可以看到总共有 3 个工具：`list_indices`、`get_index` 和 `write_documents`。

```bash
Tools: 
meta=None 
nextCursor=None 
tools=[
    Tool(
        name='list_indices', 
        description='List all Elasticsearch indices', 
        inputSchema={
            'properties': {}, 
            'title': 'list_indicesArguments', 
            'type': 'object'
        }
    ), 
    Tool(
        name='get_index', 
        description='Get detailed information about a specific Elasticsearch index', 
        inputSchema={
            'properties': {
                'index': {
                    'title': 'Index', 
                    'type': 'string'
                }
            }, 
            'required': ['index'], 
            'title': 'get_indexArguments', 
            'type': 'object'
        }
    ), 
    Tool(
        name='write_documents', 
        description='Write multiple documents to an Elasticsearch index using bulk API',
        inputSchema={
            'properties': {
                'index': {
                    'title': 'Index', 
                    'type': 'string'
                }, 
                'documents': {
                    'items': {
                        'type': 'object'
                    }, 
                    'title': 'Documents', 
                    'type': 'array'
                }
            }, 
            'required': ['index', 'documents'], 
            'title': 'write_documentsArguments', 
            'type': 'object'
        }
    )
]
```

然后，程序会调用 `list_indices` 工具，获取 Elasticsearch 集群中的索引信息，并打印出来。

```bash
Indices: 
meta=None 
content=[
    TextContent(
        type='text', 
        text="[
            {'health': 'green', 'status': 'open', 'index': 'student', 'uuid': 'iKl3j9ujSJ2i0GF5v8NUDw', 
             'pri': '1', 'rep': '1', 'docs.count': '3', 'docs.deleted': '0', 'store.size': '12kb', 'pri.store.size': '6kb'}, 

            {'health': 'green', 'status': 'open', 'index': 'teacher', 'uuid': 'vfbwvH7yQGWqRGEG-t4FnA', 
             'pri': '1', 'rep': '1', 'docs.count': '3', 'docs.deleted': '0', 'store.size': '22.6kb', 'pri.store.size': '11.3kb'}, 
             
            {'health': 'green', 'status': 'open', 'index': 'movies', 'uuid': 'JYhacHmXREWmkvwXBaFPmg', 
             'pri': '1', 'rep': '1', 'docs.count': '3', 'docs.deleted': '0', 'store.size': '13.2kb', 'pri.store.size': '6.6kb'}
        ]"
    )
]
isError=False
```

## 进阶示例：集成 LLM

在实际应用中，我们通常希望让 LLM（如 OpenAI、Claude、通义千问等）自主决定调用哪些工具。下面的代码将以通义千问为示例进行演示，并使用 OpenAI SDK 与其交互。为了简化这一过程，我们将借助 [OpenRouter](https://openrouter.ai/) -- 一个统一的 LLM 网关，它提供了 OpenAI 兼容的接口，使我们能够通过相同的 OpenAI API 访问包括通义千问在内的多种 LLM。

OpenRouter 的使用方式非常简单。我们只需在创建 OpenAI 客户端时指定 OpenRouter 的 `base_url` 和 `api_key`，并在调用模型时以 `<provider>/<model>` 的格式（例如 `qwen/qwen-plus`）指定目标模型，OpenRouter 就会根据模型名称自动将请求路由到对应的 LLM 上。除此之外，其他代码与标准的 OpenAI SDK 保持一致。关于 OpenRouter 的使用方法可以参考[这里](https://openrouter.ai/qwen/qwen-plus)。

接下来介绍一下 MCP 客户端的主要代码。

### 初始化客户端类

`MCPClient` 类的初始化包含以下 3 个组件：

- 1. `self.session`：用于存储与 MCP 服务器的会话对象，初始设为 `None`，将在连接服务器时被赋值。
- 2. `self.exit_stack`：使用 `AsyncExitStack` 来管理异步资源，确保所有资源（如服务器连接、会话等）在程序结束时能够正确关闭。
- 3. `self.client`：创建 OpenAI 异步客户端，通过 OpenRouter 来访问 LLM。这里我们：
   - 设置 `base_url` 为 OpenRouter 的 API 端点。
   - 从环境变量获取 API Key（请确保设置了 `OPENROUTER_API_KEY` 环境变量）。可以参考[该文档](https://openrouter.ai/docs/api-keys)创建 OpenRouter 的 API Key。

```python
class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
```

### 服务器连接

`connect_to_server` 方法负责建立与 MCP 服务器的连接。它首先配置服务器进程的启动参数，然后通过 `stdio_client` 建立双向通信通道，最后创建并初始化会话。所有的资源管理都通过 `AsyncExitStack` 来处理，确保资源能够正确释放。连接成功后，它会打印出 MCP 服务器提供的所有可用工具。

```python
async def connect_to_server(self, server_script_path: str):
    server_params = StdioServerParameters(
        command="python",
        args=[server_script_path],
        env=None
    )
    
    stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
    self.stdio, self.write = stdio_transport
    self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
    
    await self.session.initialize()
    
    # 列出可用工具
    response = await self.session.list_tools()
    tools = response.tools
    print("\nConnected to server with tools:", [tool.name for tool in tools])
```

### 处理请求

`process_query` 方法中定义了处理请求的流程：

- 1. 首先，将用户的查询作为初始消息发送给 LLM，同时提供 MCP 服务器上所有可用工具的描述信息。
- 2. LLM 分析用户查询，决定是直接回答还是需要调用工具。如果需要工具，它会指定要调用的工具名称和参数。
- 3. 对于每个工具调用，MCP 客户端执行调用并收集结果。
- 4. 将工具调用的结果返回给 LLM，让它基于这些新信息生成或更新回答。
- 5. 如果 LLM 认为还需要更多信息，它会继续请求调用其他工具。这个过程会一直重复，直到 LLM 收集了足够的信息来完整回答用户的查询。

```python
async def process_query(self, query: str) -> str:
    """使用 LLM 和 MCP 服务器提供的工具处理查询"""
    messages = [
        {
            "role": "user",
            "content": query
        }
    ]

    response = await self.session.list_tools()
    available_tools = [{
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.inputSchema
        }
    } for tool in response.tools]

    # 初始化 LLM API 调用
    response = await self.client.chat.completions.create(
        model="qwen/qwen-plus",
        messages=messages,
        tools=available_tools
    )

 
    final_text = []
    message = response.choices[0].message
    final_text.append(message.content or "")

    # 处理响应并处理工具调用
    while message.tool_calls:
        # 处理每个工具调用
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            
            # 执行工具调用
            result = await self.session.call_tool(tool_name, tool_args)
            final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

            # 将工具调用和结果添加到消息历史
            messages.append({
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "arguments": json.dumps(tool_args)
                        }
                    }
                ]
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result.content)
            })

        # 将工具调用的结果交给 LLM
        response = await self.client.chat.completions.create(
            model="qwen/qwen-plus",
            messages=messages,
            tools=available_tools
        )
        
        message = response.choices[0].message
        if message.content:
            final_text.append(message.content)

    return "\n".join(final_text)
```

### 交互式界面

`chat_loop` 方法提供了一个简单的命令行交互界面：

- 在一个循环中持续接收用户输入，并通过前面定义地 `process_query` 方法处理查询。
- 将处理结果格式化后显示给用户。
- 通过异常处理机制优雅地处理可能出现的错误。
- 用户输入 `quit` 时安全退出程序。

```python
async def chat_loop(self):
    """运行交互式聊天循环"""
    print("\nMCP Client Started!")
    print("Type your queries or 'quit' to exit.")
    
    while True:
        try:
            query = input("\nQuery: ").strip()
            if query.lower() == 'quit':
                break
            response = await self.process_query(query)
            print("\n" + response)
        except Exception as e:
            print(f"\nError: {str(e)}")
```

### 程序入口

程序入口代码完成以下工作：

- 检查命令行参数，确保用户提供了服务器脚本的路径。
- 创建 `MCPClient` 实例并连接到服务器。
- 启动交互式聊天循环。
- 使用 `try-finally` 结构确保在程序退出时正确清理资源。
- 通过 `asyncio.run()` 运行异步主函数。

```python
async def main():
    if len(sys.argv) < 2:
        print("Usage: uv run client.py <path_to_server_script>")
        sys.exit(1)
        
    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

### 运行程序

使用以下命令运行 MCP 客户端：

```bash
uv run client.py <MCP 服务器的代码路径>
```

启动 MCP 客户端后，我们输入问题 `Elasticsearch 集群中有哪些索引?`，可以看到 MCP 客户端成功调用了 MCP 服务器提供的 `list_indices` 从 Elasticsearch 集群中获取到了索引信息。


```bash
2025-02-03 17:13:56,518 - mcp.server.lowlevel.server - INFO - Processing request of type ListToolsRequest

Connected to server with tools: ['list_indices', 'get_index', 'write_documents']

MCP Client Started!
Type your queries or 'quit' to exit.

Query:  Elasticsearch 集群中有哪些索引?
2025-02-03 17:14:04,537 - mcp.server.lowlevel.server - INFO - Processing request of type ListToolsRequest
2025-02-03 17:14:06,185 - mcp.server.lowlevel.server - INFO - Processing request of type CallToolRequest
2025-02-03 17:14:06,248 - elastic_transport.transport - INFO - GET https://localhost:9200/_cat/indices?format=json [status:200 duration:0.062s]
2025-02-03 17:14:06,248 - mcp.server.lowlevel.server - INFO - Warning: InsecureRequestWarning: Unverified HTTPS request is being made to host 'localhost'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings


[Calling tool list_indices with args {}]
在Elasticsearch集群中有以下索引:

1. 索引名称: student
   - 健康状态: green
   - 状态: open
   - UUID: iKl3j9ujSJ2i0GF5v8NUDw
   - 主分片数: 1
   - 副本分片数: 1
   - 文档数量: 3
   - 删除的文档数量: 0
   - 存储大小: 12kb
   - 主分片存储大小: 6kb

2. 索引名称: teacher
   - 健康状态: green
   - 状态: open
   - UUID: vfbwvH7yQGWqRGEG-t4FnA
   - 主分片数: 1
   - 副本分片数: 1
   - 文档数量: 3
   - 删除的文档数量: 0
   - 存储大小: 22.6kb
   - 主分片存储大小: 11.3kb

3. 索引名称: movies
   - 健康状态: green
   - 状态: open
   - UUID: JYhacHmXREWmkvwXBaFPmg
   - 主分片数: 1
   - 副本分片数: 1
   - 文档数量: 3
   - 删除的文档数量: 0
   - 存储大小: 13.2kb
   - 主分片存储大小: 6.6kb
```

## 总结

本文介绍了如何使用 MCP Python SDK 编写一个 MCP 客户端，并集成 LLM 来实现灵活的工具调用和数据处理。通过简单的示例和进阶示例，展示了如何通过标准输入输出（stdio）方式与 MCP 服务器建立连接，并集成 LLM（如通义千问）来实现更复杂的应用场景。

## 参考资料

- For Client Developers：https://modelcontextprotocol.io/quickstart/client
- https://github.com/modelcontextprotocol/python-sdk：https://github.com/modelcontextprotocol/python-sdk
