import torch
import numpy as np
import torchaudio
from transformers import WhisperProcessor, WhisperForConditionalGeneration

if torch.cuda.is_available():
    device = "cuda"
elif torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"

model_name = "openai/whisper-medium"
processor = WhisperProcessor.from_pretrained(model_name)
model = WhisperForConditionalGeneration.from_pretrained(model_name).to(device)

def stt_whisper(audio_np):
    audio_np = audio_np / np.max(np.abs(audio_np))
    input_features = processor(audio_np, sampling_rate=16000, return_tensors="pt").input_features.to(device)
    predicted_ids = model.generate(input_features)
    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
    return transcription.strip()