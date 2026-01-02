import whisper
import os
import tempfile
import numpy as np

# Ensure ffmpeg is found
try:
    import imageio_ffmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    ffmpeg_dir = os.path.dirname(ffmpeg_exe)
    if ffmpeg_dir not in os.environ["PATH"]:
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]
except ImportError:
    pass

class WhisperTranscriber:
    def __init__(self, model_size="base"):
        print(f"Loading Whisper model: {model_size}...")
        self.model = whisper.load_model(model_size)
        print("Whisper model loaded.")

    def transcribe(self, audio_bytes: bytes) -> str:
        """
        Transcribes audio bytes using Whisper.
        Args:
            audio_bytes: The raw audio data (webm/wav/mp3 etc.)
        Returns:
            The transcribed text.
        """
        # Save bytes to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name

        try:
            # Clinical prompt to guide the model and reduce hallucinations
            prompt = "A medical encounter. The patient is describing symptoms: chest pain, shortness of breath, dizziness, heart palpitations."
            
            # Transcribe with optimized parameters
            result = self.model.transcribe(
                temp_audio_path, 
                fp16=False,
                initial_prompt=prompt,
                condition_on_previous_text=False, # Helps reduce repetitions/hallucinations
                temperature=0.0 # More deterministic
            )
            return result.get("text", "").strip()
        except Exception as e:
            print(f"Transcription Error: {e}")
            return f"Error transcribing audio: {e}"
        finally:
            # Clean up
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)

if __name__ == "__main__":
    # Test (requires an actual audio file)
    transcriber = WhisperTranscriber()
    # print(transcriber.transcribe(open("test.webm", "rb").read()))
