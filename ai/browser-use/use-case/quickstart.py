from langchain_openai import ChatOpenAI
from browser_use import Agent
from os import getenv
import asyncio

llm = ChatOpenAI(
  openai_api_key=getenv("OPENROUTER_API_KEY"),
  openai_api_base="https://openrouter.ai/api/v1",
  model_name="openai/gpt-4o",
)

async def main():
    agent = Agent(
        task="Compare the price of Qwen and DeepSeek-V3",
        llm=llm,
    )
    result = await agent.run()
    print(result)

asyncio.run(main())

# INFO     [agent] 🚀 Starting task: Compare the price of Qwen and DeepSeek-V3
# INFO     [agent] 📍 Step 1
# INFO     [agent] 🤷 Eval: Unknown - This is the initial state; I have not started the task yet.
# INFO     [agent] 🧠 Memory: I need to find and compare the prices of Qwen and DeepSeek-V3.
# INFO     [agent] 🎯 Next goal: Search online for the price of Qwen and DeepSeek-V3.
# INFO     [agent] 🛠️  Action 1/1: {"search_google":{"query":"Qwen price"}}
# INFO     [controller] 🔍  Searched for "Qwen price" in Google
# INFO     [agent] 📍 Step 2
# INFO     [agent] 👍 Eval: Success - I have found several results regarding the price of Qwen, with price information displayed in multiple snippets.
# INFO     [agent] 🧠 Memory: I need to find and compare the prices of Qwen and DeepSeek-V3. Found prices for Qwen: $0.0000000000002586 USD and $<0.000001 USD.
# INFO     [agent] 🎯 Next goal: Search online for the price of DeepSeek-V3.
# INFO     [agent] 🛠️  Action 1/1: {"search_google":{"query":"DeepSeek-V3 price"}}
# INFO     [controller] 🔍  Searched for "DeepSeek-V3 price" in Google
# INFO     [agent] 📍 Step 3
# INFO     [agent] 👍 Eval: Success - Found the price details for DeepSeek-V3 in multiple snippets.
# INFO     [agent] 🧠 Memory: Qwen price: around $0.0000000000002586 USD. DeepSeek-V3 price: $0.27 per million token inputs and $1.10 per million token outputs.
# INFO     [agent] 🎯 Next goal: Compare these prices to conclude the task.
# INFO     [agent] 🛠️  Action 1/1: {"done":{"text":"The price of Qwen is approximately $0.0000000000002586 USD, and the price of DeepSeek-V3 is $0.27 per million token inputs and $1.10 per million token outputs. Qwen is significantly cheaper than DeepSeek-V3 in terms of initial cost per token.","success":true}}
# INFO     [agent] 📄 Result: The price of Qwen is approximately $0.0000000000002586 USD, and the price of DeepSeek-V3 is $0.27 per million token inputs and $1.10 per million token outputs. Qwen is significantly cheaper than DeepSeek-V3 in terms of initial cost per token.
# INFO     [agent] ✅ Task completed
# INFO     [agent] ✅ Successfully
# AgentHistoryList(all_results=[ActionResult(is_done=False, success=None, extracted_content='🔍  Searched for "Qwen price" in Google', error=None, include_in_memory=True), ActionResult(is_done=False, success=None, extracted_content='🔍  Searched for "DeepSeek-V3 price" in Google', error=None, include_in_memory=True), ActionResult(is_done=True, success=True, extracted_content='The price of Qwen is approximately $0.0000000000002586 USD, and the price of DeepSeek-V3 is $0.27 per million token inputs and $1.10 per million token outputs. Qwen is significantly cheaper than DeepSeek-V3 in terms of initial cost per token.', error=None, include_in_memory=False)], all_model_outputs=[{'search_google': {'query': 'Qwen price'}, 'interacted_element': None}, {'search_google': {'query': 'DeepSeek-V3 price'}, 'interacted_element': None}, {'done': {'text': 'The price of Qwen is approximately $0.0000000000002586 USD, and the price of DeepSeek-V3 is $0.27 per million token inputs and $1.10 per million token outputs. Qwen is significantly cheaper than DeepSeek-V3 in terms of initial cost per token.', 'success': True}, 'interacted_element': None}])
                                                 