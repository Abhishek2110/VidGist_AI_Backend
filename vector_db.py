import os
import uuid
import time
import requests
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_URL = os.getenv("HUGGING_FACE_URL")

if QDRANT_URL:
    # Production (Qdrant Cloud)
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )
else:
    # Local development
    client = QdrantClient(
        host="localhost",
        port=6333
    )

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
    if COLLECTION_NAME not in [c.name for c in client.get_collections().collections]:
        client.create_collection(
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