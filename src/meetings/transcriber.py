import whisper
import os
from dotenv import load_dotenv

load_dotenv()

model = None

def get_model():
    global model
    if model is None:
        print("Loading Whisper model...")
        model = whisper.load_model("base")
        print("✓ Whisper model loaded")
    return model


def transcribe(audio_path):
    if not os.path.exists(audio_path):
        print(f"  ✗ File not found: {audio_path}")
        return None

    print(f"Transcribing: {audio_path}")
    m      = get_model()
    result = m.transcribe(audio_path)
    text   = result["text"].strip()
    print(f"  ✓ Transcribed {len(text)} characters")
    return text


if __name__ == "__main__":
    print("Whisper transcriber ready.")
    print("Usage: from src.meetings.transcriber import transcribe")
    print("       text = transcribe('path/to/audio.mp3')")