from typing_extensions import TypedDict, Literal
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import AIMessage
from IPython.display import Image, display
from os import getenv


@tool
def weather_search(city: str):
    """Search for the weather"""
    print("----")
    print(f"Searching for: {city}")
    print("----")
    return "Sunny!"


model = ChatOpenAI(
  openai_api_key=getenv("OPENROUTER_API_KEY"),
  openai_api_base="https://openrouter.ai/api/v1",
  model_name="openai/gpt-4o",
).bind_tools([weather_search])



class State(MessagesState):
    """Simple state."""


def call_llm(state):
    return {"messages": [model.invoke(state["messages"])]}


def human_review_node(state) -> Command[Literal["call_llm", "run_tool"]]:
    last_message = state["messages"][-1]
    tool_call = last_message.tool_calls[-1]

    # this is the value we'll be providing via Command(resume=<human_review>)
    human_review = interrupt(
        {
            "question": "Is this correct?",
            # Surface tool calls for review
            "tool_call": tool_call,
        }
    )

    review_action = human_review["action"]
    review_data = human_review.get("data")

    # if approved, call the tool
    if review_action == "continue":
        return Command(goto="run_tool")

    # update the AI message AND call tools
    elif review_action == "update":
        updated_message = {
            "role": "ai",
            "content": last_message.content,
            "tool_calls": [
                {
                    "id": tool_call["id"],
                    "name": tool_call["name"],
                    # This the update provided by the human
                    "args": review_data,
                }
            ],
            # This is important - this needs to be the same as the message you replacing!
            # Otherwise, it will show up as a separate message
            "id": last_message.id,
        }
        return Command(goto="run_tool", update={"messages": [updated_message]})

    # provide feedback to LLM
    elif review_action == "feedback":
        # NOTE: we're adding feedback message as a ToolMessage
        # to preserve the correct order in the message history
        # (AI messages with tool calls need to be followed by tool call messages)
        tool_message = {
            "role": "tool",
            # This is our natural language feedback
            "content": review_data,
            "name": tool_call["name"],
            "tool_call_id": tool_call["id"],
        }
        return Command(goto="call_llm", update={"messages": [tool_message]})


def run_tool(state):
    new_messages = []
    tools = {"weather_search": weather_search}
    tool_calls = state["messages"][-1].tool_calls
    for tool_call in tool_calls:
        tool = tools[tool_call["name"]]
        result = tool.invoke(tool_call["args"])
        new_messages.append(
            {
                "role": "tool",
                "name": tool_call["name"],
                "content": result,
                "tool_call_id": tool_call["id"],
            }
        )
    return {"messages": new_messages}


def route_after_llm(state) -> Literal[END, "human_review_node"]:
    if len(state["messages"][-1].tool_calls) == 0:
        return END
    else:
        return "human_review_node"


builder = StateGraph(State)
builder.add_node(call_llm)
builder.add_node(run_tool)
builder.add_node(human_review_node)
builder.add_edge(START, "call_llm")
builder.add_conditional_edges("call_llm", route_after_llm)
builder.add_edge("run_tool", "call_llm")

# Set up memory
memory = MemorySaver()

# Add
graph = builder.compile(checkpointer=memory)

# View
try:
    image = graph.get_graph().draw_mermaid_png()
    with open('07-graph.png', 'wb') as f:
        f.write(image)
except Exception as e:
    print(e)


# Example of approving tool
# Input
# initial_input = {"messages": [{"role": "user", "content": "what's the weather in sf?"}]}

# Thread
# thread = {"configurable": {"thread_id": "2"}}

# # Run the graph until the first interruption
# for event in graph.stream(initial_input, thread, stream_mode="updates"):
#     print(event)
#     print("\n")

# for event in graph.stream(
#     # provide value
#     Command(resume={"action": "continue"}),
#     thread,
#     stream_mode="updates",
# ):
#     print(event)
#     print("\n")

# Example of editing tool call
# Input
# initial_input = {"messages": [{"role": "user", "content": "what's the weather in sf?"}]}

# # Thread
# thread = {"configurable": {"thread_id": "3"}}

# # Run the graph until the first interruption
# for event in graph.stream(initial_input, thread, stream_mode="updates"):
#     print(event)
#     print("\n")

# # Let's now continue executing from here
# for event in graph.stream(
#     Command(resume={"action": "update", "data": {"city": "San Francisco, USA"}}),
#     thread,
#     stream_mode="updates",
# ):
#     print(event)
#     print("\n")


# Example of giving feedback to a tool call
# Input
initial_input = {"messages": [{"role": "user", "content": "what's the weather in sf?"}]}

# Thread
thread = {"configurable": {"thread_id": "4"}}

# Run the graph until the first interruption
for event in graph.stream(initial_input, thread, stream_mode="updates"):
    print(event)
    print("\n")

# Let's now continue executing from here
for event in graph.stream(
    # provide our natural language feedback!
    Command(
        resume={
            "action": "feedback",
            "data": "User requested changes: use <city, country> format for location",
        }
    ),
    thread,
    stream_mode="updates",
):
    print(event)
    print("\n")

for event in graph.stream(
    Command(resume={"action": "continue"}), thread, stream_mode="updates"
):
    print(event)
    print("\n")

# {'call_llm': {'messages': [AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_NN9qHAuyqsvxHMGv1RmHqSGg', 'function': {'arguments': '{"city":"San Francisco"}', 'name': 'weather_search'}, 'type': 'function', 'index': 0}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 16, 'prompt_tokens': 49, 'total_tokens': 65, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'openai/gpt-4o', 'system_fingerprint': 'fp_f9f4fb6dbf', 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-a66b05d9-1d10-45b7-8210-1f421f90fed8-0', tool_calls=[{'name': 'weather_search', 'args': {'city': 'San Francisco'}, 'id': 'call_NN9qHAuyqsvxHMGv1RmHqSGg', 'type': 'tool_call'}], usage_metadata={'input_tokens': 49, 'output_tokens': 16, 'total_tokens': 65, 'input_token_details': {}, 'output_token_details': {}})]}}


# {'__interrupt__': (Interrupt(value={'question': 'Is this correct?', 'tool_call': {'name': 'weather_search', 'args': {'city': 'San Francisco'}, 'id': 'call_NN9qHAuyqsvxHMGv1RmHqSGg', 'type': 'tool_call'}}, resumable=True, ns=['human_review_node:9c724d1d-ca9b-629c-8094-8ab05ca05c03'], when='during'),)}


# {'human_review_node': {'messages': [{'role': 'tool', 'content': 'User requested changes: use <city, country> format for location', 'name': 'weather_search', 'tool_call_id': 'call_NN9qHAuyqsvxHMGv1RmHqSGg'}]}}


# {'call_llm': {'messages': [AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_R6YjaaGYjsfTInv0ex6ShxZy', 'function': {'arguments': '{"city":"San Francisco, US"}', 'name': 'weather_search'}, 'type': 'function', 'index': 0}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 18, 'prompt_tokens': 85, 'total_tokens': 103, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'openai/gpt-4o', 'system_fingerprint': 'fp_f9f4fb6dbf', 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-88c4f74d-1a49-4aaf-b77a-7df2ac09085c-0', tool_calls=[{'name': 'weather_search', 'args': {'city': 'San Francisco, US'}, 'id': 'call_R6YjaaGYjsfTInv0ex6ShxZy', 'type': 'tool_call'}], usage_metadata={'input_tokens': 85, 'output_tokens': 18, 'total_tokens': 103, 'input_token_details': {}, 'output_token_details': {}})]}}


# {'__interrupt__': (Interrupt(value={'question': 'Is this correct?', 'tool_call': {'name': 'weather_search', 'args': {'city': 'San Francisco, US'}, 'id': 'call_R6YjaaGYjsfTInv0ex6ShxZy', 'type': 'tool_call'}}, resumable=True, ns=['human_review_node:e0dabe07-10b2-0a90-6591-b7dd26702023'], when='during'),)}


# {'human_review_node': None}


# ----
# Searching for: San Francisco, US
# ----
# {'run_tool': {'messages': [{'role': 'tool', 'name': 'weather_search', 'content': 'Sunny!', 'tool_call_id': 'call_R6YjaaGYjsfTInv0ex6ShxZy'}]}}


# {'call_llm': {'messages': [AIMessage(content='The weather in San Francisco, US is currently sunny!', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 13, 'prompt_tokens': 112, 'total_tokens': 125, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'openai/gpt-4o', 'system_fingerprint': 'fp_f9f4fb6dbf', 'finish_reason': 'stop', 'logprobs': None}, id='run-a5c5fdeb-0c36-409c-a651-a1d6ea4fda71-0', usage_metadata={'input_tokens': 112, 'output_tokens': 13, 'total_tokens': 125, 'input_token_details': {}, 'output_token_details': {}})]}}