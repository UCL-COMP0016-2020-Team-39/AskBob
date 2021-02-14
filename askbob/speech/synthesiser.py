import logging
from typing import Optional
import pyttsx3


class TextToSpeechService:
    """The TextToSpeechService is responsible for speech synthesis."""

    tts: pyttsx3.Engine

    def __init__(self, voice_id: Optional[str] = None) -> None:
        self.tts = pyttsx3.init()

        if voice_id:
            if voice_id in [voice.id for voice in self.tts.getProperty('voices')]:
                self.tts.setProperty('voice', voice_id)
                logging.info("Using voice: " + voice_id + ".")
            else:
                logging.error(
                    "Using default voice due to unknown model: " + voice_id + ".")
        else:
            logging.info("Using default voice - no voice_id given.")

    def say(self, text: str) -> None:
        """Converts the text into speech and outputs the audio.

        Args:
            text (str): The text to say.
        """

        self.tts.say(text)
        self.tts.runAndWait()
