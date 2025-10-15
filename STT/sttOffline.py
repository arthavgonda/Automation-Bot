import os
import json
import numpy as np
from vosk import Model, KaldiRecognizer

vosk_model_path = os.path.join(os.path.dirname(__file__), "vosk-model-en-us-0.22")
if not os.path.exists(vosk_model_path):
    raise Exception(f"Vosk model folder not found at {vosk_model_path}")

model = Model(vosk_model_path)
recognizer = KaldiRecognizer(model, 16000)

def stt_vosk(audio_np):
    data_bytes = (audio_np * 32767).astype(np.int16).tobytes()
    if recognizer.AcceptWaveform(data_bytes):
        result = json.loads(recognizer.Result())
    else:
        result = json.loads(recognizer.PartialResult())
    return result.get("text", "").strip()