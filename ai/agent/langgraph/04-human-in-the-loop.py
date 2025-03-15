from os import getenv
from typing import Annotated
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt
from langchain_core.tools import tool

# Start by creating a StateGraph. A StateGraph object defines the structure of our chatbot as a "state machine".
class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

# This tool uses interrupt to receive information from a human
@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human."""
    human_response = interrupt({"query": query})
    return human_response["data"]


# Add tools
tool = TavilySearchResults(max_results=2)
tools = [tool, human_assistance]

# Create llm
llm = ChatOpenAI(
  openai_api_key=getenv("OPENROUTER_API_KEY"),
  openai_api_base="https://openrouter.ai/api/v1",
  model_name="openai/gpt-4o",
)

# Tell the LLM which tools it can call
llm_with_tools = llm.bind_tools(tools)

# Create "chatbot" node
def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    # Because we will be interrupting during tool execution,
    # we disable parallel tool calling to avoid repeating any
    # tool invocations when we resume.
    assert len(message.tool_calls) <= 1
    return {"messages": [message]}

graph_builder.add_node("chatbot", chatbot)

# Create "tools" node
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")


# Create memory as a checkpointer
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)


# Visualize the graph
try:
    image = graph.get_graph().draw_mermaid_png()
    with open('04-graph.png', 'wb') as f:
        f.write(image)
except Exception as e:
    print(e)

user_input = "I need some expert guidance for building an AI agent. Could you request assistance for me?"
config = {"configurable": {"thread_id": "1"}}

events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,
    stream_mode="values",
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

human_response = (
    "We, the experts are here to help! We'd recommend you check out LangGraph to build your agent."
    " It's much more reliable and extensible than simple autonomous agents."
)

human_command = Command(resume={"data": human_response})

events = graph.stream(human_command, config, stream_mode="values")
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

# ================================ Human Message =================================

# I need some expert guidance for building an AI agent. Could you request assistance for me?
# ================================== Ai Message ==================================
# Tool Calls:
#   human_assistance (call_Ld2CNttWI7tjjBfUO5OJveJ3)
#  Call ID: call_Ld2CNttWI7tjjBfUO5OJveJ3
#   Args:
#     query: I need expert guidance for building an AI agent

# 在 LangGraph 内部，当执行从一个节点（"chatbot"）流向另一个节点（"tools"）时，它会在每个节点处理前显示当前状态。
# 由于两个节点都处理相同的工具调用，所以你看到了两次 Tool Calls 的输出。

# ================================== Ai Message ==================================
# Tool Calls:
#   human_assistance (call_Ld2CNttWI7tjjBfUO5OJveJ3)
#  Call ID: call_Ld2CNttWI7tjjBfUO5OJveJ3
#   Args:
#     query: I need expert guidance for building an AI agent
# ================================= Tool Message =================================
# Name: human_assistance

# We, the experts are here to help! We'd recommend you check out LangGraph to build your agent. It's much more reliable and extensible than simple autonomous agents.
# ================================== Ai Message ==================================

# I have received expert advice for you. It's recommended to check out LangGraph for building your AI agent, as it is considered to be more reliable and extensible compared to simple autonomous agents. If you need more specific guidance or have any questions, feel free to ask!