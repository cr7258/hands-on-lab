from os import getenv
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import ChatOpenAI
from langchain_text_splitters import CharacterTextSplitter

# 创建模型
model = ChatOpenAI(
  openai_api_key=getenv("OPENROUTER_API_KEY"),
  openai_api_base="https://openrouter.ai/api/v1",
  model_name="qwen/qwen-plus",
)

# 加载我们的文档。我们将使用 WebBaseLoader 来加载博客文章：
loader = WebBaseLoader('https://lilianweng.github.io/posts/2023-06-23-agent/')
docs = loader.load()  # 得到整篇文章

# 第三种：Refine
'''
Refine: RefineDocumentsChain 类似于 map-reduce：
文档链通过循环遍历输入文档并逐步更新其答案来构建响应。对于每个文档，它将当前文档和最新的中间答案传递给LLM链，以获得新的答案。
'''
# 第一步： 切割阶段
# 每一个小 docs 为 1000 个 token
text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=1000, chunk_overlap=0)
split_docs = text_splitter.split_documents(docs)

# 指定 chain_type 为：refine
chain = load_summarize_chain(model, chain_type='refine')

result = chain.invoke(split_docs)
print(result['output_text'])
# The provided context does not contribute additional information to further refine the original summary, as it primarily consists of references, tags, and metadata rather than new substantive details about the subject matter. Therefore, the original refined summary remains accurate and comprehensive in its current form.

# **Final Summary:**

# Autonomous agents powered by Large Language Models (LLMs) represent a transformative leap in artificial intelligence, enabling sophisticated reasoning, memory management, and ethical decision-making to execute complex tasks. These agents operate with varying degrees of autonomy, often requiring human guidance for specific tasks while demonstrating independence in others.

# A core strength of these agents lies in their **tool use**, which empowers them to interact seamlessly with external systems and environments. Tools range from basic scripts to advanced frameworks, and their integration is pivotal for expanding agent capabilities. A standout example is **GPT-Engineer**, a system adept at generating code repositories. GPT-Engineer employs a method of task clarification and modular decomposition, guiding users through a series of questions to refine software specifications. This showcases the potential of modular reasoning systems in automating the code generation process while aligning with best practices for software development. By structuring the process into distinct phases—such as defining core classes, methods, and their purposes—GPT-Engineer ensures compatibility, reliability, and ease of debugging in generated code.

# While GPT-Engineer exemplifies powerful tool use, it complements the broader scope of autonomous agents, which include advanced memory systems and planning capabilities. These agents address a wide array of tasks, from routine operations to high-stakes decision-making, all while adhering to ethical guidelines.

# **Challenges:**
# Despite significant advancements, several limitations remain. First, the finite context length constrains the inclusion of historical information, detailed instructions, and API call context, necessitating system designs that function effectively within limited communication bandwidth. Mechanisms like self-reflection, which could significantly enhance learning from past mistakes, are hindered by the lack of infinite context windows. While vector stores and retrieval can broaden access to knowledge, their representational power falls short compared to full attention.

# Long-term planning and task decomposition also pose challenges, as LLMs struggle to adapt plans when encountering unexpected errors, reducing their robustness compared to human trial-and-error learning. Furthermore, the reliance on natural language as an interface between LLMs and external components introduces reliability concerns. Model outputs are prone to formatting errors and occasional rebellious behavior, such as refusing instructions. Consequently, much of the agent demo code focuses heavily on parsing model output.

# **Final Note:**
# The refined summary integrates GPT-Engineer as an example of sophisticated tool use in generating code repositories, highlighting the modular reasoning capabilities that enhance productivity. However, it maintains the focus on autonomous agents, considering their multifaceted roles in managing memory, planning actions, and upholding ethical standards. The addition of challenges, including finite context limitations, difficulties in long-term planning, and natural language interface reliability, provides a balanced perspective on the current state and future potential of these technologies. Addressing these limitations will be essential for unleashing the full capabilities of autonomous agents across diverse applications. 

# Cited as:

# Weng, Lilian. (Jun 2023). “LLM-powered Autonomous Agents”. Lil’Log. https://lilianweng.github.io/posts/2023-06-23-agent/.