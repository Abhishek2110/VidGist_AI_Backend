import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from utils import transcribe_audio, split_text, clean_filename
from vector_db import create_collection, store_embeddings, search
import uuid
from agents import multi_agent_pipeline

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
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    
    video_id = str(uuid.uuid4())
    video_path = None

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


        # Transcribe video
        transcript = transcribe_audio(video_path)

        # Vector DB
        create_collection()
        chunks = split_text(transcript)
        store_embeddings(chunks, video_id)

        return {
            "video_id": video_id,
            "filename": clean_name,
            "transcript": transcript
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if video_path and os.path.exists(video_path):
            os.remove(video_path)


@app.get("/search")
def search_query(q: str):
    try:
        results = search(q)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ask")
def ask_question(q: str, video_id: str):
    try:
        answer = multi_agent_pipeline(q, video_id)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))