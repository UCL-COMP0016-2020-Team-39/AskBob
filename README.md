# AskBob
The AskBob voice assistant.

## Installation
You will need to find a [mozilla\DeepSpeech](https://github.com/mozilla/DeepSpeech/releases/tag/v0.9.2)-compatible model and scorer to be used with AskBob. Once downloaded, it is suggested that the files be placed in the `data` folder and the configuration file `config.ini` be updated with the correct file names.

Project dependencies may be installed by running the following commands:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_md
```

On Windows, you may be missing a `portaudio` binary used by Ask Bob, which may have be compiled from source.

**Note**: Christoph Gohlke maintains unofficial Windows binaries for Python extension packages, including for [PyAudio](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio), which may be installed using `pip install`.

You may have to modify the configuration depending on the voices available on your system, which may be found using the following sequence of Python commands:
```python
>>> import pyttsx3
>>> print(*[voice.id for voice in pyttsx3.init().getProperty('voices')])
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0 HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-GB_HAZEL_11.0 HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0
```

## Usage
Ask Bob may be run with the following command:
```bash
python -m askbob -c config.ini
```

Further help is available using the `--help` flag.
```bash
$ python -m askbob --help
usage: __main__.py [-h] -c CONFIG [-w SAVEPATH] [-f FILE] [-d DEVICE]
                   [-r RATE]

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
```

## Tests

Tests may be run with the following command:
```bash
$ python -m pytest
```
