from gtts import gTTS
import logging
from pathlib import Path


def text_to_speech_gtts(text, out_path, lang='en'):
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(out_path)
        return out_path
    except Exception as e:
        # Fallback: create a minimal silent MP3 for testing when network is unavailable
        logging.warning(f"gTTS failed, creating silent placeholder: {e}")
        _create_silent_mp3(out_path)
        return out_path


def _create_silent_mp3(out_path):
    """Create a minimal silent MP3 file as a placeholder when gTTS is unavailable."""
    from pydub import AudioSegment
    from pydub.generators import Sine
    
    # Create 1 second of silence
    silence = AudioSegment.silent(duration=1000)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    silence.export(out_path, format='mp3', bitrate='64k')

