import random
from typing import Annotated, Literal

from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.prebuilt import InjectedState


@tool
def get_travel_recommendations():
    """Get recommendation for travel destinations"""
    return random.choice(["aruba", "turks and caicos"])


@tool
def get_hotel_recommendations(location: Literal["aruba", "turks and caicos"]):
    """Get hotel recommendations for a given destination."""
    return {
        "aruba": [
            "The Ritz-Carlton, Aruba (Palm Beach)"
            "Bucuti & Tara Beach Resort (Eagle Beach)"
        ],
        "turks and caicos": ["Grace Bay Club", "COMO Parrot Cay"],
    }[location]


def make_handoff_tool(*, agent_name: str):
    """Create a tool that can return handoff via a Command"""
    tool_name = f"transfer_to_{agent_name}"

    @tool(tool_name)
    def handoff_to_agent(
        state: Annotated[dict, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId], # Annotation for injecting the tool_call_id
    ):
        """Ask another agent for help."""
        tool_message = {
            "role": "tool",
            "content": f"Successfully transferred to {agent_name}",
            "name": tool_name,
            "tool_call_id": tool_call_id,
        }
        return Command(
            # navigate to another agent node in the PARENT graph
            goto=agent_name,
            graph=Command.PARENT,
            # This is the state update that the agent `agent_name` will see when it is invoked.
            # We're passing agent's FULL internal message history AND adding a tool message to make sure
            # the resulting chat history is valid.
            update={"messages": state["messages"] + [tool_message]},
        )

    return handoff_to_agent


from os import getenv
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph, START
from langgraph.prebuilt import create_react_agent, InjectedState
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver


model = ChatOpenAI(
  openai_api_key=getenv("OPENROUTER_API_KEY"),
  openai_api_base="https://openrouter.ai/api/v1",
  model_name="openai/gpt-4o",
)

# Define travel advisor tools and ReAct agent
travel_advisor_tools = [
    get_travel_recommendations,
    make_handoff_tool(agent_name="hotel_advisor"),
]
travel_advisor = create_react_agent(
    model,
    travel_advisor_tools,
    prompt=(
        "You are a general travel expert that can recommend travel destinations (e.g. countries, cities, etc). "
        "If you need hotel recommendations, ask 'hotel_advisor' for help. "
        "You MUST include human-readable response before transferring to another agent."
    ),
)


def call_travel_advisor(
    state: MessagesState,
) -> Command[Literal["hotel_advisor", "human"]]:
    # You can also add additional logic like changing the input to the agent / output from the agent, etc.
    # NOTE: we're invoking the ReAct agent with the full history of messages in the state
    response = travel_advisor.invoke(state)
    return Command(update=response, goto="human")


# Define hotel advisor tools and ReAct agent
hotel_advisor_tools = [
    get_hotel_recommendations,
    make_handoff_tool(agent_name="travel_advisor"),
]
hotel_advisor = create_react_agent(
    model,
    hotel_advisor_tools,
    prompt=(
        "You are a hotel expert that can provide hotel recommendations for a given destination. "
        "If you need help picking travel destinations, ask 'travel_advisor' for help."
        "You MUST include human-readable response before transferring to another agent."
    ),
)


def call_hotel_advisor(
    state: MessagesState,
) -> Command[Literal["travel_advisor", "human"]]:
    response = hotel_advisor.invoke(state)
    return Command(update=response, goto="human")


def human_node(
    state: MessagesState, config
) -> Command[Literal["hotel_advisor", "travel_advisor", "human"]]:
    """A node for collecting user input."""

    user_input = interrupt(value="Ready for user input.")

    # identify the last active agent
    # (the last active node before returning to human)
    langgraph_triggers = config["metadata"]["langgraph_triggers"]
    if len(langgraph_triggers) != 1:
        raise AssertionError("Expected exactly 1 trigger in human node")

    active_agent = langgraph_triggers[0].split(":")[1]

    return Command(
        update={
            "messages": [
                {
                    "role": "human",
                    "content": user_input,
                }
            ]
        },
        goto=active_agent,
    )


builder = StateGraph(MessagesState)
builder.add_node("travel_advisor", call_travel_advisor)
builder.add_node("hotel_advisor", call_hotel_advisor)

# This adds a node to collect human input, which will route
# back to the active agent.
builder.add_node("human", human_node)

# We'll always start with a general travel advisor.
builder.add_edge(START, "travel_advisor")


checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

# View
try:
    image = graph.get_graph().draw_mermaid_png()
    with open('09-graph.png', 'wb') as f:
        f.write(image)
except Exception as e:
    print(e)


# Test multi-turn conversation
import uuid

thread_config = {"configurable": {"thread_id": uuid.uuid4()}}

inputs = [
    # 1st round of conversation,
    {
        "messages": [
            {"role": "user", "content": "i wanna go somewhere warm in the caribbean"}
        ]
    },
    # Since we're using `interrupt`, we'll need to resume using the Command primitive.
    # 2nd round of conversation,
    Command(
        resume="could you recommend a nice hotel in one of the areas and tell me which area it is."
    ),
    # 3rd round of conversation,
    Command(
        resume="i like the first one. could you recommend something to do near the hotel?"
    ),
]

for idx, user_input in enumerate(inputs):
    print()
    print(f"--- Conversation Turn {idx + 1} ---")
    print()
    print(f"User: {user_input}")
    print()
    for update in graph.stream(
        user_input,
        config=thread_config,
        stream_mode="updates",
    ):
        for node_id, value in update.items():
            if isinstance(value, dict) and value.get("messages", []):
                last_message = value["messages"][-1]
                if isinstance(last_message, dict) or last_message.type != "ai":
                    continue
                print(f"{node_id}: {last_message.content}")

# --- Conversation Turn 1 ---

# User: {'messages': [{'role': 'user', 'content': 'i wanna go somewhere warm in the caribbean'}]}

# travel_advisor: I recommend visiting Aruba if you are looking for a warm getaway in the Caribbean. Aruba is known for its stunning white-sand beaches, perfect weather, and vibrant culture. It's a great choice for relaxing, enjoying water sports, and exploring the unique landscapes and cultural attractions.

# If you need accommodations recommendations, I can transfer you to a hotel expert for that. Would you like me to do so?

# --- Conversation Turn 2 ---

# User: Command(resume='could you recommend a nice hotel in one of the areas and tell me which area it is.')

# hotel_advisor: Here are a couple of hotel recommendations in Aruba:

# 1. **The Ritz-Carlton, Aruba** – Located in Palm Beach, this luxury hotel offers beautiful ocean views, a world-class spa, and excellent dining options. It's perfect for a lavish and relaxing stay.

# 2. **Bucuti & Tara Beach Resort** – Situated on Eagle Beach, this adults-only resort is ideal for couples looking for a romantic escape. It provides a serene atmosphere with impeccable service.

# Both Palm Beach and Eagle Beach are popular areas in Aruba with pristine beaches and various activities to enjoy.

# --- Conversation Turn 3 ---

# User: Command(resume='i like the first one. could you recommend something to do near the hotel?')

# hotel_advisor: Staying at The Ritz-Carlton in Palm Beach, Aruba, there are several exciting activities and attractions you can enjoy nearby:

# 1. **Water Sports**: Palm Beach offers a variety of water sports, including jet skiing, parasailing, and paddleboarding. You can rent equipment or book guided adventures along the beach.

# 2. **Palm Beach Strip**: Explore the vibrant Palm Beach Strip, known for its shopping, dining, and nightlife. There's always something happening, from live music to cultural events.

# 3. **California Lighthouse**: A short drive from The Ritz-Carlton, this iconic lighthouse offers panoramic views of the island, and it's a great spot for photography enthusiasts.

# 4. **Arikok National Park**: Explore the island's natural beauty in this national park, where you can hike, explore caves, and see unique wildlife.

# 5. **Local Dining**: Try some delicious Aruban cuisine at nearby restaurants, which often feature fresh seafood, local flavors, and beachfront views.

# These activities should make your stay even more enjoyable and memorable!