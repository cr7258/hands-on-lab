from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from os import getenv

# 需求：  提示词1--> llm--> 文本----提示词2---->llm ---评分

llm = ChatOpenAI(
  openai_api_key=getenv("OPENROUTER_API_KEY"),
  openai_api_base="https://openrouter.ai/api/v1",
  model_name="openai/gpt-4o",
)

prompt1 = PromptTemplate.from_template('给我写一篇关于{key_word}的{type}，字数不超过{count}。')

prompt2 = PromptTemplate.from_template('请简单评价一下这篇短文，如果总分是10分，请给这篇短文打分： {text_content}')

# 整个需求的第一段，组成一个chain
chain1 = prompt1 | llm | StrOutputParser()


# 第一种：
# chain2 = {'text_content': chain1} | prompt2 | llm | StrOutputParser()

# 第二种
def print_chain1(input):
    print(input)
    print('--' * 30)
    return {'text_content': input}

# 打印 chain1 的输出
chain2 = chain1 | RunnableLambda(print_chain1) | prompt2 | llm | StrOutputParser()

print(chain2.invoke({'key_word': '青春', 'type': '散文', 'count': 400}))
# 青春是一场如诗如歌的旅程，带着无限的可能性和不确定性奔向未来。那是一个充满激情与梦想的阶段，仿佛每一个日出都在耳边低语，激励我们去追逐那些隐藏在心底的渴望。

# 清晨的第一缕阳光洒在校园的操场上，年轻的脸庞上写满了未来的希冀，奔跑的脚步声像是青春的乐章，有力而坚定。无数个挑灯夜读的晚上，那伴随咖啡香气的文字不仅是知识的积累，更是梦想的飞扬。从课堂到球场，从操场到图书馆，我们在不同的角色里化茧成蝶，努力地将青春的颜色涂满生活的每一个角落。

# 青春也许会有迷茫与挫折，但那是生命的必修课。那些跌倒又爬起的瞬间，正是青春的魅力所在。我们在失败中感悟成长，于孤独中领悟自我。每一滴汗水和泪水，都在浇灌着成长的沃土，让我们在历练中学会坚强和包容。

# 然而，青春总是短暂的，宛如昙花一现。它在不经意间悄然流逝，让人措手不及。因此，更显得珍贵。每一段友情、每一次欢笑、每一个心动的瞬间，都值得被珍藏。正如星空下无尽闪烁的星星，每一颗都是青春的标记，映照出我们最好的年华。

# 当回首往事，我们会发现青春是一幅泼墨的画卷，无论色彩多么斑斓或黯淡，都是我们不悔的旅程。让我们怀揣那份属于自己的青春勇气，去迎接无限的未来。
# ------------------------------------------------------------
# 这篇短文以抒情的笔调描绘了青春的多姿多彩和其中的成长历程。作者通过比喻和象征手法，将青春比作“如诗如歌的旅程”，用生动的语言描绘了青春的活力和潜力。文中详细描述了青春的不同面貌，从校园生活到个人成长，虽然短暂但却充满意义。尤其是在描绘青春即将流逝的部分，以“昙花一现”来形容，突出了珍贵与无奈，不失感人之处。

# 文本结构清晰，语言流畅，情感充沛，使读者能够感受到青春的美好以及随之而来的挑战。虽然整体具备优美的抒情，但在某些地方的表达可能稍显宽泛，若能加入更多具体的个人经历，或许更能引起共鸣。

# 综合来看，这篇短文富有诗意和感染力，能够引起读者对青春的思考和怀念。若以10分为满分，个人认为可以给这篇短文打8分。