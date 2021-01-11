import os
import halo
import logging

from askbob.audio.speaker import SpeechService
from askbob.audio.listener import UtteranceService
from askbob.audio.transcriber import Transcriber, TranscriptionEvent
from askbob.action.responder import ResponseService


def main(args):
    import configparser

    config = configparser.ConfigParser()
    config.read(args.config)

    if 'Listener' not in config:
        raise RuntimeError("No listener configuration provided.")

    if 'model' not in config['Listener']:
        raise RuntimeError("No listener model provided.")

    model_path = config['Listener']['model']
    scorer_path = config['Listener']['scorer'] if 'scorer' in config['Listener'] else ''

    if os.path.isdir(model_path):
        model_path = os.path.join(model_path, 'output_graph.pb')
        scorer_path = os.path.join(model_path, scorer_path)

    transcriber = Transcriber(model=model_path, scorer=scorer_path, aggressiveness=config['Listener'].getint(
        'aggressiveness', fallback=1), device_index=args.device, rate=args.rate, filename=args.file, save_path=args.savepath)

    speaker = SpeechService(config['Speaker']['voice_id'])

    responder = ResponseService(config['Rasa']['endpoint_base'])

    spinner = halo.Halo(spinner='line')

    print("Listening (press Ctrl-C to exit).")
    for state, text in transcriber.transcribe():
        if state == TranscriptionEvent.START_UTTERANCE:
            spinner.start()
        elif state == TranscriptionEvent.END_UTTERANCE:
            spinner.stop()

            if text:
                print("==", text)

                for response in responder.respond(text):
                    print("=>", response)
                    speaker.say(response)

        else:
            logging.error("Unknown transcription event: " + state)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description="Ask Bob: a customisable voice assistant.")

    parser.add_argument('-c', '--config', required=True,
                        help="The configuration file.")

    parser.add_argument('-w', '--savepath',
                        help="Save .wav files of utterences to a given directory.")

    parser.add_argument('-f', '--file',
                        help="Read from a .wav file instead of the microphone.")

    parser.add_argument('-d', '--device', type=int, default=None,
                        help="The device input index (int) as given by pyaudio.PyAudio.get_device_info_by_index(). Default: pyaudio.PyAudio.get_default_device().")

    parser.add_argument('-r', '--rate', type=int, default=UtteranceService.sample_rate,
                        help=f"The input device sample rate (your device might require 44100Hz). Default: {UtteranceService.sample_rate}.")

    main(parser.parse_args())
