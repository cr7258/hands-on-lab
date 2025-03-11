from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RouterRunnable, RunnableSequence
from langchain_openai import ChatOpenAI
from os import getenv

# 需求：用户会问到各种领域（数学，物理，历史等）的问题，根据不同的领域，定义不同的提示词模板。动态的选择合适的任务模板去完成。

llm = ChatOpenAI(
  openai_api_key=getenv("OPENROUTER_API_KEY"),
  openai_api_base="https://openrouter.ai/api/v1",
  model_name="openai/gpt-4o",
)

# 定义物理任务模板
physics_template = ChatPromptTemplate.from_template(
    "你是一位物理学教授，擅长用简洁易懂的方式回答物理问题。以下是问题内容：{input}"
)

# 定义数学任务模板
math_template = ChatPromptTemplate.from_template(
    "你是一位数学家，擅长分步骤解决数学问题，并提供详细的解决过程。以下是问题内容：{input}"
)

# 定义历史任务模板
history_template = ChatPromptTemplate.from_template(
    "你是一位历史学家，对历史事件和背景有深入研究。以下是问题内容：{input}"
)

# 定义计算机科学任务模板
computerscience_template = ChatPromptTemplate.from_template(
    "你是一位计算机科学专家，擅长算法、数据结构和编程问题。以下是问题内容：{input}"
)

default_template = ChatPromptTemplate.from_template(
    "输入内容无法归类，请直接回答：{input}"
)

default_chain = default_template | llm
physics_chain = physics_template | llm
math_chain = math_template | llm
history_chain = history_template | llm
computerscience_chain = computerscience_template | llm


# 动态路由的chain
def route(input):
    """根据大模型第一次处理只有的输出来： 动态判断各种领域的任务"""
    if '物理' in input['type']:
        print('1号')
        return {"key": 'physics', "input": input['input']}
    elif '数学' in input['type']:
        print('2号')
        return {"key": 'math', "input": input['input']}
    elif '历史' in input['type']:
        print('3号')
        return {"key": 'history', "input": input['input']}
    elif '计算机' in input['type']:
        print('4号')
        return {"key": 'computer_science', "input": input['input']}
    else:
        print('5号')
        return {"key": 'default', "input": input['input']}


# 创建一个路由节点
route_runnable = RunnableLambda(route)

# 路由调度器
router = RouterRunnable(runnables={ # 所有各个领域对应的任务 字典
    'physics': physics_chain,
    'math': math_chain,
    'history': history_chain,
    'computer_science': computerscience_chain,
    'default': default_chain
})


# 第一个提示词模板：
first_prompt = ChatPromptTemplate.from_template(
    "不要回答下面用户的问题，只要根据用户的输入来判断分类，一共有[物理，历史，计算机，数学，其他]5种类别。\n\n \
    用户的输入：{input} \n\n \
    最后的输出包含分类的类别和用户输入的内容，输出格式为json. 其中，类别的key为type，用户输入内容的key为input"
)

chain1 = first_prompt | llm | JsonOutputParser()

# 相当于
# chain2 = RunnableSequence(chain1, route_runnable, router, StrOutputParser())  
chain2 = chain1 | route_runnable | router | StrOutputParser()

inputs = [
    {"input": "什么是黑体辐射？"},  # 物理问题
    {"input": "计算 2 + 2 的结果。"},  # 数学问题
    {"input": "介绍一次世界大战的背景。"},  # 历史问题
    {"input": "如何实现快速排序算法？"}  # 计算机科学问题
]

for inp in inputs:
    result = chain2.invoke(inp)
    print(f'问题: {inp} \n 回答: {result} \n')
# 1号
# 问题: {'input': '什么是黑体辐射？'} 
# 回答: 黑体辐射指的是一种理想化物体的辐射现象，这种物体被称为“黑体”。在物理学中，黑体是一个能够完全吸收任何波长的电磁辐射的物体，因此它不会反射任何光，看起来完全是黑色的。

# 当黑体被加热时，会以特定的方式发射辐射。这种辐射只依赖于物体的温度，而与其他特性无关。黑体辐射在不同温度下的辐射强度分布是经典物理学的重要课题，最终由普朗克在1900年提出的“普朗克辐射定律”成功解释。

# 普朗克辐射定律表明，黑体辐射的波长分布服从一个特定的数学函数，这个函数与物体的温度密切相关。温度越高，辐射的峰值波长越短，同时整体辐射能量也更大。

# 黑体辐射概念在很多领域有应用，比如解释恒星光谱、研究热成像技术以及发展量子力学基础理论等。 

# 2号
# 问题: {'input': '计算 2 + 2 的结果。'} 
#  回答: 计算 \(2 + 2\) 的结果非常简单。我们可以逐步分解这个加法过程：

# 步骤 1：识别数字
# - 我们有两个数字：2 和 2。

# 步骤 2：将这两个数字相加
# - 计算 \(2 + 2\)。

# 步骤 3：得出结果
# - \(2 + 2 = 4\)。

# 因此，\(2 + 2\) 的结果是 4。 

# 3号
# 问题: {'input': '介绍一次世界大战的背景。'} 
#  回答: 一次世界大战（1914-1918年）是一场发生在全球范围内的大规模军事冲突，其背景复杂且多层次，涉及政治、经济、军事和社会因素。以下是一些关键背景：

# 1. **帝国主义扩张**：19世纪末和20世纪初，欧洲列强如英国、法国、德国、奥匈帝国和俄罗斯帝国正处于帝国主义的巅峰时期，争夺殖民地和全球影响力。此种竞争加剧了列强之间的紧张关系。

# 2. **军事联盟体系**：由于相互猜忌和防御需要，欧洲列强逐渐形成了两个主要军事联盟：协约国（主要包括英国、法国和俄罗斯）与同盟国（主要包括德国、奥匈帝国和意大利，尽管意大利后来倒向协约国）。这个联盟体系使得任何局部冲突都有可能扩大为全面战争。

# 3. **民族主义**：欧洲国家内部以及巴尔干半岛地区的民族主义情绪高涨，特别是在奥匈帝国和奥斯曼帝国等多民族国家，这导致了内部的不稳定和外部的侵略性。

# 4. **巴尔干半岛的动荡**：巴尔干地区由于奥斯曼帝国的衰落和民族主义的兴起成为欧洲的“火药桶”。塞尔维亚、希腊、保加利亚等国都在争夺奥斯曼遗留下来的领土，奥匈帝国和俄罗斯则在此地区有重要利益。

# 5. **军备竞赛**：20世纪初，列强之间展开了激烈的军备竞赛，尤其是海军力量的竞争。德国和英国的海军扩张尤其引人注目，这导致紧张局势进一步加剧。

# 6. **外交失误与危机处理不当**：19世纪末与20世纪初，欧洲发生了一系列外交事件和危机，如摩洛哥危机、巴尔干战争等。这些事件削弱了各国间原本就脆弱的信任关系。

# 7. **萨拉热窝事件**：1914年6月28日，奥匈帝国皇储斐迪南大公在萨拉热窝被一名塞尔维亚民族主义者刺杀。这一事件成为导火索，迅速引发了奥匈帝国与塞尔维亚之间的冲突，并通过联盟体系扩散到整个欧洲。

# 结合上述因素，一战成为不可避免的“完美风暴”，导致了一场空前的全球战争，改变了20世纪的历史进程。 

# 4号
# 问题: {'input': '如何实现快速排序算法？'} 
#  回答: 快速排序（QuickSort）是一种高效的分而治之排序算法。它通过选择一个“基准”元素，并将待排序数组划分为两个子数组，一个包含小于基准的元素，另一个包含大于基准的元素，递归地对这两个子数组进行排序。下面是快速排序算法的具体实现步骤以及Python代码示例。

# ### 实现步骤

# 1. **选择基准**：从数组中选择一个元素作为基准（pivot）。基准的选择方法有多种，可以是第一个元素、最后一个元素、随机一个元素或中间元素。
   
# 2. **分区**：重新排列数组，使所有小于基准的元素都出现在基准的左边，所有大于基准的元素都出现在基准的右边。基准最终位于其正确的排序位置。
   
# 3. **递归排序**：递归地对划分的左右子数组进行快速排序。

# 4. **终止条件**：子数组的长度为0或1时，不需要再进行排序。

# ### Python代码示例

# ```python
# def quicksort(arr):
#     # 终止条件：数组为空或仅包含一个元素
#     if len(arr) <= 1:
#         return arr
    
#     # 选择基准元素
#     pivot = arr[len(arr) // 2]
    
#     # 分区步骤
#     left = [x for x in arr if x < pivot]
#     middle = [x for x in arr if x == pivot]
#     right = [x for x in arr if x > pivot]
    
#     # 递归调用
#     return quicksort(left) + middle + quicksort(right)

# # 示例用法
# arr = [3, 6, 8, 10, 1, 2, 1]
# sorted_arr = quicksort(arr)
# print(sorted_arr)
# ```

# ### 复杂度分析

# - **时间复杂度**：
#   - 最优和平均时间复杂度：O(n log n)，其中n是数组的长度。
#   - 最差时间复杂度：O(n²)，当每次选择的基准都导致最不平衡的划分时发生，比如在已排序数组上选择第一个或最后一个元素作为基准。

# - **空间复杂度**：最优为O(log n)，在最差情况下为O(n)，这是由于递归系统栈的消耗。

# 通过改进基准选择策略（比如使用随机选取或三数取中法），可以大大降低最差情况发生的概率，从而提升算法的效率。