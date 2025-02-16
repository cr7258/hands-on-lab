from smolagents import load_tool

model_download_tool = load_tool(
    "m-ric/hf-model-downloads",
    trust_remote_code=True
)

result = model_download_tool(task="text-classification")
print("The most downloaded model is {}".format(result))