import os
import requests
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

client = QdrantClient(":memory:")

COLLECTION_NAME = "vidgist"

HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

HF_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"

headers = {
    "Authorization": f"Bearer {HF_API_KEY}"
}


# 🔥 Real embedding function
def get_embedding(text):
    response = requests.post(
        HF_URL,
        headers=headers,
        json={"inputs": text}
    )

    return response.json()[0]


def create_collection():
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )


def store_embeddings(chunks):
    points = []

    for i, chunk in enumerate(chunks):
        vector = get_embedding(chunk)

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
    query_vector = get_embedding(query)

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=3
    )

    return [point.payload["text"] for point in results.points]