from typing_extensions import TypedDict
from openai import OpenAI
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
import os

# load env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# state for langgraph
class State(TypedDict):
    query: str
    llm_result: str | None

# node
def chat_bot(state: State):
    
    query = state['query']
    
    # call gemini
    llm_result = client.chat.completions.create(
    model='gemini-1.5-flash-8b',
    messages=[
        {'role': 'user', 'content': query}
    ])
    # llm call for query
    
    result = llm_result.choices[0].message.content
    state["llm_result"] = result
    
    return state

# creating a graph
graph_builder = StateGraph(State)

# adding node
graph_builder.add_node("chat_bot", chat_bot)

# adding edge
graph_builder.add_edge(START, "chat_bot")
graph_builder.add_edge("chat_bot", END)

# compiling the graph
graph = graph_builder.compile()

def main():
    user = input(" > ")
    # invoke the graph
    _state = {
        "query": user,
        "llm_result": None
    }
    graph_result = graph.invoke(_state)
    print("Graph_Result: ", graph_result)

main()