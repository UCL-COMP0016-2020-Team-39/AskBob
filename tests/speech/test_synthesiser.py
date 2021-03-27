from askbob.speech.synthesiser import TextToSpeechService


def test_synthesiser_no_voice_id():
    TextToSpeechService().say("Test.")


def test_synthesiser_with_nonexistent_voice_id():
    TextToSpeechService("nonexistent").say("Test.")


def test_synthesiser_with_existent_voice_id():
    import pyttsx3

    tts = pyttsx3.init()
    voice_id = tts.getProperty('voices')[0].id

    TextToSpeechService(voice_id).say("Test.")


def test_synthesiser_no_voices(caplog):
    import pyttsx3

    tts = pyttsx3.init()
    voices = tts.getProperty('voices')
    tts.setProperty('voices', [])

    TextToSpeechService("nonexistent")

    assert "WARNING" in [record.levelname for record in caplog.records]
    tts.setProperty('voices', voices)
