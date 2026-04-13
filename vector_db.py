from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

client = QdrantClient(":memory:")

COLLECTION_NAME = "vidgist"


# 🔥 Simple lightweight embedding (no ML model)
def fake_embedding(text):
    # Create simple numeric vector from text
    return [float(ord(c) % 10) for c in text[:50]] + [0.0] * (384 - min(len(text), 50))


def create_collection():
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )


def store_embeddings(chunks):
    points = []

    for i, chunk in enumerate(chunks):
        vector = fake_embedding(chunk)

        points.append(
            PointStruct(
                id=i,
                vector=vector,
                payload={"text": chunk}
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )


def search(query):
    query_vector = fake_embedding(query)

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=3
    )

    return [point.payload["text"] for point in results.points]