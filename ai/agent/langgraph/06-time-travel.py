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
    with open('06-graph.png', 'wb') as f:
        f.write(image)
except Exception as e:
    print(e)

config = {"configurable": {"thread_id": "1"}}
events = graph.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "I'm learning LangGraph. "
                    "Could you do some research on it for me?"
                ),
            },
        ],
    },
    config,
    stream_mode="values",
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

events = graph.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "Ya that's helpful. Maybe I'll "
                    "build an autonomous agent with it!"
                ),
            },
        ],
    },
    config,
    stream_mode="values",
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

# ================================ Human Message =================================

# I'm learning LangGraph. Could you do some research on it for me?
# ================================== Ai Message ==================================
# Tool Calls:
#   tavily_search_results_json (call_4tQ1IxQI92ZZRVEaNITVdpDo)
#  Call ID: call_4tQ1IxQI92ZZRVEaNITVdpDo
#   Args:
#     query: LangGraph language framework
# ================================= Tool Message =================================
# Name: tavily_search_results_json

# [{"title": "langchain-ai/langgraph: Build resilient language agents as graphs.", "url": "https://github.com/langchain-ai/langgraph", "content": "GitHub - langchain-ai/langgraph: Build resilient language agents as graphs. LangGraph is a library for building stateful, multi-actor applications with LLMs, used to create agent and multi-agent workflows. Let's build a tool-calling ReAct-style agent that uses a search tool! The simplest way to create a tool-calling agent in LangGraph is to use create_react_agent: Define the tools for the agent to use Define the tools for the agent to use This means that after tools is called, agent node is called next. workflow.add_edge(\"tools\", 'agent') Normal edge: after the tools are invoked, the graph should always return to the agent to decide what to do next LangGraph adds the input message to the internal state, then passes the state to the entrypoint node, \"agent\".", "score": 0.7159213}, {"title": "LangGraph - LangChain", "url": "https://www.langchain.com/langgraph", "content": "Build and scale agentic applications with LangGraph Platform. Design agent-driven user experiences with LangGraph Platform's APIs. Quickly deploy and scale your application with infrastructure built for agents. LangGraph sets the foundation for how we can build and scale AI workloads — from conversational agents, complex task automation, to custom LLM-backed experiences that 'just work'. The next chapter in building complex production-ready features with LLMs is agentic, and with LangGraph and LangSmith, LangChain delivers an out-of-the-box solution to iterate quickly, debug immediately, and scale effortlessly.” LangGraph sets the foundation for how we can build and scale AI workloads — from conversational agents, complex task automation, to custom LLM-backed experiences that 'just work'. LangGraph Platform is a service for deploying and scaling LangGraph applications, with an opinionated API for building agent UXs, plus an integrated developer studio.", "score": 0.59796065}]
# ================================== Ai Message ==================================

# LangGraph is a platform and library designed for building and scaling agentic applications. Here's some more detailed information about it:

# - **Purpose and Functionality:** 
#   - LangGraph is developed for constructing stateful, multi-actor applications employing Large Language Models (LLMs). It's used to create workflows for agents and multi-agent systems.
#   - It allows developers to build resilient language agents as graphs, enabling easier management of complex interactions and processes.

# - **Features:**
#   - You can design agent-driven user experiences using LangGraph Platform's APIs.
#   - The platform provides tools for deploying and scaling applications, focusing on the concept of agentic computing. This involves making AI workloads more efficient, from conversational agents and task automation to custom LLM-backed solutions.

# - **Technical Aspects:**
#   - LangGraph provides a structured way to create tool-calling agents using a ReAct-style (Reactive) agent that utilizes a search tool.
#   - The architecture allows the graph to return to an "agent" node after tools are invoked to decide the next steps in the process.
  
# - **Platform and Support:**
#   - The LangGraph Platform offers infrastructure to rapidly deploy and scale applications with an opinionated API for building agent UXs.
#   - It includes a developer studio for immediate debugging and iterative development, helping build complex, production-ready features.

# - **Resources:**
#   - The LangGraph library is available on GitHub as part of the LangChain suite of tools. It plays a role in how AI workloads can be developed and scaled effectively.

# You can explore more about LangGraph through [LangGraph GitHub Repository](https://github.com/langchain-ai/langgraph) and [LangGraph on LangChain](https://www.langchain.com/langgraph).
# ================================ Human Message =================================

# Ya that's helpful. Maybe I'll build an autonomous agent with it!
# ================================== Ai Message ==================================

# That sounds like an exciting project! Building an autonomous agent with LangGraph will give you the opportunity to explore stateful, multi-agent systems and leverage the power of large language models in a structured and scalable way. If you have any specific questions or need further assistance as you dive into your project, feel free to ask. Happy coding!

to_replay = None
for state in graph.get_state_history(config):
    print("Num Messages: ", len(state.values["messages"]), "Next: ", state.next)
    print("-" * 80)
    if len(state.values["messages"]) == 3:
        # We are somewhat arbitrarily selecting a specific state based on the number of chat messages in the state.
        to_replay = state
# Num Messages:  6 Next:  ()
# --------------------------------------------------------------------------------
# Num Messages:  5 Next:  ('chatbot',)
# --------------------------------------------------------------------------------
# Num Messages:  4 Next:  ('__start__',)
# --------------------------------------------------------------------------------
# Num Messages:  4 Next:  ()
# --------------------------------------------------------------------------------
# Num Messages:  3 Next:  ('chatbot',)
# --------------------------------------------------------------------------------
# Num Messages:  2 Next:  ('tools',)
# --------------------------------------------------------------------------------
# Num Messages:  1 Next:  ('chatbot',)
# --------------------------------------------------------------------------------
# Num Messages:  0 Next:  ('__start__',)
# --------------------------------------------------------------------------------

print(to_replay.next)
print(to_replay.config)

# ('chatbot',)
# {'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1f0014cf-4416-6ebc-8002-e82981c976be'}}

# The `checkpoint_id` in the `to_replay.config` corresponds to a state we've persisted to our checkpointer.
for event in graph.stream(None, to_replay.config, stream_mode="values"):
    if "messages" in event:
        event["messages"][-1].pretty_print()

# Rewind from the 3rd message
# ================================= Tool Message =================================
# Name: tavily_search_results_json

# [{"title": "langchain-ai/langgraph: Build resilient language agents as graphs.", "url": "https://github.com/langchain-ai/langgraph", "content": "GitHub - langchain-ai/langgraph: Build resilient language agents as graphs. LangGraph is a library for building stateful, multi-actor applications with LLMs, used to create agent and multi-agent workflows. Let's build a tool-calling ReAct-style agent that uses a search tool! The simplest way to create a tool-calling agent in LangGraph is to use create_react_agent: Define the tools for the agent to use Define the tools for the agent to use This means that after tools is called, agent node is called next. workflow.add_edge(\"tools\", 'agent') Normal edge: after the tools are invoked, the graph should always return to the agent to decide what to do next LangGraph adds the input message to the internal state, then passes the state to the entrypoint node, \"agent\".", "score": 0.7159213}, {"title": "LangGraph - LangChain", "url": "https://www.langchain.com/langgraph", "content": "Build and scale agentic applications with LangGraph Platform. Design agent-driven user experiences with LangGraph Platform's APIs. Quickly deploy and scale your application with infrastructure built for agents. LangGraph sets the foundation for how we can build and scale AI workloads — from conversational agents, complex task automation, to custom LLM-backed experiences that 'just work'. The next chapter in building complex production-ready features with LLMs is agentic, and with LangGraph and LangSmith, LangChain delivers an out-of-the-box solution to iterate quickly, debug immediately, and scale effortlessly.” LangGraph sets the foundation for how we can build and scale AI workloads — from conversational agents, complex task automation, to custom LLM-backed experiences that 'just work'. LangGraph Platform is a service for deploying and scaling LangGraph applications, with an opinionated API for building agent UXs, plus an integrated developer studio.", "score": 0.59796065}]
# ================================== Ai Message ==================================

# LangGraph is a library and platform designed for building stateful, multi-actor applications using Large Language Models (LLMs). Here are some key points about LangGraph:

# 1. **Purpose and Functionality**: LangGraph helps in creating agent and multi-agent workflows by structuring them as graphs. It is used to build resilient language agents which are capable of complex task automation and custom experiences backed by LLMs.

# 2. **Tool Integration**: The platform allows for the creation of tool-calling agents, which are primarily developed using the `create_react_agent` method. This involves defining tools the agent can use and determining the flow of tasks within the graph so that the agent can decide on subsequent actions.

# 3. **Development and Deployment**: LangGraph is part of the LangChain ecosystem and includes tools for designing and deploying agent-driven user experiences. It provides an infrastructure for quickly deploying and scaling applications with an integrated developer studio and an opinionated API for building agent user experiences.

# 4. **Applications**: It is used for building and scaling various AI workloads, such as conversational agents and complex automation tasks, enabling rapid iteration and debugging.

# For more detailed information, you can visit the [LangGraph GitHub repository](https://github.com/langchain-ai/langgraph) or explore the [LangGraph Platform](https://www.langchain.com/langgraph) website.