from os import getenv
from langchain.chains.combine_documents.map_reduce import MapReduceDocumentsChain
from langchain.chains.combine_documents.reduce import ReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_text_splitters import CharacterTextSplitter

# 创建模型
model = ChatOpenAI(
  openai_api_key=getenv("OPENROUTER_API_KEY"),
  openai_api_base="https://openrouter.ai/api/v1",
  model_name="openai/gpt-4o",
)

# 加载我们的文档。我们将使用 WebBaseLoader 来加载博客文章：
loader = WebBaseLoader('https://lilianweng.github.io/posts/2023-06-23-agent/')
docs = loader.load()  # 得到整篇文章

# 第二种： Map-Reduce
# 第一步： 切割阶段
# 每一个小docs为1000个token
text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=1000, chunk_overlap=0)
split_docs = text_splitter.split_documents(docs)

# 第二步： map阶段
map_template = """以下是一组文档(documents)
"{docs}"
根据这个文档列表，请给出总结摘要:"""
map_prompt = PromptTemplate.from_template(map_template)
map_llm_chain = LLMChain(llm=model, prompt=map_prompt)

# 第三步： reduce阶段: (combine和 最终的reduce)
reduce_template = """以下是一组总结摘要:
{docs}
将这些内容提炼成一个最终的、统一的总结摘要:"""
reduce_prompt = PromptTemplate.from_template(reduce_template)
reduce_llm_chain = LLMChain(llm=model, prompt=reduce_prompt)

'''
reduce的思路:
如果map之后文档的累积token数超过了 4000个，那么我们将递归地将文档以<= 4000 个token的批次传递给我们的 StuffDocumentsChain 来创建批量摘要。
一旦这些批量摘要的累积大小小于 4000 个token，我们将它们全部传递给 StuffDocumentsChain 最后一次，以创建最终摘要。
'''

# 定义一个combine的chain
combine_chain = StuffDocumentsChain(llm_chain=reduce_llm_chain, document_variable_name='docs')

reduce_chain = ReduceDocumentsChain(
    # 这是最终调用的链。
    combine_documents_chain=combine_chain,
    # 中间的汇总的脸
    collapse_documents_chain=combine_chain,
    # 将文档分组的最大令牌数。
    token_max=4000
)

# 第四步：合并所有链
map_reduce_chain = MapReduceDocumentsChain(
    llm_chain=map_llm_chain,
    reduce_documents_chain=reduce_chain,
    document_variable_name='docs',
    return_intermediate_steps=False
)


# 第五步： 调用最终的链
result = map_reduce_chain.invoke(split_docs)
print(result['output_text'])
# 这组文档全面探讨了大型语言模型（LLM）在自主智能体系统中的应用，特别是在任务规划、记忆管理和工具使用等方面。智能体通过链式思维和思维树等方法，将复杂任务分解为简单子任务，以提高准确性和执行能力。记忆管理结合短期和长期记忆，通过向量存储实现快速信息检索，而工具使用则通过外部API获取缺失信息，提升任务执行能力。此外，文档还展示了如Chain of Hindsight和Algorithm Distillation等研究示例在模型改进和强化学习中的应用。
# 该文档还提供了关于代码编写的规范指南，包括模块化设计和实现的最佳实践。对代码结构设计、实现顺序以及项目管理提出了详细建议，强调了代码注释和使用`pytest`进行测试的重要性。
# 总的来看，这些文档展示了LLM在复杂任务中的广泛应用潜力和面临的挑战，同时提供了高质量代码实现的方法。研究揭示了LLM在提高推理、规划和工具运用能力方面的重要性，以及在化学等特定领域应用的前景。最后，还指出当前存在的挑战，比如效率、稳定性、可靠性和复杂性问题，强调了在自主智能体开发中需要不断探索和优化的空间。