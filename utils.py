import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
DEEPGRAM_URL = os.getenv("DEEPGRAM_URL")
DEEPGRAM_MODEL = os.getenv("DEEPGRAM_MODEL")

headers = {
    "Authorization": f"Token {DEEPGRAM_API_KEY}",
}

def transcribe_audio(file_path):

    with open(file_path, "rb") as f:
        response = requests.post(
            DEEPGRAM_URL,
            headers={
                **headers,
                "Content-Type": "video/mp4"
            },
            params={
                "model": DEEPGRAM_MODEL,
                "smart_format": "true"
            },
            data=f
        )

    data = response.json()

    transcript = data.get("results", {}) \
        .get("channels", [{}])[0] \
        .get("alternatives", [{}])[0] \
        .get("transcript", "")

    if not transcript:
        raise Exception("Empty transcript")

    return transcript


def split_text(text, chunk_size=300):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks

def clean_filename(filename):
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)