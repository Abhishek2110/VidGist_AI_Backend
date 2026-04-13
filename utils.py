import os
import whisper

model = whisper.load_model("base")

def extract_audio(video_path, audio_path):
    # Temporary: skip extraction
    return video_path
    
def transcribe_audio(audio_path):
    try:
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        print("Error transcribing audio:", e)
        return str(e)
    
def split_text(text, chunk_size=300):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks