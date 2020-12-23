import datetime
import deepspeech
import enum
import logging
import numpy as np
import os

from askbob.audio.listener import UtteranceService


class TranscriptionEvent(enum.Enum):
    START_UTTERANCE = 1
    END_UTTERANCE = 2


class Transcriber:

    def __init__(self, model: str, scorer: str, aggressiveness: int,
                 device_index: int, rate: int, filename: str, save_path: str):
        # Load the DeepSpeech model
        self.model = self.init_deepspeech(model, scorer)

        # Start audio
        self.us = UtteranceService(aggressiveness=aggressiveness,
                                   device_index=device_index,
                                   input_rate=rate,
                                   filename=filename)

        self.save_path = save_path

    def init_deepspeech(self, model_path, scorer_path=""):
        logging.info("Initialising DeepSpeech model: %s", scorer_path)

        if os.path.isdir(model_path):
            model_path = os.path.join(model_path, 'output_graph.pb')
            scorer_path = os.path.join(model_path, scorer_path)

        model = deepspeech.Model(model_path)
        if scorer_path:
            logging.info("Enabling the external scorer: %s", scorer_path)
            model.enableExternalScorer(scorer_path)

        return model

    def transcribe(self):
        if self.save_path:
            os.makedirs(self.save_path, exist_ok=True)

        stream_context = self.model.createStream()
        wav_data = bytearray()
        last_event = None
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
                if text:
                    if self.save_path:
                        self.us.write_wav(os.path.join(self.save_path, datetime.datetime.now().strftime(
                            "%Y-%m-%d_%H-%M-%S - " + text + ".wav")), wav_data)

                last_event = TranscriptionEvent.END_UTTERANCE
                yield last_event, text

                if self.save_path:
                    wav_data = bytearray()

                stream_context = self.model.createStream()
