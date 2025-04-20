from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI
import os

hf_token = os.getenv("HUGGINGFACE_API_TOKEN")

llm = HuggingFaceInferenceAPI(
    model_name="Qwen/Qwen2.5-Coder-32B-Instruct",
    temperature=0.7,
    max_tokens=100,
    token=hf_token,
)

response = llm.complete("Hello, how are you?")
print(response)
# I am good, how can I help you today?