from askbob.util import make_argument_parser


"""
Ask Bob: a customisable voice assistant.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        The configuration file.
  -w SAVEPATH, --savepath SAVEPATH
                        Save .wav files of utterences to a given directory.
  -f FILE, --file FILE  Read from a .wav file instead of the microphone.
  -d DEVICE, --device DEVICE
                        The device input index (int) as given by
                        pyaudio.PyAudio.get_device_info_by_index(). Default:
                        pyaudio.PyAudio.get_default_device().
  -r RATE, --rate RATE  The input device sample rate (your device might
                        require 44100Hz). Default: 16000.
  -s, --serve           Run Ask Bob as a server instead of interactively.
  --setup [SETUP]       Setup Ask Bob from the configuration JSON file
                        provided.
"""


def test_argparser_empty():
    parser = make_argument_parser()
    args = parser.parse_args([])

    assert args.config == 'config.ini'
    assert args.device == None
    assert args.rate == 16000
    assert args.serve == False


def test_argparser_serve_short():
    parser = make_argument_parser()
    args = parser.parse_args(["-s"])

    assert args.config == 'config.ini'
    assert args.device == None
    assert args.rate == 16000
    assert args.serve == True


def test_argparser_serve_long():
    parser = make_argument_parser()
    args = parser.parse_args(["--serve"])

    assert args.config == 'config.ini'
    assert args.device == None
    assert args.rate == 16000
    assert args.serve == True


def test_argparser_rate():
    parser = make_argument_parser()
    args = parser.parse_args(["-r", "48000"])

    assert args.config == 'config.ini'
    assert args.device == None
    assert args.rate == 48000
    assert args.serve == False


def test_argparser_device():
    parser = make_argument_parser()
    args = parser.parse_args(["--device", "1"])

    assert args.config == 'config.ini'
    assert args.device == 1
    assert args.rate == 16000
    assert args.serve == False


def test_argparser_device():
    parser = make_argument_parser()
    args = parser.parse_args(["-c", "qwerty.ini"])

    assert args.config == 'qwerty.ini'
    assert args.device == None
    assert args.rate == 16000
    assert args.serve == False
