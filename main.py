import os
import re
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from utils import transcribe_audio, split_text, extract_audio, clean_filename
from vector_db import create_collection, store_embeddings, search
from rag_pipeline import generate_answer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_SIZE = 30 * 1024 * 1024

UPLOAD_DIR = "uploads"
AUDIO_DIR = "audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)


@app.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    video_path = None
    audio_path = None

    try:
        contents = await file.read()

        # File size check
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large (max 30MB)")

        clean_name = clean_filename(file.filename)
        video_path = os.path.join(UPLOAD_DIR, clean_name)

        # Save video
        with open(video_path, "wb") as f:
            f.write(contents)

        # Extract audio
        base_name = os.path.splitext(clean_name)[0]
        audio_path = os.path.join(AUDIO_DIR, base_name + ".mp3")
        extract_audio(video_path, audio_path)

        # Transcribe audio
        transcript = transcribe_audio(audio_path)

        # Vector DB
        create_collection()
        chunks = split_text(transcript)
        store_embeddings(chunks)

        return {
            "filename": clean_name,
            "transcript": transcript
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if video_path and os.path.exists(video_path):
            os.remove(video_path)

        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)


@app.get("/search")
def search_query(q: str):
    try:
        results = search(q)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ask")
def ask_question(q: str):
    try:
        answer = generate_answer(q)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))