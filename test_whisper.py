import os
import sys

# Ensure core is in path
sys.path.append(os.getcwd())

# Add ffmpeg to PATH dynamically (copying logic from server.py)
try:
    import imageio_ffmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    ffmpeg_dir = os.path.dirname(ffmpeg_exe)
    if ffmpeg_dir not in os.environ["PATH"]:
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]
    print(f"FFmpeg found at: {ffmpeg_exe}")
except ImportError:
    print("imageio-ffmpeg not found")

from core.transcriber import WhisperTranscriber
import numpy as np
import tempfile
import wave

def create_dummy_wav(path):
    # Create a 1-second silent mono wav file
    with wave.open(path, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(16000)
        f.writeframes(np.zeros(16000, dtype=np.int16).tobytes())

def test_whisper():
    print("Initializing WhisperTranscriber...")
    transcriber = WhisperTranscriber(model_size="base")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        create_dummy_wav(tmp.name)
        tmp_path = tmp.name
        
    try:
        print(f"Transcribing dummy audio from {tmp_path}...")
        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()
        
        result = transcriber.transcribe(audio_bytes)
        print(f"Transcription result: '{result}'")
        print("Whisper is working correctly in the terminal!")
    except Exception as e:
        print(f"Whisper test failed: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    test_whisper()
