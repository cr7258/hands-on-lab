from os import getenv
from typing import Annotated
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools.tavily_search import TavilySearchResults

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
graph = graph_builder.compile()


# Visualize the graph
try:
    image = graph.get_graph().draw_mermaid_png()
    with open('02-graph.png', 'wb') as f:
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

# User: What's the weather today in Shanghai?
# Assistant: [{"title": "Weather in Shanghai", "url": "https://www.weatherapi.com/", "content": "{'location': {'name': 'Shanghai', 'region': 'Shanghai', 'country': 'China', 'lat': 31.005, 'lon': 121.4086, 'tz_id': 'Asia/Shanghai', 'localtime_epoch': 1741960578, 'localtime': '2025-03-14 21:56'}, 'current': {'last_updated_epoch': 1741959900, 'last_updated': '2025-03-14 21:45', 'temp_c': 10.2, 'temp_f': 50.4, 'is_day': 0, 'condition': {'text': 'Light rain', 'icon': '//cdn.weatherapi.com/weather/64x64/night/296.png', 'code': 1183}, 'wind_mph': 5.1, 'wind_kph': 8.3, 'wind_degree': 33, 'wind_dir': 'NNE', 'pressure_mb': 1018.0, 'pressure_in': 30.06, 'precip_mm': 2.57, 'precip_in': 0.1, 'humidity': 94, 'cloud': 75, 'feelslike_c': 9.2, 'feelslike_f': 48.5, 'windchill_c': 9.0, 'windchill_f': 48.1, 'heatindex_c': 10.0, 'heatindex_f': 50.0, 'dewpoint_c': 9.6, 'dewpoint_f': 49.3, 'vis_km': 8.0, 'vis_miles': 4.0, 'uv': 0.0, 'gust_mph': 7.6, 'gust_kph': 12.3}}", "score": 0.9127278}, {"title": "Shanghai weather in March 2025 - Weather25.com", "url": "https://www.weather25.com/asia/china/shanghai?page=month&month=March", "content": "Shanghai weather in March 2025 | Shanghai 14 day weather Shanghai  Shanghai Shanghai weather in March 2025 | Shanghai in March | | Shanghai in May | Temperatures in Shanghai in March Weather in Shanghai in March - FAQ The average temperature in Shanghai in March is 7/15° C. On average, there are 7 rainy days in Shanghai during March. Weather wise, is March a good time to visit Shanghai? The weather in Shanghai in March is ok. On average, there are 0 snowy days in Shanghai in March. More about the weather in Shanghai Shanghai 14 day weather Long range weather for Shanghai Shanghai weather in November Shanghai weather in December Shanghai Webcam Weather tomorrow Hotels in Shanghai", "score": 0.9106172}]
# Assistant: Today's weather in Shanghai is characterized by light rain, with a temperature of approximately 10.2°C (50.4°F). The wind is coming from the north-northeast at about 8.3 kph (5.1 mph), and the humidity level is at 94%. The cloud cover is around 75%, and visibility is 8 kilometers (4 miles).
