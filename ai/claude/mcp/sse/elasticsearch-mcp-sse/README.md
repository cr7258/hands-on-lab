# 构建基于 SSE 协议通信的 MCP Server 和 Client

在之前的系列教程中，我们编写的 MCP 服务器与 MCP 客户端是通过 **stdio（Standard Input/Output，标准输入输出）**来进行交互的。客户端通过启动服务器子进程，并利用标准输入（stdin）和标准输出（stdout）建立双向通信。这种模式导致 MCP 客户端与服务器之间存在强耦合，且每个服务器进程只能与启动它的客户端通信（1:1 的关系）。

为了解耦 MCP 客户端与服务器，本文将演示如何使用 **SSE（Server-Sent Events，服务器发送事件）**协议进行通信，使服务器能够作为一个独立运行的进程，支持多个客户端的灵活连接、使用和断开。换句话说，基于 SSE 的服务器和客户端可以是完全解耦的进程，甚至运行在不同的节点上，从而提供更高的灵活性和扩展性。

本文使用到的所有代码可以在 Github 上找到：https://github.com/cr7258/hands-on-lab/tree/main/ai/claude/mcp/sse/elasticsearch-mcp-sse

MCP 系列文章：

- [一文带你入门 MCP（模型上下文协议）](https://mp.weixin.qq.com/s/rcOi7e8F5qGVVF2noCk46Q)
- [MCP Server 开发实战：无缝对接 LLM 和 Elasticsearch](https://mp.weixin.qq.com/s/38HiPOOKVKz3C76d_SGkmw)
- [快速上手：实现你的第一个 MCP Client](https://mp.weixin.qq.com/s/yLuNixOVBlSNGkGHik-XaA)
- 构建基于 SSE 协议通信的 MCP Server 和 Client（本文）


## 什么是 SSE？

Server-Sent Events（SSE，服务器发送事件）是一种基于 HTTP 协议的技术，允许服务器向客户端**单向、实时地推送数据**。在 SSE 模式下，客户端通过创建一个 `EventSource` 对象与服务器建立持久连接，服务器则通过该连接持续发送数据流，而无需客户端反复发送请求。

**SSE 的主要特点包括：**

- **单向通信**：服务器主动向客户端推送数据，客户端无法通过同一连接向服务器发送数据。
- **基于 HTTP 协议**：利用现有的 HTTP 协议，无需额外的协议支持，易于实现和部署。
- **轻量级**：实现简单，适用于需要实时更新的应用场景，如新闻推送、股票行情等。
- **自动重连**：客户端在连接断开时会自动尝试重新连接，确保数据传输的连续性。

需要注意的是，SSE 仅支持服务器到客户端的单向通信，若应用场景需要双向实时通信，可能需要考虑使用 WebSocket 等其他技术。

## 环境准备

在本教程中，我们将使用 [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) 来编写项目，使用 [uv](https://docs.astral.sh/uv/) 来管理 Python 项目依赖。

```bash
uv add "mcp[cli]" elasticsearch python-dotenv uvicorn openai
```

实验用到的 Elasticsearch 集群可以通过 Github 中的 `docker-compose.yaml` 文件启动：

```bash
docker-compose up -d
```
浏览器输入 http://localhost:5601 访问 Kibana 界面，用户名 `elastic`，密码 `test123`。

在 `.env` 文件中设置好 Elasticsearch 的连接信息。

```bash
ELASTIC_HOST=https://localhost:9200
ELASTIC_USERNAME=elastic
ELASTIC_PASSWORD=test123
```

## 准备测试数据

在 Kibana 中打开 `Management -> Dev Tools` 页面， 执行以下代码创建两个索引 `student` 和 `teacher`，分别插入几条数据：

```json
POST /student/_doc
{
  "name": "Alice",
  "age": 20,
  "major": "Computer Science"
}

POST /student/_doc
{
  "name": "Bob",
  "age": 22,
  "major": "Mathematics"
}

POST /student/_doc
{
  "name": "Carol",
  "age": 21,
  "major": "Physics"
}

POST /teacher/_doc
{
  "name": "Tom",
  "subject": "English",
  "yearsOfExperience": 10
}

POST /teacher/_doc
{
  "name": "John",
  "subject": "History",
  "yearsOfExperience": 7
}

POST /teacher/_doc
{
  "name": "Lily",
  "subject": "Mathematics",
  "yearsOfExperience": 5
}
```

## 实现基于 SSE 协议的 MCP Server

MCP 服务器部分的代码与[MCP Server 开发实战：无缝对接 LLM 和 Elasticsearch](https://mp.weixin.qq.com/s/38HiPOOKVKz3C76d_SGkmw)一文中介绍的内容相同，因此在此不再赘述，读者可参阅该文章以获取详细信息。 

这里重点说明一下如何让 MCP 服务器运行在 SSE 协议之上。在本教程中，我们使用 Starlette 框架来实现 SSE 服务器，代码主要分为以下几个部分：

1. **SSE 传输对象的初始化**  
   在函数开始处，通过创建 `SseServerTransport` 对象，并指定基础路径 `/messages/`，用于后续管理 SSE 连接和消息传递。

2. **定义 SSE 连接处理函数**  
   - **handle_sse 函数**：这是一个异步请求处理函数，当客户端请求建立 SSE 连接时会被调用。  
   - **连接过程**：  
       利用 `sse.connect_sse` 方法，传入当前请求的 `scope`、`receive` 方法和 `_send` 方法，建立一个异步上下文管理器。  
       管理器返回两个数据流：`read_stream` 用于读取客户端发送的数据，`write_stream` 用于向客户端发送数据。  
   - **启动 MCP 服务器**：在成功建立连接后，调用 `mcp_server.run` 方法，并传入读取、写入流以及由 `mcp_server.create_initialization_options()` 生成的初始化参数。这一过程实现了 MCP 服务器与客户端之间的实时数据交互。

3. **Starlette 应用及路由配置**  
   - **Starlette 实例化**：函数返回一个新的 Starlette 应用实例，其调试模式根据传入的 `debug` 参数设置。  
   - **路由设置**：  
       使用 `Route("/sse", endpoint=handle_sse)` 定义 `/sse` 路径，当客户端访问此路径时将触发 `handle_sse` 函数处理 SSE 连接。  
       使用 `Mount("/messages/", app=sse.handle_post_message)` 将 `/messages/` 路径挂载到 `sse.handle_post_message` 应用上，用于处理通过 POST 请求发送的消息，实现与 SSE 长连接的消息传递功能。

```python
def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can server the provied mcp server with SSE."""
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

接下来就是创建 MCP 服务器实例，然后通过上面定义的 `create_starlette_app` 方法创建 Starlette 应用，最后使用 uvicorn 启动 ASGI 服务器，实现实时的 SSE 数据传输。

```python
if __name__ == "__main__":
    mcp_server = mcp._mcp_server

    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=18080, help='Port to listen on')
    args = parser.parse_args()

    # Bind SSE request handling to MCP server
    starlette_app = create_starlette_app(mcp_server, debug=True)

    uvicorn.run(starlette_app, host=args.host, port=args.port)
```

## 启动 MCP 服务器

执行以下命令可以启动 MCP 服务器，默认监听在 18080 端口。

```bash
uv run server.py

# 输出
INFO:     Started server process [82035]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:18080 (Press CTRL+C to quit)
```

## 实现基于 SSE 协议的 MCP Client

MCP 客户端部分的代码可以参考[快速上手：实现你的第一个 MCP Client](https://mp.weixin.qq.com/s/yLuNixOVBlSNGkGHik-XaA)一文，这里不再重复说明。

唯一的区别就是在连接 MCP 服务器的时候通过 SSE 协议进行交互。以下是具体的代码：

```python
async def connect_to_sse_server(self, server_url: str):
    """Connect to an MCP server running with SSE transport"""
    # 创建 SSE 客户端连接上下文管理器
    self._streams_context = sse_client(url=server_url)
    # 异步初始化 SSE 连接，获取数据流对象
    streams = await self._streams_context.__aenter__()

    # 使用数据流创建 MCP 客户端会话上下文
    self._session_context = ClientSession(*streams)
    # 初始化客户端会话对象
    self.session: ClientSession = await self._session_context.__aenter__()

    # 执行 MCP 协议初始化握手
    await self.session.initialize()
```

## 启动 MCP 客户端

执行以下命令启动 MCP 客户端并连接 MCP 服务器。

```bash
uv run client.py http://localhost:18080/sse
```

启动 MCP 客户端后，我们输入问题 `Elasticsearch 集群中有哪些索引?`，可以看到 MCP 客户端成功调用了 MCP 服务器提供的 `list_indices` 从 Elasticsearch 集群中获取到了索引信息。

```bash
Initialized SSE client...
Listing tools...

Connected to server with tools: ['list_indices', 'get_index']

MCP Client Started!
Type your queries or 'quit' to exit.

Query: 集群中有哪些索引?


[Calling tool list_indices with args {}]
在集群中,有以下索引:

1. 索引名称: student
   - 健康状况: green
   - 状态: open
   - UUID: gPUyqTHZQ12rSTEYX-Ho3w
   - 主分片数: 1
   - 副本分片数: 1
   - 文档数量: 3
   - 已删除的文档数量: 0
   - 存储大小: 12kb
   - 主分片的存储大小: 6kb

2. 索引名称: teacher
   - 健康状况: green
   - 状态: open
   - UUID: ygkfkvjJSMaB946myzanNg
   - 主分片数: 1
   - 副本分片数: 1
   - 文档数量: 3
   - 已删除的文档数量: 0
   - 存储大小: 22.6kb
   - 主分片的存储大小: 6kb
```

## 总结

本文介绍了如何利用 Server-Sent Events（SSE）协议，实现 MCP 服务器与客户端之间的解耦通信。通过采用 SSE，服务器能够作为独立进程运行，支持多个客户端的灵活连接与断开，从而提升系统的灵活性和可扩展性。
