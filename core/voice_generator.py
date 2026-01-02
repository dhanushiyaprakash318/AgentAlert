from gtts import gTTS
import base64
import io
import os

class VoiceGenerator:
    def __init__(self, lang="en"):
        self.lang = lang

    def text_to_speech_base64(self, text: str) -> str:
        """
        Converts text to speech and returns it as a base64 encoded MP3 string.
        """
        if not text:
            return ""
            
        try:
            tts = gTTS(text=text, lang=self.lang)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            
            audio_base64 = base64.b64encode(fp.read()).decode('utf-8')
            return audio_base64
        except Exception as e:
            print(f"TTS Error: {e}")
            return ""

if __name__ == "__main__":
    generator = VoiceGenerator()
    b64 = generator.text_to_speech_base64("I have a severe chest pain")
    print(f"Generated {len(b64)} bytes of base64 audio.")
