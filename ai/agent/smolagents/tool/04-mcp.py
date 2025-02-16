from smolagents import ToolCollection, CodeAgent, HfApiModel
from mcp import StdioServerParameters
from dotenv import load_dotenv
import os


# Load environment variables from .env
load_dotenv()

server_parameters = StdioServerParameters(
    command="/Users/I576375/Code/hands-on-lab/ai/agent/smolagents/tool/.venv/bin/python",
    args=["../../../claude/mcp/server/elasticsearch-mcp-server-example/server.py"],
    env={
        "ELASTIC_HOST": os.getenv("ELASTIC_HOST"),
        "ELASTIC_USERNAME": os.getenv("ELASTIC_USERNAME"),
        "ELASTIC_PASSWORD": os.getenv("ELASTIC_PASSWORD"),
    }
)

# You can choose to not pass any model_id to HfApiModel to use a default free model
model = HfApiModel(token=os.getenv("HUGGINGFACE_API_TOKEN"))

with ToolCollection.from_mcp(server_parameters) as tool_collection:
    agent = CodeAgent(tools=[*tool_collection.tools], model=model, add_base_tools=True)
    agent.run("How many indicies in the Elasticsearch cluster?")