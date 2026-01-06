"""
Deep Agents Quickstart Demo

Based on: https://docs.langchain.com/oss/python/deepagents/quickstart
"""

import os

from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent


# Note: NO @tool decorator needed!
# Just a regular Python function with:
# - Type hints for parameters
# - Docstring describing the function
def get_weather(city: str) -> str:
    """Get the current weather for a city.

    Args:
        city: The name of the city to get weather for

    Returns:
        Weather information as a string
    """
    # Mock implementation
    print(f"Getting weather for {city}")
    weather_data = {
        "beijing": "Sunny, 25°C",
        "shanghai": "Cloudy, 22°C",
        "shenzhen": "Rainy, 28°C",
        "new york": "Partly cloudy, 18°C",
    }
    return weather_data.get(city.lower(), f"Weather data not available for {city}")


def calculate(expression: str) -> str:
    """Evaluate a mathematical expression.

    Args:
        expression: A mathematical expression to evaluate (e.g., "2 + 2 * 3")

    Returns:
        The result of the calculation as a string
    """
    print(f"Calculating {expression}")
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error: {e}"


def search_knowledge(query: str, limit: int = 3) -> list[dict]:
    """Search the knowledge base for information.

    Args:
        query: The search query
        limit: Maximum number of results to return (default: 3)

    Returns:
        A list of search results
    """
    print(f"Searching knowledge for {query}")
    # Mock implementation
    mock_results = [
        {"title": "LangGraph Overview", "content": "LangGraph is a library for building stateful agents."},
        {"title": "Deep Agents", "content": "Deep Agents is built on top of LangGraph."},
        {"title": "Tool Usage", "content": "Tools in Deep Agents don't need @tool decorator."},
    ]
    return mock_results[:limit]


# System prompt to guide the agent
system_prompt = """You are a helpful assistant with access to the following tools:

## `get_weather`
Get the current weather for a city.

## `calculate`
Evaluate mathematical expressions.

## `search_knowledge`
Search the knowledge base for information.

Use these tools to help answer user questions.
"""

# ============================================================
# LLM Configuration - Using OpenRouter
# ============================================================
model = ChatOpenAI(
    model="deepseek/deepseek-v3.2",  # OpenRouter model name
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

agent = create_deep_agent(
    model=model,
    tools=[get_weather, calculate, search_knowledge],
    system_prompt=system_prompt,
)


def main():
    """Run the agent with a sample query."""
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "What's the weather in Beijing?"}]}
    )

    print("=" * 60)
    print("Agent Response:")
    print("=" * 60)
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
