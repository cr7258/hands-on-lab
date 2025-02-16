from langchain.agents import load_tools
from smolagents import CodeAgent, HfApiModel, Tool
import os

# You can choose to not pass any model_id to HfApiModel to use a default free model
model = HfApiModel(token=os.getenv("HUGGINGFACE_API_TOKEN"))

# Set SerpAPI api key as an environment variable (SERPAPI_API_KEY)
# https://serpapi.com/dashboard
search_tool = Tool.from_langchain(load_tools(["serpapi"])[0])

agent = CodeAgent(tools=[search_tool], model=model)

agent.run("How many more blocks (also denoted as layers) are in BERT base encoder compared to the encoder from the architecture proposed in Attention is All You Need?")