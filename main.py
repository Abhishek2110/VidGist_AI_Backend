import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from utils import extract_audio, transcribe_audio, split_text
from vector_db import create_collection, store_embeddings, search
from rag_pipeline import generate_answer

app = FastAPI()

# ✅ CORS (good as it is)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
AUDIO_DIR = "audio"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)


@app.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    video_path = os.path.join(UPLOAD_DIR, file.filename)
    audio_path = os.path.join(AUDIO_DIR, file.filename + ".mp3")

    try:
        # 🔥 Save video
        with open(video_path, "wb") as f:
            f.write(await file.read())

        # 🔥 Extract audio
        extract_audio(video_path, audio_path)

        # 🔥 Transcribe (REAL)
        transcript = transcribe_audio(audio_path)

        # 🔥 Vector DB
        create_collection()
        chunks = split_text(transcript)
        store_embeddings(chunks)

        return {
            "filename": file.filename,
            "transcript": transcript
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 🔥 Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)

        if os.path.exists(audio_path):
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