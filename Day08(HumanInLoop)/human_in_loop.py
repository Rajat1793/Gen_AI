from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os, json
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.types import interrupt, Command

# Load environment variables (for GEMINI_API_KEY)
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
tools = []

@tool
def human_assistance(query: str) -> str:
    """
    Use this tool when the user needs help from a human and the AI cannot proceed.
    """
    human_response = interrupt({"query": query})
    return human_response["data"]

tools = [human_assistance]

class State(TypedDict):
    messages: Annotated[list, add_messages]

llm = init_chat_model(model_provider="google_genai", model="gemini-1.5-flash")
llm_with_tools = llm.bind_tools(tools = tools)

def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    print("Tool calls:", message.additional_kwargs.get("tool_calls", []))
    return {"messages": [message]}


tool_node = ToolNode(tools=tools)

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot",tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("chatbot", END)

def create_chat_graph(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)

def user_chat():
    # Use the correct MongoDB URI with authSource=admin
    DB_URI = "mongodb://admin:admin@localhost:27017/?authSource=admin"
    config = {"configurable": {"thread_id": "22"}}
    with MongoDBSaver.from_conn_string(DB_URI) as mongo_checkpointer:
        graph_with_cp = create_chat_graph(mongo_checkpointer)
        while True:
            query = input(" > ")
            # invoke creates a fresh new state and its gets deleted as soon as states gets over
            for event in graph_with_cp.stream({"messages": [{"role": "user", "content": query}]}, config, stream_mode="values"):
                if "messages" in event:
                    event["messages"][-1].pretty_print()

user_chat()

def admin_call():
    # Use the correct MongoDB URI with authSource=admin
    DB_URI = "mongodb://admin:admin@localhost:27017/?authSource=admin"
    config = {"configurable": {"thread_id": "22"}}

    with MongoDBSaver.from_conn_string(DB_URI) as mongo_checkpointer:
        graph_with_cp = create_chat_graph(mongo_checkpointer)

        # Get the latest state
        state = graph_with_cp.get_state(config=config)

        # Get the last message from the state
        last_message = state.values['messages'][-1]

        # Extract function call info
        function_call = last_message.additional_kwargs.get("function_call", {})
        user_query = None

        if function_call.get("name") == "human_assistance":
            args = function_call.get("arguments", "{}")
            try:
                args_dict = json.loads(args)
                user_query = args_dict.get("query")
                print("user query:", user_query)
            except json.JSONDecodeError:
                print("Failed to decode function arguments")

        if user_query:
            print("User has a query:", user_query)
            solution = input(" > ")

            # Resume the interrupted tool call with human-provided solution
            resume_command = Command(resume={"data": solution})
            for event in graph_with_cp.stream(resume_command, config, stream_mode="values"):
                if "messages" in event:
                    event["messages"][-1].pretty_print()
        else:
            print("No human assistance request found in the last message.")

# admin_call()