import os
import uuid
import time
import requests
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

client = QdrantClient(":memory:")

COLLECTION_NAME = "vidgist"

HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

HF_URL = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"

headers = {
    "Authorization": f"Bearer {HF_API_KEY}"
}


def get_embedding(text):
    for _ in range(3):
        try:
            response = requests.post(
                HF_URL,
                headers=headers,
                json={"inputs": [text[:1000]]},
                timeout=15
            )

            if not response.text:
                time.sleep(2)
                continue

            try:
                data = response.json()
            except:
                time.sleep(2)
                continue

            if isinstance(data, dict) and "error" in data:
                time.sleep(3)
                continue

            return data[0]

        except Exception as e:
            time.sleep(2)

    # fallback
    return [0.0] * 384


def create_collection():
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )


def store_embeddings(chunks):
    points = []

    for chunk in chunks:
        vector = get_embedding(chunk)

        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
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