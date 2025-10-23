import sounddevice as sd
import numpy as np
import queue
import webrtcvad
import noisereduce as nr
from scipy import signal
from collections import deque

fs = 16000
blocksize = 1024
q = queue.Queue()
vad = webrtcvad.Vad(3)  

ENERGY_THRESHOLD = 0.015  
MIN_SPEECH_DURATION = 0.5  
SILENCE_DURATION = 1.0  

class SpeechDetector:
    def __init__(self):
        self.speech_frames = deque(maxlen=int(MIN_SPEECH_DURATION * fs / blocksize))
        self.silence_frames = 0
        self.is_speaking = False
        self.noise_level = 0.01
        
    def calculate_energy(self, audio):
        return np.sqrt(np.mean(audio**2))
    
    def update_noise_level(self, audio):
        energy = self.calculate_energy(audio)
        self.noise_level = 0.95 * self.noise_level + 0.05 * energy
    
    def is_speech_energy(self, audio):
        energy = self.calculate_energy(audio)
        return energy > max(ENERGY_THRESHOLD, self.noise_level * 3)

def is_speech(audio_block, detector):
    if not detector.is_speech_energy(audio_block):
        return False
    
    pcm_data = (audio_block * 32767).astype(np.int16).tobytes()
    frame_length = 480  
    speech_frames = 0
    total_frames = 0
    
    for i in range(0, len(pcm_data), frame_length*2):
        frame = pcm_data[i:i+frame_length*2]
        if len(frame) < frame_length*2:
            break
        total_frames += 1
        if vad.is_speech(frame, sample_rate=fs):
            speech_frames += 1
    
    return total_frames > 0 and (speech_frames / total_frames) >= 0.7

def preprocess_audio(audio_np, noise_sample=None):
    
    if noise_sample is not None:
        audio_np = nr.reduce_noise(
            y=audio_np, 
            sr=fs,
            y_noise=noise_sample,
            stationary=True,
            prop_decrease=0.8
        )
    else:
        audio_np = nr.reduce_noise(y=audio_np, sr=fs, stationary=True)
    
    sos = signal.butter(4, 100, 'hp', fs=fs, output='sos')
    audio_np = signal.sosfilt(sos, audio_np)
    
    sos_bp = signal.butter(3, [300, 3000], 'bp', fs=fs, output='sos')
    audio_np = signal.sosfilt(sos_bp, audio_np)
    
    max_val = np.max(np.abs(audio_np))
    if max_val > 0:
        audio_np = audio_np / max_val
    
    return audio_np.astype(np.float32)

def audio_callback(indata, frames, time_info, status):
    if status:
        print(status)
    q.put(indata.copy())

def stream_microPhone(stt_function, buffer_seconds=2, noise_profile_duration=3):
    buffer = []
    speech_buffer = []
    max_buffer_len = int(buffer_seconds * fs / blocksize)
    detector = SpeechDetector()
    noise_profile = []
    
    print("\n" + "="*60)
    print("NOISE CALIBRATION")
    print("="*60)
    print(f"Please remain SILENT for {noise_profile_duration} seconds...")
    print("This helps the system learn background noise.")
    print("="*60 + "\n")
    
    with sd.InputStream(samplerate=fs, channels=1,
                        blocksize=blocksize,
                        callback=audio_callback):
        try:
            noise_blocks = int(noise_profile_duration * fs / blocksize)
            for i in range(noise_blocks):
                block = q.get()
                noise_profile.append(block)
                if (i+1) % 5 == 0:
                    print(f"Calibrating... {i+1}/{noise_blocks}")
            
            noise_sample = np.concatenate(noise_profile, axis=0).flatten()
            
            detector.noise_level = detector.calculate_energy(noise_sample)
            
            print("\n" + "="*60)
            print(f"Calibration complete!")
            print(f"  Background noise level: {detector.noise_level:.4f}")
            print(f"  Speech threshold: {max(ENERGY_THRESHOLD, detector.noise_level * 3):.4f}")
            print("="*60)
            print("\nListening for speech...")
            print("Press Ctrl+C to stop.\n")
            
            silence_blocks = 0
            max_silence_blocks = int(SILENCE_DURATION * fs / blocksize)
            
            while True:
                audio_block = q.get()
                audio_flat = audio_block.flatten()
                
                if not detector.is_speaking:
                    detector.update_noise_level(audio_flat)
                
                buffer.append(audio_block)
                if len(buffer) > max_buffer_len:
                    buffer.pop(0)

                if is_speech(audio_flat, detector):
                    silence_blocks = 0
                    if not detector.is_speaking:
                        detector.is_speaking = True
                        speech_buffer = buffer.copy()
                        print("Speech detected...", end='', flush=True)
                    else:
                        speech_buffer.append(audio_block)
                else:
                    if detector.is_speaking:
                        silence_blocks += 1
                        speech_buffer.append(audio_block)
                        
                        if silence_blocks >= max_silence_blocks:
                            print(" Processing...")
                            detector.is_speaking = False
                            silence_blocks = 0
                            
                            audio_np = np.concatenate(speech_buffer, axis=0).flatten()
                            
                            if detector.calculate_energy(audio_np) > ENERGY_THRESHOLD:
                                audio_proc = preprocess_audio(audio_np, noise_sample)
                                
                                text = stt_function(audio_proc)
                                if text.strip() != "" and len(text.strip()) > 2:
                                    print(f"Transcription: {text}\n")
                                else:
                                    print("No clear speech detected\n")
                            else:
                                print("Audio too quiet\n")
                            
                            speech_buffer = []

        except KeyboardInterrupt:
            print("\n\nStopped listening.")
        except Exception as e:
            print(f"\nError: {e}")