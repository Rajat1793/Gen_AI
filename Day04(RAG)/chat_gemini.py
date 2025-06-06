from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from openai import OpenAI
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print(api_key)

# load the env files
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
# load_dotenv()

# vector embedding model
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004"
)

# reading the data from DB
vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name = "learning_ vectors",
    embedding=embedding_model,
)
# take user query
query = input("user > ")

# vector similarity search in DB
search_results = vector_db.similarity_search(
    query=query
)

context = "\n\n\n".join([f"Page content: {result.page_content}\n Page Number: {result.metadata['page_label']} \n File Location: {result.metadata['source']}"for result in search_results])
# System Prompt
SYSTEM_PROMPT = f"""
    You are a helpfull AI Assistant who answer user query based on the available context
    retrieved from a PDF file along with page_contents and page number.

    You should only ans the user based on the following context and navigate the user
    to open the right page number to know more.

    Context:
    {context}
"""
message = {'role': 'system', 'content': SYSTEM_PROMPT }
response = client.chat.completions.create(
    model='gemini-2.0-flash',
    messages=[
        {'role': 'user', 'content': query}
    ]
)
print(f"🤖 : {response.choices[0].message.content}")