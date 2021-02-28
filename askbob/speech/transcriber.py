import datetime
from typing import Optional
import deepspeech
import enum
import logging
import numpy as np
import os

from askbob.speech.listener.listener import UtteranceService


class TranscriptionEvent(enum.Enum):
    """An enum representing utterance-related events."""
    START_UTTERANCE = 1
    END_UTTERANCE = 2


class Transcriber:
    """The transcriber performs speech-to-text on captured utterances spoken by the user."""

    def __init__(self, model: str, scorer: str, us: UtteranceService, save_path: Optional[str] = None):
        # Load the DeepSpeech model
        self.model = self.init_deepspeech(model, scorer)

        # Utterance service
        self.us = us
        self.save_path = save_path

    def init_deepspeech(self, model_path: str, scorer_path: str = "") -> deepspeech.Model:
        """Initialises the DeepSpeech model.

        Args:
            model_path (str): The path to the DeepSpech model.
            scorer_path (str, optional): The path to an external scorer. Defaults to "".

        Returns:
            deepspeech.Model: The DeepSpeech model.
        """

        logging.info("Initialising DeepSpeech model: %s", scorer_path)

        model = deepspeech.Model(model_path)
        if scorer_path:
            logging.info("Enabling the external scorer: %s", scorer_path)
            model.enableExternalScorer(scorer_path)

        return model

    def transcribe(self):
        """Transcribes spoken words.

        Yields:
            TranscriptionEvent: Whether the utterance has started or ended.
            str: The transcribed phrase spoken by the user.
        """

        if not self.us:
            return

        if self.save_path:
            os.makedirs(self.save_path, exist_ok=True)

        stream_context = self.model.createStream()
        wav_data = bytearray()
        last_event = None
        try:
            for utterance in self.us.utterances():
                if utterance is not None:
                    if last_event != TranscriptionEvent.START_UTTERANCE:
                        logging.debug("Utterance started.")
                        last_event = TranscriptionEvent.START_UTTERANCE
                        yield last_event, None

                    stream_context.feedAudioContent(
                        np.frombuffer(utterance, np.int16))

                    if self.save_path:
                        wav_data.extend(utterance)
                else:
                    logging.debug("Utterence ended.")

                    text = stream_context.finishStream()
                    if text and self.save_path:
                        self.us.write_wav(os.path.join(self.save_path, datetime.datetime.now().strftime(
                            "%Y-%m-%d_%H-%M-%S - " + text + ".wav")), wav_data)

                    last_event = TranscriptionEvent.END_UTTERANCE
                    yield last_event, text

                    if self.save_path:
                        wav_data = bytearray()

                    stream_context = self.model.createStream()
        except KeyboardInterrupt:
            return
