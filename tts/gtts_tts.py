from gtts import gTTS


def text_to_speech_gtts(text, out_path, lang='en'):
    tts = gTTS(text=text, lang=lang)
    tts.save(out_path)
    return out_path
