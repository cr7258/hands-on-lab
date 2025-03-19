# Create server parameters for stdio connection
from os import getenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

from langchain_openai import ChatOpenAI
import asyncio

model = ChatOpenAI(
  openai_api_key=getenv("OPENROUTER_API_KEY"),
  openai_api_base="https://openrouter.ai/api/v1",
  model_name="openai/gpt-4o",
)

async def main():
    server_params = StdioServerParameters(
        command="python",
        # Make sure to update to the full absolute path to your math_server.py file
        args=["./math_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # Get tools
            tools = await load_mcp_tools(session)

            # Create and run the agent
            agent = create_react_agent(model, tools)
            agent_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
            print(agent_response)

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())

# {
#   'messages': [
#     HumanMessage(content="what's (3 + 5) x 12?",
#     additional_kwargs={
      
#     },
#     response_metadata={
      
#     },
#     id='b8afa658-7e31-4afb-86e4-938ca7cd65ab'),
#     AIMessage(content='',
#     additional_kwargs={
#       'tool_calls': [
#         {
#           'id': 'call_kcHyOJBKkMbMMjSmjXIB4Fp8',
#           'function': {
#             'arguments': '{
#               "a": 3,
#               "b": 5
#             }',
#             'name': 'add'
#           },
#           'type': 'function',
#           'index': 0
#         },
#         {
#           'id': 'call_RSTMCjgILiysFlBjMScn4KMK',
#           'function': {
#             'arguments': '{
#               "a": 8,
#               "b": 12
#             }',
#             'name': 'multiply'
#           },
#           'type': 'function',
#           'index': 1
#         }
#       ],
#       'refusal': None
#     },
#     response_metadata={
#       'token_usage': {
#         'completion_tokens': 51,
#         'prompt_tokens': 77,
#         'total_tokens': 128,
#         'completion_tokens_details': None,
#         'prompt_tokens_details': None
#       },
#       'model_name': 'openai/gpt-4o',
#       'system_fingerprint': 'fp_90d33c15d4',
#       'id': 'gen-1742309053-tnsXgIJwtt96USzSy3dW',
#       'finish_reason': 'tool_calls',
#       'logprobs': None
#     },
#     id='run-b271e9d9-e21a-488a-b7ca-1cee13fe659c-0',
#     tool_calls=[
#       {
#         'name': 'add',
#         'args': {
#           'a': 3,
#           'b': 5
#         },
#         'id': 'call_kcHyOJBKkMbMMjSmjXIB4Fp8',
#         'type': 'tool_call'
#       },
#       {
#         'name': 'multiply',
#         'args': {
#           'a': 8,
#           'b': 12
#         },
#         'id': 'call_RSTMCjgILiysFlBjMScn4KMK',
#         'type': 'tool_call'
#       }
#     ],
#     usage_metadata={
#       'input_tokens': 77,
#       'output_tokens': 51,
#       'total_tokens': 128,
#       'input_token_details': {
        
#       },
#       'output_token_details': {
        
#       }
#     }),
#     ToolMessage(content='8',
#     name='add',
#     id='a7ebb896-79f4-4370-8af8-aae3846edee5',
#     tool_call_id='call_kcHyOJBKkMbMMjSmjXIB4Fp8'),
#     ToolMessage(content='96',
#     name='multiply',
#     id='18c39741-f98b-4b77-a4c8-ca9360edd766',
#     tool_call_id='call_RSTMCjgILiysFlBjMScn4KMK'),
#     AIMessage(content='Theresultof\\((3+5)\\times12\\)is96.',
#     additional_kwargs={
#       'refusal': None
#     },
#     response_metadata={
#       'token_usage': {
#         'completion_tokens': 22,
#         'prompt_tokens': 143,
#         'total_tokens': 165,
#         'completion_tokens_details': None,
#         'prompt_tokens_details': None
#       },
#       'model_name': 'openai/gpt-4o',
#       'system_fingerprint': 'fp_90d33c15d4',
#       'id': 'gen-1742309054-iy7qymFg410pgijca0XW',
#       'finish_reason': 'stop',
#       'logprobs': None
#     },
#     id='run-a0e792bb-14ef-470f-a1fb-02f2ab278671-0',
#     usage_metadata={
#       'input_tokens': 143,
#       'output_tokens': 22,
#       'total_tokens': 165,
#       'input_token_details': {
        
#       },
#       'output_token_details': {
        
#       }
#     })
#   ]
# }