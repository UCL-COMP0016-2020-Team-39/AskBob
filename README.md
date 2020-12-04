# AskBob
The AskBob voice assistant.

## Installation
You will need to find a [mozilla\DeepSpeech](https://github.com/mozilla/DeepSpeech/releases/tag/v0.9.2)-compatible model and scorer to be used with AskBob. Once downloaded, it is suggested that the files be placed in the `data` folder and the configuration file `config.ini` be updated with the correct file names.

Project dependencies may be installed by running the following command:
```bash
pip install -r requirements.txt
```

On Windows, you may be missing a `portaudio` binary used by Ask Bob, which may have be compiled from source.

**Note**: Christoph Gohlke maintains unofficial Windows binaries for Python extension packages, including for [PyAudio](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio), which may be installed using `pip install`.

## Usage
Ask Bob may be run with the following command:
```bash
python -m askbob -c config.ini
```
