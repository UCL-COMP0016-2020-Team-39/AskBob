# AskBob

**AskBob** is an easily customisable, completely federated voice assistant deployable on low-power devices.

## Docker (for use as a server only)

If you are only using **AskBob** as a server (headlessly), then you can do this using Docker with the `Dockerfile` provided.

### Installation

Build the container using the following command:
```bash
$ docker build -t askbob .
```

You can specify a config.json file in the same directory as this README.md file to train off using a docker build argument as in the following command:
```bash
$ docker build --build-arg ASKBOB_SETUP_CONFIG=default_config.json -t askbob .
```

### Usage

The **AskBob** server can then be launched using the following command:
```bash
$ docker run -it --rm -p 8000:8000 askbob
```

## Local use (for all modes of use)

First, ensure you have Python 3.7 and `pip` installed on your system. Pip may be installed using the following command:
```bash
$ curl https://bootstrap.pypa.io/get-pip.py | sudo python
```
On Linux, you must ensure you have the right Python dev package installed, e.g. `python3.7-dev` on Ubuntu.

Next, ensure that your versions of `pip`, `setuptools` and `wheel` are up to date.
```bash
$ python -m pip install -U pip setuptools wheel
```

### Installation

Dependencies shared across all **AskBob** utilisation modes (interactive mode, voiceless RESTful web API server or voice-enabled RESTful web API server) are installed by the default **AskBob** package wit no extras, as are the components required to run **AskBob** as a voiceless (i.e. with no speech-to-text capabilities) RESTful web API server.

The latest release of **AskBob** may be installed from the Python Package Index using the following command:
```bash
$ python -m pip install askbob
```

Alternatively, the very latest version of **AskBob** can also be installed from this GitHub repository using the following commands (assuming `git` is installed):
```bash
$ git clone https://github.com/UCL-COMP0016-2020-Team-39/AskBob
$ cd AskBob
$ python -m pip install -e .
```

The **AskBob** Python package may be installed with multiple 'extras' depending on the use case:
- voice
- interactive
- docs
- test

A compatible `spaCy` model must then be installed (the `en_core_web_md` model is recommended) with the following command:
```bash
$ python -m spacy download en_core_web_md
```

#### Voice-enabled RESTful web API server mode

To run the **AskBob** server in voice-enabled mode, where WAV files of speech can be uploaded to the **AskBob** server on the `/voicequery` endpoint from which **AskBob** will produce a JSON response, additional voice-related dependencies must be installed.

When installing **AskBob** from PyPi, use the following command:
```bash
$ python -m pip install askbob[voice]
```

When installing **AskBob** from a clone of this GitHub repository, instead use the following command:
```bash
$ python -m pip install .[voice]
```

#### Interactive mode

To run **AskBob** as a voice assistant interactively (i.e. with speech transcription and synthesis enabled), additional interactive mode-related dependencies must be installed.

Firstly, the cross-platform audio API `portaudio` must be installed on your machine.

On Ubuntu, the `portaudio` binary can be installed with the following command:
```bash
$ sudo apt install portaudio19-dev python3-pyaudio
```

On Windows, you may have to compile the `portaudio` binary used by **AskBob** from source.

**Note**: Christoph Gohlke maintains unofficial Windows binaries for Python extension packages, including for [PyAudio](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio), which may be installed using `pip install INSERT_BINARY_LOCATION`.


If you get an `ImportError` related to `_portaudio`, then you may have to additionally run the following commands (assuming you have `git` installed):
```bash
$ git clone https://people.csail.mit.edu/hubert/git/pyaudio.git
$ cd pyaudio
$ sudo python setup.py install
```

With `portaudio` properly installed, you will then need to find a [mozilla\DeepSpeech](https://github.com/mozilla/DeepSpeech/releases/tag/v0.9.3)-compatible model and scorer to be used with **AskBob**. Once downloaded, place the files in the `data` folder and update the runtime configuration file (`config.ini`) with the correct file paths to the model and scorer, respectively.

You may also have to modify the configuration depending on the text-to-speech voices made available by your operating system, which may be found using the following sequence of Python commands:
```python
>>> import pyttsx3
>>> print(*[voice.id for voice in pyttsx3.init().getProperty('voices')])
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0 HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-GB_HAZEL_11.0 HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0
```

Once this is done, the additional **AskBob** `interactive` extra must be installed. When installing **AskBob** from PyPi, use the following command:
```bash
$ python -m pip install askbob[interactive]
```

When installing **AskBob** from a clone of this GitHub repository, instead use the following command:
```bash
$ python -m pip install .[interactive]
```

### Training

The **AskBob** voice assistant must be trained before use (this is done automatically when building the Docker container). This may be done using the following command:

```bash
$ python -m askbob --setup [optional additional configuration JSON file]
```

**AskBob** will train off installed plugins only if no additional configuration JSON file is provided.

The following command is an example of how **AskBob** could be trained:
```bash
$ python -m askbob --setup default_config.json
```

### Usage

**AskBob** may be run interactively with the following command:
```bash
$ python -m askbob
```

You can specify your own runtime config.ini file with the -c flag:
```bash
$ python -m askbob -c config.ini
```

**AskBob** can also be run as a standalone server with the following command:
```bash
$ python -m askbob -s
```

The `/voicequery` endpoint where a single-channel (preferably 16kHz) WAV file (<10MiB in size) may be uploaded is enableable by starting **AskBob** with the `-v` flag in addition to the `-s` flag, i.e.
```bash
$ python -m askbob -s -v
```

Further help is available using the `--help` flag.
```bash
$ python -m askbob --help
usage: __main__.py [-h] [-c CONFIG] [-w SAVEPATH] [-f FILE] [-d DEVICE]
                   [-r RATE] [-s] [-v] [--setup [SETUP]]

**AskBob**: a customisable voice assistant.

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
  -s, --serve           Run AskBob as a server instead of interactively.
  -v, --voice           Enable speech transcription in server mode.
  --setup [SETUP]       Setup AskBob from the configuration JSON file
                        provided.
```

## Runtime Configuration Options

### Listener
```ini
[Listener]
model = data/deepspeech-0.9.1-models.pbmm
scorer = data/deepspeech-0.9.1-models.scorer
aggressiveness = 1
```

- `model` is the location to the DeepSpeech model
- `scorer` is the optional location to an external DeepSpeech scorer
- `aggressiveness` is an optional integer (1 if unspecified) between 0 and 3 (inclusive) determining how aggressive the voice activity detector is at filtering out non-speech (0 is the least aggressive, 3 is the most aggressive).

### TTS
```ini
[TTS]
voice_id = HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-GB_HAZEL_11.0
```
- `voice_id` is the ID of the voice to be used by the pyttsx3 text-to-speech library. If this voice cannot be found, the default voice is used. You may need to install voices in a manner consistent with your operating system before this may work.

### Rasa
```ini
[Rasa]
config = data/rasa/config
model = data/rasa/models
```

- `config` is the location where **AskBob** will generate a set of Rasa YAML config files
- `model` is the location where **AskBob** will place trained Rasa models

It is highly recommended that you do not change either of these values.

### Server
```ini
[Server]
host = 0.0.0.0
port = 8000
```

- `host` is the host **AskBob** will bind to when being run in server mode (0.0.0.0 if unspecified)
- `post` is the post **AskBob** will bind to when being run in server mode (8000 if unspecified)

### Plugins
```ini
[Plugins]
location = plugins
action_server_port = 5055
summary = data/summary.json
```

- `plugins` is the location of the plugins folder (this cannot contain any spaces and must be a valid python module name)
- `action_server_port` is the port used by the internal Rasa custom action server (5055 if unspecified)
- `summary` is the location at which a summary of installed voice assistant skills is stored at build-time

It is highly recommended that you do not change any of these values.

## Documentation

Before attempting to generate the documentation, ensure that the documentation tools are installed.
```bash
$ python -m pip install .[docs]
```

The documentation can be generated using the following commands on Linux:
```bash
$ cd docs
$ make html
```

On Windows in a bash-style terminal, use the `make.bat` file provided in the following way:
```bash
> cd docs
> ./make.bat html
```

The generated documentation will be found at `docs/_build/html`.

In order to generate the full documentation, ensure all project dependencies are installed (all extras, i.e. voice, interactive, etc).

## Tests

Before running any tests, ensure that **AskBob** was installed with the `test` extra to additionally include the testing suite.
```bash
$ python -m pip install -e .[test]
```

Tests may be run with the following command:
```bash
$ python -m pytest
```

Code coverage may be generated using the following command:
```bash
$ python -m pytest --cov-report html:cov_html --cov=askbob tests/
```

**Note**: you must have `pytest-cov` installed to generate the coverage report (this will have been installed if you ran `python setup.py install test`).
