from smolagents import CodeAgent, HfApiModel, DuckDuckGoSearchTool
import os

# You can choose to not pass any model_id to HfApiModel to use a default free model
model = HfApiModel(token=os.getenv("HUGGINGFACE_API_TOKEN"))

web_agent = CodeAgent(
    tools=[DuckDuckGoSearchTool()],
    model=model,
    name="web_search",
    description="Runs web searches for you. Give it your query as an argument."
)

manager_agent = CodeAgent(
    tools=[], model=model, managed_agents=[web_agent]
)

manager_agent.run("Who is the CEO of Hugging Face?")