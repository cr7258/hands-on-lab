from os import getenv
from typing import Annotated

from langchain_community.tools import TavilySearchResults
from langchain_core.messages import ToolMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END
from langgraph.graph import add_messages, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import BaseModel
from typing_extensions import TypedDict
from langgraph_utils import draw_graph, loop_graph_invoke, loop_graph_invoke_tools

# 1、定义一个状态 类型
class MyState(TypedDict):  # 在整个流程中， 状态用来保存历史记录
    # messages:状态中保存数据的key， list: 数据类型， add_messages：一个函数，用于更新list数据
    messages: Annotated[list, add_messages]
    ask_person: bool  # 决定是否请求人工介入的标签

def create_response(response: str, ai_message: AIMessage):
    """
    创建一个ToolMessage（包含人类的回答）。
    参数:
    - response (str): 响应文本内容。
    - ai_message (AIMessage): AI消息对象，从中获取工具调用的ID。
    返回:
    - ToolMessage: 包含响应内容和工具调用ID的消息对象。
    """
    return ToolMessage(
        content=response,
        tool_call_id=ai_message.tool_calls[0]["id"],
    )

class AskPersonMessage(BaseModel):
    """
    将对话升级到人工客服。
    如果您无法直接提供帮助，或者用户需要超出您权限的支持，请使用此功能。
    要使用此功能，请转达用户的“请求”，以便人工客服可以提供正确的指导。
    """
    request: str  # 普通用户的请求内容，需要传达给人工客服以获得适当的帮助

# 2、定义一个流程图
graph = StateGraph(MyState)

# 3、准备一个node（节点）, 并且把它添加到流程图中
llm = ChatOpenAI(
  openai_api_key=getenv("OPENROUTER_API_KEY"),
  openai_api_base="https://openrouter.ai/api/v1",
  model_name="openai/gpt-4o",
)

# 4、添加一个工具节点（互联网搜索的工具）
search_tool = TavilySearchResults(max_results=2)
tools = [search_tool]

# 把工具和大模型绑定一下
agent = llm.bind_tools(tools + [AskPersonMessage])

def chatbot(state: MyState):
    resp = agent.invoke(state['messages'])
    ask_person = False  # 默认情况下，不需要人工客服（人工介入）

    # 判断一： 响应中包含工具调用 ， 并且，判断二：工具调用的名字与RequestAssistance类名匹配
    if resp.tool_calls and resp.tool_calls[0]['name'] == AskPersonMessage.__name__:
        ask_person = True  # 如果满足条件，就需要人工介入
    return {'messages': [resp], "ask_person": ask_person}

# chatbot 节点函数如何以当前 State 作为输入，并返回一个包含更新后的 messages
# 第一个参数是唯一的节点名称
# 第二个参数是每当节点被使用时将调用的函数或对象
graph.add_node('agent', chatbot)

# 添加一个工具节点
tool_node = ToolNode(tools=tools)
graph.add_node('tools', tool_node)

# 增加一个人工介入的节点
def person_node(state: MyState):
    """
    处理需要人工客服介入的节点逻辑。
    :param state:
    :return:
    """

    # 创建一个消息
    new_message = []
    # 检查最后一条消息是否不是ToolMessage类型： 表示用户输入：no
    if not isinstance(state['messages'][-1], ToolMessage):
        # 通常情况下，如果，输入了yes，用户会在中断期间更新状态。
        # 如果输入了no， 我们将追加一个占位符ToolMessage，
        # 以便LLM可以继续处理。
        new_message.append(create_response('人工客服太忙了，稍等片刻...', state['messages'][-1]))

    return {
        'messages': new_message,
        'ask_person': False,
    }

graph.add_node('person', person_node)


def select_next_node(state: MyState):
    """
    根据当前状态选择下一个节点。
    参数:
    - state (State): 当前的状态字典，包含所有消息及标志位。
    返回:
    - str: 下一个要执行的节点名称。
    """
    # 如果当前状态指示需要人类介入，则返回"human"节点
    if state["ask_person"]:
        return "person"

    # 否则，我们可以像以前一样路由到其他节点
    # 这里使用了`tools_condition`函数来决定下一步
    return tools_condition(state)

# 根据智能体自动决策是否需要调用工具，
graph.add_conditional_edges(
    'agent',
    select_next_node,
    {  # 路由匹配
        'person': 'person',
        'tools': 'tools',
        END: END
    }
)

# 4、设置边
graph.add_edge('tools', 'agent')
graph.add_edge('person', 'agent')

# 设置入口节点
graph.set_entry_point('agent')
# 我们正在使用内存中的检查点。它将所有内容都保存在内存中。
# 在生产应用程序中，您可能会将其更改为使用 SqliteSaver 或 PostgresSaver 并连接到您自己的数据库 # pip install langgraph-checkpoint-sqlite
memory_checkpointer = MemorySaver()
# sqlite_checkpointer = SqliteSaver('sqlite:///tset.db')

# 整个graph已经确定
graph = graph.compile(
    checkpointer=memory_checkpointer,
    interrupt_before=['person']  # 在执行到"tools"节点之前中断，允许外部处理或检查
    # 注意：如果需要，也可以在工具执行后中断
    # interrupt_after=["tools"]  # 取消注释此行可以在"tools"节点执行后中断

)  # 构建一个图对象

# 5、把graph变成一张图
draw_graph(graph, '10-graph.png')

thread_id = input('请输入一个sessionId:')
config = {"configurable": {"thread_id": thread_id}}


def get_answer(tool_message):
    """让人工介入，并且给一个问题的答案"""
    input_answer = input('人工给一个答案：')
    answer = (
        input_answer
    )

    # 创建一个消息
    person_message = create_response(answer, ai_message=tool_message)

    # 把新人造的消息，添加到工作流的state中
    graph.update_state(
        config=config,
        values={'messages': [person_message]}
    )

    for msg in graph.get_state(config).values['messages'][-1:]:
        msg.pretty_print()

# 执行这个工作流
while True:
    try:
        user_input = input('用户: ')
        if user_input.lower() in ['q', 'exit', 'quit']:
            print('对话结束，拜拜！')
            break
        else:
            # 执行 工作流
            loop_graph_invoke(graph, user_input, config)
            # 查看此时的状态
            now_state = graph.get_state(config)
            # print('此时的状态数据为: ', now_state)

            if 'person' in now_state.next:
                # 可以人工介入
                tools_script_message = now_state.values['messages'][-1]  # 状态中存储的最后一个message
                print('需要请求人工: ', tools_script_message.tool_calls)

                if input('人工是否需要介入： yes或者no').lower() == 'yes':
                    get_answer(tools_script_message)  # 有人类制造一条消息

                else:
                    # 用户输入了no， 代表人工客服没有空。
                    loop_graph_invoke_tools(graph, None, config)

    except Exception as e:
        print(e)

# 请输入一个sessionId:123456
# 用户:   你是谁? 
# ================================ Human Message =================================

# 你是谁?
# ================================== Ai Message ==================================

# 我是一个人工智能助手，旨在帮助您解答问题和提供信息。如果您有任何问题或者需要帮助，可以随时问我！
# 用户: 请找人工
# ================================ Human Message =================================

# 请找人工
# ================================== Ai Message ==================================
# Tool Calls:
#   AskPersonMessage (call_Fpeukp8k4NvCMQnKhH9al5uL)
#  Call ID: call_Fpeukp8k4NvCMQnKhH9al5uL
#   Args:
#     request: 客户要求升级为人工客服。
# 需要请求人工:  [{'name': 'AskPersonMessage', 'args': {'request': '客户要求升级为人工客服。'}, 'id': 'call_Fpeukp8k4NvCMQnKhH9al5uL', 'type': 'tool_call'}]
# 人工是否需要介入： yes或者no yes 
# 人工给一个答案： 来自人工助手的回复.....
# ================================= Tool Message =================================

#  来自人工助手的回复.....