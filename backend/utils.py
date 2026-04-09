import ffmpeg
import os
import whisper

model = whisper.load_model("base")

def extract_audio(video_path, audio_path):
    try:
        (
            ffmpeg
            .input(video_path)
            .output(audio_path, format='mp3')
            .run(overwrite_output=True)
        )
        return audio_path
    except Exception as e:
        print("Error extracting audio:", e)
        return str(e)
    
def transcribe_audio(audio_path):
    try:
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        print("Error transcribing audio:", e)
        return str(e)