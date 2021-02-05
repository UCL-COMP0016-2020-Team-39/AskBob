from .main import main
from .setup import setup


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description="Ask Bob: a customisable voice assistant.")

    parser.add_argument('-c', '--config', default="config.ini",
                        help="The configuration file.")

    parser.add_argument('-w', '--savepath',
                        help="Save .wav files of utterences to a given directory.")

    parser.add_argument('-f', '--file',
                        help="Read from a .wav file instead of the microphone.")

    parser.add_argument('-d', '--device', type=int, default=None,
                        help="The device input index (int) as given by pyaudio.PyAudio.get_device_info_by_index(). Default: pyaudio.PyAudio.get_default_device().")

    parser.add_argument('-r', '--rate', type=int, default=16000,
                        help=f"The input device sample rate (your device might require 44100Hz). Default: 16000.")

    parser.add_argument('-s', '--serve', default=False, action='store_true',
                        help="Run Ask Bob as a server instead of interactively.")

    parser.add_argument('--setup', const=".", nargs="?",
                        help="Setup Ask Bob from the configuration JSON file provided.")

    args = parser.parse_args()

    import configparser
    config = configparser.ConfigParser()
    config.read(args.config)

    if args.setup:
        setup(args, config)
    else:
        main(args, config)
