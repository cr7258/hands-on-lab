from smolagents import (
    load_tool,
    CodeAgent,
    HfApiModel,
    GradioUI
)
import os

# Import tool from Hub
image_generation_tool = load_tool("m-ric/text-to-image", trust_remote_code=True)

# You can choose to not pass any model_id to HfApiModel to use a default free model
model = HfApiModel(token=os.getenv("HUGGINGFACE_API_TOKEN"))

# Initialize the agent with the image generation tool
agent = CodeAgent(tools=[image_generation_tool], model=model)

GradioUI(agent).launch()