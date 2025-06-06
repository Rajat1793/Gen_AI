from dotenv import load_dotenv
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore

load_dotenv()
# Load the file
file_path = Path(__file__).parent / 'nodejs.pdf'
loader = PyPDFLoader(file_path)
docs = loader.load()
print(docs[5])

# Chunking
text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size=500,
    chunk_overlap=100,
)
split_doc = text_splitter.split_documents(documents=docs)

# vector embedding model
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004"
)

# using the [embedding_model] create a embedding of [split_doc] and store it in DB
vector_store = QdrantVectorStore.from_documents(
    documents=split_doc,
    url="http://localhost:6333",
    collection_name = "learning_ vectors",
    embedding=embedding_model,
    force_recreate = True
)

print('indexing of the doc done.')
