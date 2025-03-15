from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver


class State(TypedDict):
    input: str
    user_feedback: str


def step_1(state):
    print("---Step 1---")
    pass


def human_feedback(state):
    print("---human_feedback---")
    feedback = interrupt("Please provide feedback:")
    return {"user_feedback": feedback}


def step_3(state):
    print("---Step 3---")
    pass


builder = StateGraph(State)
builder.add_node("step_1", step_1)
builder.add_node("human_feedback", human_feedback)
builder.add_node("step_3", step_3)
builder.add_edge(START, "step_1")
builder.add_edge("step_1", "human_feedback")
builder.add_edge("human_feedback", "step_3")
builder.add_edge("step_3", END)

# Set up memory
memory = MemorySaver()

# Add
graph = builder.compile(checkpointer=memory)

# View
try:
    image = graph.get_graph().draw_mermaid_png()
    with open('08-simple-graph.png', 'wb') as f:
        f.write(image)
except Exception as e:
    print(e)

# Input
initial_input = {"input": "hello world"}

# Thread
thread = {"configurable": {"thread_id": "1"}}

# Run the graph until the first interruption
for event in graph.stream(initial_input, thread, stream_mode="updates"):
    print(event)
    print("\n")

# Continue the graph execution
for event in graph.stream(
    Command(resume="go to step 3!"), thread, stream_mode="updates"
):
    print(event)
    print("\n")

# ---Step 1---
# {'step_1': None}


# ---human_feedback---
# {'__interrupt__': (Interrupt(value='Please provide feedback:', resumable=True, ns=['human_feedback:d593b69e-4152-9e42-0eb9-e0ce08ace5e0'], when='during'),)}


# ---human_feedback---
# {'human_feedback': {'user_feedback': 'go to step 3!'}}


# ---Step 3---
# {'step_3': None}