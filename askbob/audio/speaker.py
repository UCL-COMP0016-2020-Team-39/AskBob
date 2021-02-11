import logging
import pyttsx3


class SpeechService:
    """The SpeechService is responsible for speech synthesis.
    """

    tts: pyttsx3.Engine

    def __init__(self, voice_id: str) -> None:
        self.tts = pyttsx3.init()

        if voice_id in [voice.id for voice in self.tts.getProperty('voices')]:
            self.tts.setProperty('voice', voice_id)
            logging.info("Using voice: " + voice_id + ".")
        else:
            logging.error(
                "Using default voice due to unknown model: " + voice_id + ".")

    def say(self, text: str) -> None:
        """Converts the text into speech and outputs the audio.

        Args:
            text (str): The text to say
        """

        self.tts.say(text)
        self.tts.runAndWait()
