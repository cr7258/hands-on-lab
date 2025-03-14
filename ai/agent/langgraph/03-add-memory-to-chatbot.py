from os import getenv
from typing import Annotated
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.checkpoint.memory import MemorySaver

# Start by creating a StateGraph. A StateGraph object defines the structure of our chatbot as a "state machine".
class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)


# Add tools
tool = TavilySearchResults(max_results=2)
tools = [tool]

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
    return {"messages": [llm_with_tools.invoke(state["messages"])]}
graph_builder.add_node("chatbot", chatbot)

# Create "tools" node
tool_node = ToolNode(tools=[tool])
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
    with open('03-graph.png', 'wb') as f:
        f.write(image)
except Exception as e:
    print(e)

config = {"configurable": {"thread_id": "1"}}

user_input = "Hi there! My name is Will."

# The config is the **second positional argument** to stream() or invoke()!
events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,
    stream_mode="values",
)
for event in events:
    event["messages"][-1].pretty_print()

user_input = "Remember my name?"

# The config is the **second positional argument** to stream() or invoke()!
events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,
    stream_mode="values",
)
for event in events:
    event["messages"][-1].pretty_print()

# ================================ Human Message =================================

# Hi there! My name is Will.
# ================================== Ai Message ==================================

# Hello Will! How can I assist you today?
# ================================ Human Message =================================

# Remember my name?
# ================================== Ai Message ==================================

# I'll remember your name as Will for the duration of this conversation. How can I help you today, Will?


# Use a different thread_id
# The only difference is we change the `thread_id` here to "2" instead of "1"
events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    {"configurable": {"thread_id": "2"}},
    stream_mode="values",
)
for event in events:
    event["messages"][-1].pretty_print()
# ================================ Human Message =================================

# Remember my name?
# ================================== Ai Message ==================================

# I don't have access to personal memory, so I can't recall your name. However, if you tell me, I'll be sure to use it in our conversation!