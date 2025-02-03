from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import sys

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="python",
    args=[sys.argv[1]],
    env=None # Optional environment variables
)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print("Tools:", tools)

            # Call a tool
            indices = await session.call_tool("list_indices")
            print("Indices:", indices)

# uv run simple.py ../../server/elasticsearch-mcp-server-example/server.py
if __name__ == "__main__":
    import asyncio
    asyncio.run(run())