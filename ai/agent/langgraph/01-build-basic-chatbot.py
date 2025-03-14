from os import getenv
from typing import Annotated
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages


# Start by creating a StateGraph. A StateGraph object defines the structure of our chatbot as a "state machine".
class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

# Create llm
llm = ChatOpenAI(
  openai_api_key=getenv("OPENROUTER_API_KEY"),
  openai_api_base="https://openrouter.ai/api/v1",
  model_name="openai/gpt-4o",
)

# Create "chatbot" node
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever the node is used.
graph_builder.add_node("chatbot", chatbot)


# Set entry and finish point
# same as graph_builder.add_edge(START, "chatbot")
graph_builder.set_entry_point("chatbot")
# same as graph_builder.add_edge("chatbot", END)
graph_builder.set_finish_point("chatbot")
graph = graph_builder.compile()

# Visualize the graph
try:
    image = graph.get_graph().draw_mermaid_png()
    with open('01-graph.png', 'wb') as f:
        f.write(image)
except Exception as e:
    print(e)

def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        stream_graph_updates(user_input)
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break

# User: Who are you?
# Assistant: I am an AI language model created by OpenAI, known as ChatGPT. I'm here to help answer questions and provide information on a wide range of topics. How can I assist you today?
