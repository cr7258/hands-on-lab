from smolagents import DuckDuckGoSearchTool, HfApiModel
import os

# You can choose to not pass any model_id to HfApiModel to use a default free model
model = HfApiModel(token=os.getenv("HUGGINGFACE_API_TOKEN"))
search_tool = DuckDuckGoSearchTool()
print(search_tool("Who's the current president of Russia?"))