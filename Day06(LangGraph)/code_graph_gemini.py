from typing_extensions import TypedDict
from openai import OpenAI
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
import os
from pydantic import BaseModel
from typing import Literal

# load env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

class ClassifyMessageResponse(BaseModel):
    is_coding_question: bool

class CodeAccuracyResponse(BaseModel):
    accuracy_percentage: str

# state for langgraph
class State(TypedDict):
    query: str
    llm_result: str | None
    accuracy_percentage: str | None
    is_coding_question: bool | None  # <-- FIXED

def classify_message(state: State):
    print("⚠️ classify_message")
    query = state["query"]  # <-- FIXED
    SYSTEM_PROMPT = """
    You are an AI assistant. Your job is to detect if the user's query is
    related to coding question or not.
    Return the response in specified JSON boolean only.
    """
    response = client.beta.chat.completions.parse(
        model='gemini-1.5-flash',
        response_format=ClassifyMessageResponse,
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': query}
        ])
    is_coding_question = response.choices[0].message.parsed.is_coding_question
    state["is_coding_question"] = is_coding_question
    return state

def route_query(state: State) -> Literal["general_query", "coding_query"]:
    print("⚠️ route_query")
    is_coding = state["is_coding_question"]
    if is_coding:
        return "coding_query"
    else:
        return "general_query"

def general_query(state: State):
    print("⚠️ general_query")
    query = state["query"] 
    response = client.chat.completions.create(
        model="gemini-1.5-flash",
        messages=[
            {"role": "user", "content": query}
        ]
    )
    state["llm_result"] = response.choices[0].message.content
    return state

def coding_query(state: State):
    print("⚠️ coding_query")
    query = state["query"] 

    SYSTEM_PROMPT = """
        You are a Coding Expert Agent
    """

    response = client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query}
        ]
    )

    state["llm_result"] = response.choices[0].message.content

    return state

def coding_validate_query(state:State):
    print("⚠️ coding_validate_query")
    query = state["query"]
    llm_code = state["llm_result"]

    SYSTEM_PROMPT = f"""
        You are expert in calculating accuracy of the code according to the question.
        Return the percentage of accuracy
        
        User Query: {query}
        Code: {llm_code}
    """

    response = client.beta.chat.completions.parse(
        model="gemini-2.0-flash",
        response_format=CodeAccuracyResponse,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ]
    )

    state["accuracy_percentage"] = response.choices[0].message.parsed.accuracy_percentage
    return state

# creating a graph
graph_builder = StateGraph(State)

# adding node
graph_builder.add_node("classify_message", classify_message)
graph_builder.add_node("route_query", route_query)
graph_builder.add_node("general_query", general_query)
graph_builder.add_node("coding_query", coding_query)
graph_builder.add_node("coding_validate_query", coding_validate_query)

# adding edge
graph_builder.add_edge(START, "classify_message")
graph_builder.add_conditional_edges("classify_message", route_query)  # <-- FIXED
graph_builder.add_edge("general_query", END)
graph_builder.add_edge("coding_query", "coding_validate_query")
graph_builder.add_edge("coding_validate_query", END)

# compiling the graph
graph = graph_builder.compile()

def main():
    user = input(" > ")
    _state = {
        "query": user,
        "llm_result": None,
        "accuracy_percentage": None,
        "is_coding_question": None,
    }
    graph_result = graph.invoke(_state)
    print("Graph_Result: ", graph_result)

main()
