import os
import subprocess
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
from elasticsearch import Elasticsearch
import logging
import warnings
from typing import List, Dict
import uvicorn

MCP_SERVER_NAME = "elasticsearch-mcp-sse"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(MCP_SERVER_NAME)

def create_elasticsearch_client() -> Elasticsearch:
    # Load environment variables from .env file
    load_dotenv()

    url = os.getenv("ELASTIC_HOST")
    username = os.getenv("ELASTIC_USERNAME")
    password = os.getenv("ELASTIC_PASSWORD")

    # Disable SSL warnings
    warnings.filterwarnings("ignore", message=".*TLS with verify_certs=False is insecure.*",)
    
    if username and password:
        return Elasticsearch(url, basic_auth=(username, password), verify_certs=False)
    return Elasticsearch(url)

es = create_elasticsearch_client()
mcp = FastMCP(MCP_SERVER_NAME)

@mcp.tool()
def list_indices() -> dict:
    """List all Elasticsearch indices"""
    return es.cat.indices(format="json")
 
@mcp.tool()
def get_index(index: str) -> dict:
    """Get detailed information about a specific Elasticsearch index"""
    return es.indices.get(index=index)

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

if __name__ == "__main__":
    mcp_server = mcp._mcp_server

    import argparse
    
    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    args = parser.parse_args()

    # Bind SSE request handling to MCP server
    starlette_app = create_starlette_app(mcp_server, debug=True)

    uvicorn.run(starlette_app, host=args.host, port=args.port)
