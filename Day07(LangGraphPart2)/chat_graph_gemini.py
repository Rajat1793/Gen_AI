from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
import os
from langgraph.checkpoint.mongodb import MongoDBSaver

# Load environment variables (for GEMINI_API_KEY)
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

class State(TypedDict):
    messages: Annotated[list, add_messages]

# Initialize the chat model (Google Gemini in this example)
llm = init_chat_model(model_provider="google_genai", model="gemini-1.5-flash-8b")
# If you want to use OpenAI, uncomment the following line and comment the above:
# llm = init_chat_model(model_provider="openai", model="gpt-4.1")

def chat_node(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# Build the state graph
graph_builder = StateGraph(State)
graph_builder.add_node("chat_node", chat_node)
graph_builder.add_edge(START, "chat_node")
graph_builder.add_edge("chat_node", END)
graph = graph_builder.compile()

# checkpointing
def compile_graph_with_checkpointer(checkpointer):
    graph_with_checkpointer = graph_builder.compile(checkpointer=checkpointer)
    return graph_with_checkpointer

def main():
    # Use the correct MongoDB URI with authSource=admin
    DB_URI = "mongodb://admin:admin@localhost:27017/?authSource=admin"
    config = {"configurable": {"thread_id": "1"}}
    
    with MongoDBSaver.from_conn_string(DB_URI) as mongo_checkpointer:
        graph_with_mongo = compile_graph_with_checkpointer(mongo_checkpointer)
        query = input(" > ")
        # invoke creates a fresh new state and its gets deleted as soon as states gets over
        result = graph_with_mongo.invoke({"messages": [{"role": "user", "content": query}]}, config)
        print(result)

if __name__ == "__main__":
    main()
