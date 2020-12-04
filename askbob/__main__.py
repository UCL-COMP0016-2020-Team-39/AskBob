import halo
import logging
from askbob.audio.voice import VoiceAudioService
from askbob.audio.transcriber import Transcriber, TranscriptionEvent


def main(args):
    import configparser

    config = configparser.ConfigParser()
    config.read(args.config)
    voice = config['Voice']

    transcriber = Transcriber(model=voice['model'], scorer=voice['scorer'], aggressiveness=voice.getint('aggressiveness'),
                              device_index=args.device, rate=args.rate, filename=args.file, save_path=args.savepath)

    spinner = halo.Halo(spinner='line')

    print("Listening (press Ctrl-C to exit).")
    for state, text in transcriber.transcribe():
        if state == TranscriptionEvent.START_UTTERANCE:
            spinner.start()
        elif state == TranscriptionEvent.END_UTTERANCE:
            spinner.stop()

            if text:
                print("=> %s" % text)
        else:
            logging.error("Unknown transcription event: " + state)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description="Stream from microphone to DeepSpeech using VAD")

    parser.add_argument('-c', '--config', required=True,
                        help="The configuration file.")

    parser.add_argument('-w', '--savepath',
                        help="Save .wav files of utterences to a given directory.")

    parser.add_argument('-f', '--file',
                        help="Read from a .wav file instead of the microphone.")

    parser.add_argument('-d', '--device', type=int, default=None,
                        help="The device input index (int) as given by pyaudio.PyAudio.get_device_info_by_index(). Default: pyaudio.PyAudio.get_default_device().")

    parser.add_argument('-r', '--rate', type=int, default=VoiceAudioService.sample_rate,
                        help=f"The input device sample rate (your device might require 44100Hz). Default: {VoiceAudioService.sample_rate}.")

    main(parser.parse_args())
