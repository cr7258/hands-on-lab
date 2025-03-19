from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
import asyncio
from os import getenv

from langchain_openai import ChatOpenAI
model = ChatOpenAI(
  openai_api_key=getenv("OPENROUTER_API_KEY"),
  openai_api_base="https://openrouter.ai/api/v1",
  model_name="openai/gpt-4o",
)


async def main():
    async with MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                # Make sure to update to the full absolute path to your math_server.py file
                "args": ["./math_server.py"],
                "transport": "stdio",
            },
            "weather": {
                # make sure you start your weather server on port 8000
                "url": "http://localhost:8000/sse",
                "transport": "sse",
            }
        }
    ) as client:
        agent = create_react_agent(model, client.get_tools())
        math_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
        weather_response = await agent.ainvoke({"messages": "what is the weather in nyc?"})

        # Extract the final answer from the math response
        math_final_answer = math_response['messages'][-1].content if math_response['messages'][-1].content else "No final answer found"
        print(f"Math answer: {math_final_answer}")
        
        # Extract the final answer from the weather response
        weather_final_answer = weather_response['messages'][-1].content if weather_response['messages'][-1].content else "No final answer found"
        print(f"Weather answer: {weather_final_answer}")

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())

# Math answer: The result of \((3 + 5) \times 12\) is 96.
# Weather answer: The weather in New York City is currently sunny.