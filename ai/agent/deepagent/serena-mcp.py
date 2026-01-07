"""
Deep Agents + Serena MCP Integration Demo

Uses langchain-mcp-adapters with proper session management.

Usage:
    export OPENROUTER_API_KEY="your-openrouter-api-key"
    export SERENA_SERVER_PATH="/path/to/serena"  # or use uvx
    uv run serena-mcp.py /path/to/repo "Analyze this project"
"""

import asyncio
import os
import sys
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

# MCP client
from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools


SYSTEM_PROMPT = """You are a code analysis assistant using Serena's semantic code tools via MCP.

Serena provides IDE-like capabilities:
- find_symbol: Find code symbols by name
- find_referencing_symbols: Find where a symbol is used  
- read_file: Read file content
- get_symbols_overview: Get all symbols in a file
- search_for_pattern: Search patterns in codebase

Use these tools to analyze and understand the codebase efficiently.
"""


model = ChatOpenAI(
    model="openai/gpt-4o",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)


async def main():
    if len(sys.argv) < 2:
        print("Usage: uv run serena-mcp.py <repo_path> [query]")
        print()
        print("Examples:")
        print('  uv run serena-mcp.py . "Analyze the project architecture"')
        print('  uv run serena-mcp.py ./my-project "Find all API handlers"')
        sys.exit(1)

    repo_path = os.path.abspath(sys.argv[1])
    query = sys.argv[2] if len(sys.argv) > 2 else "Analyze the architecture of this codebase"

    if not Path(repo_path).exists():
        print(f"Error: Path '{repo_path}' does not exist")
        sys.exit(1)

    print("=" * 60)
    print("Deep Agent + Serena MCP")
    print("=" * 60)
    print(f"Repository: {repo_path}")
    print(f"Query: {query}")
    print("=" * 60)
    print()

    # Configure Serena MCP server via stdio
    # Using uvx to run directly from GitHub
    server_params = StdioServerParameters(
        command="uvx",
        args=[
            "--from", "git+https://github.com/oraios/serena",
            "serena", "start-mcp-server",
            "--project", repo_path,
        ],
    )

    print("[DEBUG] Connecting to Serena MCP server...")
    
    # Key: Keep the session alive while using the agent!
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the MCP connection
            print("[DEBUG] Initializing MCP session...")
            await session.initialize()

            # Load tools from the session
            print("[DEBUG] Loading MCP tools...")
            tools = await load_mcp_tools(session)
            print(f"[DEBUG] Loaded {len(tools)} tools")
            
            for tool in tools:
                print(f"  - {tool.name}")

            # Create agent with Serena tools
            agent = create_agent(model, tools)

            print()
            print("[DEBUG] Calling agent.ainvoke()...")
            result = await agent.ainvoke({
                "messages": [{"role": "user", "content": query}]
            })
            print("[DEBUG] agent.ainvoke() completed")

            print("=" * 60)
            print("Result:")
            print("=" * 60)
            print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
