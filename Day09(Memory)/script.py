from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

client = QdrantClient(host="localhost", port=6333)

client.recreate_collection(
    collection_name="mem0",  # Replace with your actual collection name if different
    vectors_config=VectorParams(
        size=768,
        distance=Distance.COSINE
    )
)

print("✅ Qdrant collection recreated with 768-dimensional vectors.")
