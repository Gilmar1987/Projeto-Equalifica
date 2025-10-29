# accessibility/whisper_service.py
import whisper

_model = None

def get_model():
    global _model
    if _model is None:
        _model = whisper.load_model("base")
    return _model

def transcribe_audio(audio_path: str) -> str:
    model = get_model()
    result = model.transcribe(audio_path, language="pt", fp16=False)
    return result["text"].strip()