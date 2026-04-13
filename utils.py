import os
import requests
import time

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

UPLOAD_URL = "https://api.assemblyai.com/v2/upload"
TRANSCRIPT_URL = "https://api.assemblyai.com/v2/transcript"

headers = {
    "authorization": ASSEMBLYAI_API_KEY
}


# 🔥 Step 1: Upload file to AssemblyAI
def upload_file(file_path):
    with open(file_path, "rb") as f:
        response = requests.post(UPLOAD_URL, headers=headers, data=f)
    return response.json()["upload_url"]


# 🔥 Step 2: Request transcription
def request_transcript(audio_url):
    json_data = {
        "audio_url": audio_url
    }
    response = requests.post(TRANSCRIPT_URL, json=json_data, headers=headers)
    return response.json()["id"]


# 🔥 Step 3: Poll for result
def get_transcript(transcript_id):
    url = f"{TRANSCRIPT_URL}/{transcript_id}"

    while True:
        response = requests.get(url, headers=headers)
        data = response.json()

        if data["status"] == "completed":
            return data["text"]

        elif data["status"] == "error":
            return "Error in transcription"

        time.sleep(3)


# 🔥 MAIN FUNCTION
def transcribe_audio(file_path):
    audio_url = upload_file(file_path)
    transcript_id = request_transcript(audio_url)
    transcript = get_transcript(transcript_id)

    return transcript


# 🔥 OPTIONAL (skip ffmpeg for now)
def extract_audio(video_path, audio_path):
    return video_path


def split_text(text, chunk_size=300):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks