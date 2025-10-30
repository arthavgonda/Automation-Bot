import torch
import numpy as np
import torchaudio
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

try:
    from config import PRIMARY_LANGUAGE
except ImportError:
    PRIMARY_LANGUAGE = "english"

if torch.cuda.is_available():
    device = "cuda"
elif torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"

model_name = "openai/whisper-medium"
processor = WhisperProcessor.from_pretrained(model_name)
model = WhisperForConditionalGeneration.from_pretrained(model_name).to(device)

model.config.forced_decoder_ids = None

print(f"✓ Whisper initialized with PRIMARY_LANGUAGE: {PRIMARY_LANGUAGE}")

def stt_whisper(audio_np):
    audio_np = audio_np / np.max(np.abs(audio_np))
    input_features = processor(audio_np, sampling_rate=16000, return_tensors="pt").input_features.to(device)
    predicted_ids = model.generate(
        input_features,
        language=PRIMARY_LANGUAGE,
        task="transcribe",
        max_length=448,
        num_beams=5,
        temperature=0.0,
        compression_ratio_threshold=1.35,
        logprob_threshold=-1.0,
        no_repeat_ngram_size=3,
    )
    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
    transcription = transcription.strip()
    suspicious_ranges = [
        (0x1780, 0x17FF),
        (0x0E00, 0x0E7F),
        (0x0600, 0x06FF),
        (0x4E00, 0x9FFF),
        (0x3040, 0x309F),
        (0x30A0, 0x30FF),
    ]
    for char in transcription:
        code = ord(char)
        for start, end in suspicious_ranges:
            if start <= code <= end:
                print(f"⚠️  Detected non-Hindi/English script, likely wrong detection. Ignoring.")
                return ""
    return transcription