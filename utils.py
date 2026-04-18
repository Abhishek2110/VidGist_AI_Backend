import os
import re
import requests
import subprocess

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

DEEPGRAM_URL = "https://api.deepgram.com/v1/listen"

headers = {
    "Authorization": f"Token {DEEPGRAM_API_KEY}",
}

def extract_audio(video_path, audio_path):
    command = [
        "ffmpeg",
        "-i", video_path,
        "-vn",
        "-acodec", "mp3",
        "-ac", "1",
        "-ar", "16000",
        "-y",
        audio_path
    ]

    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return audio_path

def transcribe_audio(audio_path):

    try:
        with open(audio_path, "rb") as f:
            response = requests.post(
                DEEPGRAM_URL,
                headers={**headers, "Content-Type": "audio/mp3"},
                params={
                    "model": "nova-2",
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

    except Exception as e:
        return "Error: Transcription failed"


def split_text(text, chunk_size=300):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks

def clean_filename(filename):
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)