import os
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from utils import extract_audio, transcribe_audio

app = FastAPI()

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

    # Save video
    with open(video_path, "wb") as f:
        f.write(await file.read())

    # Extract audio
    audio_path = os.path.join(AUDIO_DIR, file.filename + ".mp3")
    extract_audio(video_path, audio_path)

    # Transcribe
    transcript = transcribe_audio(audio_path)

    return {
        "filename": file.filename,
        "transcript": transcript
    }