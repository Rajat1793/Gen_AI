from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os, requests
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition

# Load environment variables (for GEMINI_API_KEY)
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
todos = []

# initialising it as langchain tool
@tool()
def add_todo(task:str):
    """
    Adds the input task to the DB
    
    """
    todos.append(task)
    return True

@tool()
def get_all_todo():
    """
    Returns all todos
    """
    return todos
    
@tool()
def add_number(a: int, b:int):
    """This tool adds two number

    Args:
        a (int): number
        b (int): number
    """
    return a + b

@tool()
def get_weather(city: str):
    """
    This tool return the weather data about the given city
    """
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}."
    
    return "Something went wrong"

# preparing the tools
# keep adding the tool in below array
tools = [get_weather, add_number, add_todo, get_all_todo]

class State(TypedDict):
    messages: Annotated[list, add_messages]
    
# Initialize the chat model (Google Gemini in this example)
llm = init_chat_model(model_provider="google_genai", model="gemini-1.5-flash-8b")

# initializing the new llm call for the tool
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    # response = llm .invoke(state["messages"])
    # invoking the llm_tool
    response = llm_with_tools.invoke(state["messages"]) 
    return {"messages": [response]}

tool_node = ToolNode(tools=tools)

graph_builder = StateGraph(State)
graph_builder.add_node(chatbot)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

def main():
    while True:
        user_query = input("> ")
        state = State(
            messages=[{"role": "user", "content": user_query}]
        )
        for event in graph.stream(state, stream_mode="values"):
            if "messages" in event:
                event["messages"][-1].pretty_print()

main()