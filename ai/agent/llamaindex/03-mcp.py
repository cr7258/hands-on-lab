from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import ReActAgent
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI
import os
import asyncio


hf_token = os.getenv("HUGGINGFACE_API_TOKEN")

llm = HuggingFaceInferenceAPI(
    model_name="Qwen/Qwen2.5-Coder-32B-Instruct",
    temperature=0.7,
    max_tokens=100,
    token=hf_token,
)

async def main():
    # We consider there is a mcp server running on 127.0.0.1:18000, or you can use the mcp client to connect to your own mcp server.
    mcp_client = BasicMCPClient("http://127.0.0.1:18000/user/sse")
    mcp_tool_spec = McpToolSpec(client=mcp_client)
    
    # Get tools asynchronously
    tools = await mcp_tool_spec.to_tool_list_async()
    
    # Print detailed information about each tool
    for i, tool in enumerate(tools):
        print(f"Tool {i+1}:")
        print(f"  Name: {tool.metadata.name}")
        print(f"  Description: {tool.metadata.description}")
        print(f"  Type: {type(tool).__name__}")
    #Tool 1:
    #   Name: get-user
    #   Description: Get random user information
    #   Type: FunctionTool

    # Create a FunctionAgent with the tools
    agent = ReActAgent(
        name="UserInfoAgent",
        description="An agent that can get random user information",
        llm=llm,
        tools=tools,
    )
    
    # Run the agent
    resp = await agent.run("Get a random user information.")
    print(resp)
# Here is the random user information:

# - **Name**: Alberto Pinto
# - **Email**: alberto.pinto@example.com
# - **Location**: Rio Verde, Brazil
# - **Phone**: (82) 7981-4983

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())