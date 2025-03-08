from os import getenv
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# 创建模型
model = ChatOpenAI(
  openai_api_key=getenv("OPENROUTER_API_KEY"),
  openai_api_base="https://openrouter.ai/api/v1",
  model_name="openai/gpt-4o",
)


# 加载我们的文档。我们将使用 WebBaseLoader 来加载博客文章：
loader = WebBaseLoader('https://lilianweng.github.io/posts/2023-06-23-agent/')
docs = loader.load()  # 得到整篇文章

# 第一种： Stuff
# Stuff的第一种写法
# chain = load_summarize_chain(model, chain_type='stuff')

# Stuff的第二种写法
# 定义提示
prompt_template = """针对下面的内容，写一个简洁的总结摘要:
"{text}"
简洁的总结摘要:"""
prompt = PromptTemplate.from_template(prompt_template)

llm_chain = LLMChain(llm=model, prompt=prompt)

stuff_chain = StuffDocumentsChain(llm_chain=llm_chain, document_variable_name='text')

result = stuff_chain.invoke(docs)
print(result['output_text'])
# 本文探讨了以大语言模型（LLM）为核心的自主代理系统，其优势和设计组件包括计划、记忆和工具使用。
# 1. 在计划方面，代理可将复杂任务分解为可管理的子目标，通过自我反思不断优化结果。
# 2. 记忆方面，短期记忆用于上下文学习，长期记忆通过外部存储实现信息的快速检索。
# 3. 工具使用方面，代理可接入外部API以弥补模型权重中的信息缺口，增强模型能力。如AutoGPT和GPT-Engineer等案例展示了其应用潜力。面临的挑战包括上下文限制、长期规划及语言界面的可靠性。