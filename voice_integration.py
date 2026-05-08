"""
Voice Integration Module
Handles Speech-to-Text using Groq Whisper API.
"""
import os
import tempfile
from groq import Groq
from dotenv import load_dotenv
import pyttsx3

# Load API key (fallback for backend testing)
load_dotenv()
_default_api_key = os.getenv("GROQ_API_KEY")

class GroqManager:
    """Manages Groq API interactions for Whisper STT."""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or _default_api_key
        self.client = None
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                print(f"Groq Init Error: {e}")

    def transcribe(self, file_path):
        """Transcribe audio using Whisper."""
        if not self.client:
            return "Error: Groq API key is missing or invalid. Please check your settings."

        try:
            with open(file_path, "rb") as f:
                transcription = self.client.audio.transcriptions.create(
                    file=(os.path.basename(file_path), f, "audio/wav"),
                    model="whisper-large-v3-turbo",
                )
                return transcription.text if hasattr(transcription, "text") else str(transcription)
        except Exception as e:
            err_msg = str(e).lower()
            if "api_key" in err_msg or "401" in err_msg:
                return "Error: Invalid API key. Please verify your Groq key."
            print(f"STT Error: {e}")
            return f"Error: Transcription failed ({type(e).__name__})"

def get_whisper_model():
    """Return Groq's Whisper model."""
    return "whisper-large-v3-turbo"


def get_tts_model():
    """TTS is handled by pyttsx3 (local), not Groq."""
    return None


def speech_to_text(file_path, api_key=None):
    """
    Convert speech from audio file to text using Groq Whisper.
    """
    manager = GroqManager(api_key)
    return manager.transcribe(file_path)


def text_to_speech(text, lang="en", output_file=None):
    """
    Convert text to speech using pyttsx3.
    
    Args:
        text: Text to convert to speech
        lang: Language code (default: 'en')
        output_file: Optional path to save audio file
    
    Returns:
        Path to output file if specified, otherwise None.
    """
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        # Set speech properties
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        
        # Try to find a voice matching the language
        for voice in voices:
            try:
                if lang.lower() in str(voice.languages).lower() or lang.lower() in voice.id.lower():
                    engine.setProperty('voice', voice.id)
                    break
            except:
                pass
        
        if output_file:
            engine.save_to_file(text, output_file)
            engine.runAndWait()
            return output_file
        else:
            engine.say(text)
            engine.runAndWait()
            return None
    except Exception as e:
        print(f"TTS Error: {e}")
        return None
