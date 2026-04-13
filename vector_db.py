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
    vectors = model.encode(chunks)

    points = []
    for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
        points.append(
        PointStruct(
            id=i,
            vector=vector.tolist(),
            payload={"text": chunk}
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

def search(query):
    query_vector = model.encode(query).tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=3
    )

    return [point.payload["text"] for point in results.points]