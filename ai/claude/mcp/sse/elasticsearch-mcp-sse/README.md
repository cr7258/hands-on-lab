# 构建基于 SSE 的 MCP Server：实现实时数据流与 LLM 交互

在本教程中，我们将探讨如何使用 Server-Sent Events (SSE) 构建一个 MCP Server。我们将以 Elasticsearch 集成为例，展示如何实现基于 SSE 的实时数据流通信。

## 什么是 SSE Transport？

Server-Sent Events (SSE) 是一种服务器推送技术，允许服务器向客户端实时推送数据。在 MCP 中，SSE transport 提供了以下优势：

1. 服务器到客户端的实时数据流
2. 基于标准 HTTP 协议，易于实现和维护
3. 支持自动重连机制
4. 适用于需要实时更新的场景

## 项目结构

首先，让我们看看项目的基本结构：

```
elasticsearch-mcp-sse/
├── pyproject.toml    # 项目依赖配置
├── server.py         # MCP Server 实现
└── README.md         # 项目文档
```

## 环境准备

1. 安装必要的依赖：

```bash
pip install "mcp[cli]" elasticsearch python-dotenv starlette uvicorn
```

2. 配置环境变量：

创建 `.env` 文件：

```bash
ELASTIC_HOST=https://localhost:9200
ELASTIC_USERNAME=elastic
ELASTIC_PASSWORD=your_password
```

## 实现 SSE-based MCP Server

### 1. 基础设置

首先，我们需要导入必要的模块并进行基本配置：

```python
import os
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
import uvicorn

MCP_SERVER_NAME = "elasticsearch-mcp-sse"

# 配置日志
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

### 2. 创建 Elasticsearch 客户端

实现与 Elasticsearch 的连接：

```python
def create_elasticsearch_client() -> Elasticsearch:
    load_dotenv()
    url = os.getenv("ELASTIC_HOST")
    username = os.getenv("ELASTIC_USERNAME")
    password = os.getenv("ELASTIC_PASSWORD")
    
    warnings.filterwarnings("ignore", message=".*TLS with verify_certs=False is insecure.*",)
    
    if username and password:
        return Elasticsearch(url, basic_auth=(username, password), verify_certs=False)
    return Elasticsearch(url)

es = create_elasticsearch_client()
```

### 3. 定义 MCP 工具

使用 FastMCP 创建工具函数：

```python
mcp = FastMCP(MCP_SERVER_NAME)

@mcp.tool()
def list_indices() -> dict:
    """List all Elasticsearch indices"""
    return es.cat.indices(format="json")
 
@mcp.tool()
def get_index(index: str) -> dict:
    """Get detailed information about a specific Elasticsearch index"""
    return es.indices.get(index=index)
```

### 4. 实现 SSE Transport

这是本教程的核心部分，我们使用 Starlette 框架来实现 SSE transport：

```python
def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can serve the provided mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )
```

这段代码实现了：
- `/sse` 端点用于建立 SSE 连接
- `/messages/` 端点处理客户端到服务器的通信
- 使用 `SseServerTransport` 管理 SSE 连接
- 通过 `connect_sse` 建立双向通信通道

### 5. 启动服务器

最后，实现服务器启动逻辑：

```python
if __name__ == "__main__":
    mcp_server = mcp._mcp_server
    
    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    args = parser.parse_args()

    starlette_app = create_starlette_app(mcp_server, debug=True)
    uvicorn.run(starlette_app, host=args.host, port=args.port)
```

## SSE Transport 工作原理

1. **连接建立**：
   - 客户端通过 HTTP GET 请求连接到 `/sse` 端点
   - 服务器保持连接打开，设置适当的 SSE headers

2. **数据流**：
   - 服务器通过 SSE 连接推送数据到客户端
   - 客户端通过 POST 请求发送数据到 `/messages/` 端点

3. **事件处理**：
   - `SseServerTransport` 管理事件流
   - 自动处理重连和错误情况

## 实现 MCP SSE Client

在这一部分，我们将实现一个基于 SSE 的 MCP 客户端，它能够连接到我们的 MCP Server 并进行实时通信。这个客户端将展示如何：
- 建立和维护 SSE 连接
- 处理与 LLM 的交互
- 执行服务器端工具调用
- 管理异步通信流程

### 1. 客户端基础结构

首先，我们需要创建一个 `MCPClient` 类来管理与服务器的连接和通信。这个类将作为我们客户端的核心，负责：
- 维护与 MCP 服务器的会话状态
- 处理与 OpenAI API 的交互
- 管理异步上下文和资源清理
- 提供统一的查询处理接口

以下是基础类的实现：

```python
class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
```

### 2. 建立 SSE 连接

SSE 连接是客户端与服务器之间的核心通信桥梁。这个方法实现了：
- 使用 MCP 的 SSE client 创建持久连接
- 管理异步上下文和资源生命周期
- 初始化客户端会话
- 验证连接并获取可用工具列表

这个实现确保了连接的可靠性和资源的正确管理：

```python
async def connect_to_sse_server(self, server_url: str):
    """Connect to an MCP server running with SSE transport"""
    # Store the context managers so they stay alive
    self._streams_context = sse_client(url=server_url)
    streams = await self._streams_context.__aenter__()

    self._session_context = ClientSession(*streams)
    self.session: ClientSession = await self._session_context.__aenter__()

    # Initialize
    await self.session.initialize()

    # List available tools to verify connection
    print("Initialized SSE client...")
    print("Listing tools...")
    response = await self.session.list_tools()
    tools = response.tools
    print("\nConnected to server with tools:", [tool.name for tool in tools])
```

### 3. 查询处理

查询处理是客户端的核心功能，它实现了一个复杂的工作流程：
1. 构建初始查询消息
2. 获取并格式化可用工具信息
3. 与 OpenAI API 交互获取响应
4. 处理工具调用和结果
5. 维护对话上下文
6. 生成最终响应

这个实现展示了如何处理多轮对话和工具调用：

```python
async def process_query(self, query: str) -> str:
    """Process a query using OpenAI and available tools"""
    messages = [
        {
            "role": "user",
            "content": query
        }
    ]

    # 获取可用工具列表
    response = await self.session.list_tools()
    available_tools = [{
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.inputSchema
        }
    } for tool in response.tools]

    # 调用 OpenAI API
    response = await self.client.chat.completions.create(
        model="qwen/qwen-plus",
        messages=messages,
        tools=available_tools
    )
    
    # 处理响应和工具调用
    tool_results = []
    final_text = []

    message = response.choices[0].message
    final_text.append(message.content or "")

    # 处理工具调用循环
    while message.tool_calls:
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            
            # 执行工具调用
            result = await self.session.call_tool(tool_name, tool_args)
            tool_results.append({"call": tool_name, "result": result})
            final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

            # 更新消息历史
            messages.extend([
                {
                    "role": "assistant",
                    "tool_calls": [{
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "arguments": json.dumps(tool_args)
                        }
                    }]
                },
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result.content)
                }
            ])

        # 获取下一个 OpenAI 响应
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

### 4. 交互式聊天循环

交互式聊天循环提供了一个用户友好的命令行界面，它实现了：
- 持续的用户输入处理
- 优雅的错误处理和异常捕获
- 清晰的用户提示和反馈
- 简单的退出机制

这个实现让用户能够方便地与系统进行交互：

```python
async def chat_loop(self):
    """Run an interactive chat loop"""
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

### 5. 资源清理

资源清理是确保系统稳定性和可靠性的关键部分。这个方法：
- 正确关闭所有打开的连接
- 清理异步上下文
- 释放系统资源
- 防止资源泄漏

通过实现完善的清理机制，确保系统的健壮性：

```python
async def cleanup(self):
    """Properly clean up the session and streams"""
    if self._session_context:
        await self._session_context.__aexit__(None, None, None)
    if self._streams_context:
        await self._streams_context.__aexit__(None, None, None)
```

### 6. 运行客户端

主程序实现了完整的客户端启动流程，包括：
- 命令行参数解析
- 客户端实例化
- 连接建立
- 错误处理
- 资源清理

这个实现确保了程序的可靠运行和优雅退出：

```python
async def main():
    if len(sys.argv) < 2:
        print("Usage: uv run client.py <URL of SSE MCP server>")
        sys.exit(1)
        
    client = MCPClient()
    try:
        await client.connect_to_sse_server(server_url=sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

### 使用方法

在运行客户端之前，需要完成以下准备工作：

1. 确保 MCP Server 已经启动并正常运行
   - 检查服务器日志确认启动成功
   - 验证服务器端口可访问

2. 配置必要的环境变量
   - 设置 `OPENROUTER_API_KEY` 用于 OpenAI API 访问
   - 确保环境变量正确加载

3. 运行客户端：
```bash
python client.py http://localhost:8080/sse
```

客户端启动后的工作流程：
1. 连接到服务器并获取可用工具列表
2. 等待用户输入查询
3. 处理查询并显示结果：
   - 调用 OpenAI API 进行处理
   - 执行必要的工具调用
   - 展示最终结果
4. 重复步骤 2-3 直到用户选择退出

要退出客户端，只需输入 "quit"。

## 最佳实践

1. **错误处理**：
   ```python
   try:
       async with sse.connect_sse(...) as (read_stream, write_stream):
           await mcp_server.run(...)
   except Exception as e:
       logger.error(f"SSE connection error: {e}")
   ```

2. **心跳机制**：
   - 定期发送心跳消息保持连接
   - 监控连接状态

3. **重连策略**：
   - 实现指数退避重连
   - 设置最大重试次数

## 性能考虑

1. **连接管理**：
   - 适当设置连接超时
   - 监控活动连接数

2. **资源使用**：
   - 控制并发连接数
   - 合理设置缓冲区大小

## 调试技巧

1. 使用浏览器开发工具监控 SSE 连接
2. 启用详细日志记录
3. 使用工具如 `curl` 测试 SSE 端点

## 总结

SSE transport 为 MCP Server 提供了强大的实时通信能力。通过本教程，我们展示了如何：

1. 使用 Starlette 实现 SSE transport
2. 集成 Elasticsearch 功能
3. 处理实时数据流
4. 实现可靠的错误处理

这种实现方式特别适合需要实时数据流的 LLM 应用场景，提供了更好的用户体验和更强的实时性。

## 参考资料

- [MCP Transports Documentation](https://modelcontextprotocol.io/docs/concepts/transports)
- [Python SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [Starlette Documentation](https://www.starlette.io/)