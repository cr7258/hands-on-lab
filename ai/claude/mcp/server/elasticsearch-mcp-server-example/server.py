import os
import subprocess
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from elasticsearch import Elasticsearch
import logging
import warnings
from typing import List, Dict

MCP_SERVER_NAME = "elasticsearch-mcp-server"

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

@mcp.resource("es://logs")
def get_logs() -> str:
    """Get Elasticsearch container logs"""
    result = subprocess.run(["docker", "logs", "elasticsearch-mcp-server-example-es01-1"], capture_output=True, text=True, check=True)
    return result.stdout

@mcp.resource("file://docker-compose.yaml")
def get_file() -> str:
    """Return the contents of docker-compose.yaml file"""
    with open("docker-compose.yaml", "r") as f:
        return f.read()

@mcp.resource("file://movies.csv")
def get_movies() -> str:
    """Return the contents of movies.csv file"""
    with open("movies.csv", "r") as f:
        return f.read()

@mcp.tool()
def write_documents(index: str, documents: List[Dict]) -> dict:
    """Write multiple documents to an Elasticsearch index using bulk API
    
    Args:
        index: Name of the index to write to
        documents: List of documents to write
        
    Returns:
        Bulk operation response from Elasticsearch
    """
    operations = []
    for doc in documents:
        # Add index operation
        operations.append({"index": {"_index": index}})
        # Add document
        operations.append(doc)
    
    return es.bulk(operations=operations, refresh=True)

@mcp.prompt()
def es_prompt(index: str) -> str:
    """Create a prompt for index analysis"""
    return f"""You are an elite Elasticsearch expert with deep knowledge of search engine architecture, data indexing strategies, and performance optimization. Please analyze the index '{index}' considering:
- Index settings and mappings
- Search optimization opportunities
- Data modeling improvements
- Potential scaling considerations
"""

if __name__ == "__main__":
    mcp.run()
