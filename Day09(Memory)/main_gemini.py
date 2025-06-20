import os, json
# os.environ["POSTHOG_DISABLED"] = "true"

from mem0 import Memory
from dotenv import load_dotenv
from openai import OpenAI
from typing_extensions import TypedDict
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
# import google.generativeai as genai

# Load environment variables (for GEMINI_API_KEY)
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = OpenAI( 
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

config = {
    "version": "v1.1",
    "embedder": {
        "provider": "gemini",
        "config": {
            "api_key": api_key,
            "model": "models/text-embedding-004",
        }
    },
    "llm": {"provider": "gemini", "config": {"api_key": api_key, "model": "gemini-1.5-flash-8b"}},
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": "6333"
        }
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": "bolt://localhost:7687",
            "username": "neo4j",
            "password": "reform-william-center-vibrate-press-5829"
        }
    }
}

mem_client = Memory.from_config(config_dict=config)

def chat():
    while True:
        user_query = input("> ")
        # extracting the memories from Qdrant
        relevant_memories = mem_client.search(query=user_query, user_id="rajat")
        memories = [
            f"ID: {mem.get('id')} Memory: {mem.get('memory')}" for mem in relevant_memories.get("results")]
        print("Memories: ", memories)
        SYSTEM_PROMPT = f"""
        You are an memory aware assistant which responds to user with context.
        You are given with the past memories and facts about the user.
        
        Memories of user: {json.dumps(memories)}
        """
        result = client.chat.completions.create(
            model='gemini-1.5-flash-8b',
            messages=[{"role":"system", "content": SYSTEM_PROMPT},
                {'role': 'user', 'content': user_query}]
        )
        print(f" Content: {result.choices[0].message.content}")
        mem_client.add([
            {"role": "user", "content": user_query},
            {"role": "assistant","content": result.choices[0].message.content}
        ],user_id='rajat')
        
chat()
