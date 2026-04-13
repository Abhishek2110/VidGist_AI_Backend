from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer

client = QdrantClient(":memory:")

model = SentenceTransformer("all-MiniLM-L6-v2")

COLLECTION_NAME = "vidgist"

def create_collection():
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

def store_embeddings(chunks):
    pass

def search(query):
    return ["Demo response from system"]