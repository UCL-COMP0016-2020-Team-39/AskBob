import logging
from typing import Optional
import pyttsx3


class TextToSpeechService:
    """The TextToSpeechService is responsible for speech synthesis."""

    tts: pyttsx3.Engine

    def __init__(self, voice_id: Optional[str] = None) -> None:
        self.tts = pyttsx3.init()

        voices = [voice.id for voice in self.tts.getProperty('voices')]
        if not voices:
            logging.warning(
                "No voices were found - you may be missing additional dependencies on your system before you will hear any voice output.")
            return

        logging.info("Found voices: {}.".format(", ".join(voices)))

        if voice_id:
            if voice_id in voices:
                self.tts.setProperty('voice', voice_id)
                logging.info(f"Using voice: {voice_id}.")
            else:
                logging.warning(
                    f"Using the default voice due to an unknown voice_id: {voice_id}.")
        else:
            logging.info(
                "Using the default voice as no voice_id was provided.")

    def say(self, text: str) -> None:
        """Converts the text into speech and outputs the audio.

        Args:
            text (str): The text to say.
        """

        self.tts.say(text)
        self.tts.runAndWait()
