"""
Text-to-Speech Module
- Uses pyttsx3 (FREE, offline) for demo
- Can upgrade to ElevenLabs/Amazon Polly for human-like voice later
"""
import os


def speak_text(text: str, save_to_file: str = None) -> str:
    """Convert text to speech"""
    try:
        import pyttsx3
        engine = pyttsx3.init()

        # Configure voice
        engine.setProperty('rate', 160)    # Speed (words per minute)
        engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)

        # Try to use a female voice (sounds more professional for calls)
        voices = engine.getProperty('voices')
        if len(voices) > 1:
            engine.setProperty('voice', voices[1].id)  # Usually female

        if save_to_file:
            engine.save_to_file(text, save_to_file)
            engine.runAndWait()
            return save_to_file
        else:
            engine.say(text)
            engine.runAndWait()
            return "spoken"

    except Exception as e:
        return f"[TTS Error: {str(e)}] - Text was: {text}"


def speak_text_gtts(text: str, filename: str = "output.mp3") -> str:
    """Alternative: Use Google TTS (needs internet, but better quality)"""
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang='en', slow=False)
        filepath = f"./data/{filename}"
        tts.save(filepath)
        return filepath
    except Exception as e:
        return f"[gTTS Error: {str(e)}]"
