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
from langchain_core.tools import InjectedToolCallId, tool
from langchain_core.messages import ToolMessage

# Start by creating a StateGraph. A StateGraph object defines the structure of our chatbot as a "state machine".
class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]
    name: str
    birthday: str

graph_builder = StateGraph(State)

# This tool uses interrupt to receive information from a human
@tool
# Note that because we are generating a ToolMessage for a state update, we
# generally require the ID of the corresponding tool call. We can use
# LangChain's InjectedToolCallId to signal that this argument should not
# be revealed to the model in the tool's schema.
def human_assistance(
    name: str, birthday: str, tool_call_id: Annotated[str, InjectedToolCallId]
) -> str:
    """Request assistance from a human."""
    human_response = interrupt(
        {
            "question": "Is this correct?",
            "name": name,
            "birthday": birthday,
        },
    )
    # If the information is correct, update the state as-is.
    if human_response.get("correct", "").lower().startswith("y"):
        verified_name = name
        verified_birthday = birthday
        response = "Correct"
    # Otherwise, receive information from the human reviewer.
    else:
        verified_name = human_response.get("name", name)
        verified_birthday = human_response.get("birthday", birthday)
        response = f"Made a correction: {human_response}"

    # This time we explicitly update the state with a ToolMessage inside
    # the tool.
    state_update = {
        "name": verified_name,
        "birthday": verified_birthday,
        "messages": [ToolMessage(response, tool_call_id=tool_call_id)],
    }
    # We return a Command object in the tool to update our state.
    return Command(update=state_update)


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
    with open('05-graph.png', 'wb') as f:
        f.write(image)
except Exception as e:
    print(e)

user_input = (
    "Can you look up when LangGraph was released? "
    "When you have the answer, use the human_assistance tool for review."
)
config = {"configurable": {"thread_id": "1"}}

events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,
    stream_mode="values",
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

human_command = Command(
    resume={
        "name": "LangGraph",
        "birthday": "Jan 17, 2024",
        # "correct": "y"  # 走第一个分支
    },

)

events = graph.stream(human_command, config, stream_mode="values")
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

# ================================ Human Message =================================

# Can you look up when LangGraph was released? When you have the answer, use the human_assistance tool for review.
# ================================== Ai Message ==================================
# Tool Calls:
#   tavily_search_results_json (call_RvJtK4Wsqi5oPZgUHRSnLQdz)
#  Call ID: call_RvJtK4Wsqi5oPZgUHRSnLQdz
#   Args:
#     query: LangGraph release date
# ================================= Tool Message =================================
# Name: tavily_search_results_json

# [{"title": "Releases · langchain-ai/langgraph - GitHub", "url": "https://github.com/langchain-ai/langgraph/releases", "content": "Releases · langchain-ai/langgraph · GitHub Search code, repositories, users, issues, pull requests... Releases: langchain-ai/langgraph Releases · langchain-ai/langgraph langgraph: release 0.2.70 (#3341) langgraph: add agent name to AI messages in create_react_agent (#3340) fix(langgraph): Dedupe input (right-side) messages in add_messages (#3338) Merge branch 'jacob/dedupe' of github.com:langchain-ai/langgraph into jacob/dedupe langgraph: release 0.2.69 (#3256) docs: update README to include built w/ langgraph (#3254) langgraph: add get_stream_writer() (#3251) langgraph: release 0.2.68 (#3224) langgraph: actually fix flaky test (#3219) langgraph: use 'prompt' param for model input preprocessing in create_react_agent (#3173) langgraph: fix flaky test (#3218) langgraph: add names for tasks (#3202) langgraph: update docstrings/api ref for functional api (#3176) langgraph: add support for BaseModel updates to Command (#2747) langgraph: allow async state modifier in create_react_agent (#3161)", "score": 0.72418857}, {"title": "langgraph · PyPI", "url": "https://pypi.org/project/langgraph/", "content": "LangGraph is a library for building stateful, multi-actor applications with LLMs, used to create agent and multi-agent workflows. The simplest way to create a tool-calling agent in LangGraph is to use create_react_agent: # Define the tools for the agent to use # Define the tools for the agent to use # This means that after `tools` is called, `agent` node is called next. workflow.add_edge(\"tools\", 'agent') Normal edge: after the tools are invoked, the graph should always return to the agent to decide what to do next LangGraph adds the input message to the internal state, then passes the state to the entrypoint node, \"agent\". langgraph-0.2.70-py3-none-any.whl (149.7 kB view details)Uploaded Feb 6, 2025 Python 3", "score": 0.68571854}]
# ================================== Ai Message ==================================
# Tool Calls:
#   human_assistance (call_PipFz6efEssI1srnpwwTgXMV)
#  Call ID: call_PipFz6efEssI1srnpwwTgXMV
#   Args:
#     name: LangGraph
#     birthday: There isn't a specific 'release date' listed in the provided search results for LangGraph. However, the information contains release versions like 0.2.70, which was last updated on GitHub in the context of the documentation updates. For an exact first release date, examining the commit history on the official GitHub page might be needed, or checking for the first version's release notes.
# ================================== Ai Message ==================================
# Tool Calls:
#   human_assistance (call_PipFz6efEssI1srnpwwTgXMV)
#  Call ID: call_PipFz6efEssI1srnpwwTgXMV
#   Args:
#     name: LangGraph
#     birthday: There isn't a specific 'release date' listed in the provided search results for LangGraph. However, the information contains release versions like 0.2.70, which was last updated on GitHub in the context of the documentation updates. For an exact first release date, examining the commit history on the official GitHub page might be needed, or checking for the first version's release notes.
# ================================= Tool Message =================================
# Name: human_assistance

# Made a correction: {'name': 'LangGraph', 'birthday': 'Jan 17, 2024'}
# ================================== Ai Message ==================================

# LangGraph was released on January 17, 2024.

# Note that these fields are now reflected in the state
snapshot = graph.get_state(config)
print({k: v for k, v in snapshot.values.items() if k in ("name", "birthday")})
# {'name': 'LangGraph', 'birthday': 'Jan 17, 2024'}