from smolagents import ToolCallingAgent, HfApiModel
import os

# You can choose to not pass any model_id to HfApiModel to use a default free model
model = HfApiModel(token=os.getenv("HUGGINGFACE_API_TOKEN"))
agent = ToolCallingAgent(tools=[], model=model, add_base_tools=True)
agent.run("Could you get me the title of the page at url 'https://huggingface.co/blog'?")