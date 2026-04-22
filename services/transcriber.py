import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def transcribe_audio(file_path: str) -> str:
    with open(file_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file=audio_file,
            response_format="text"
        )
    return response