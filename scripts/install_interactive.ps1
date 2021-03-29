python -m pip install -U pip setuptools wheel

Invoke-WebRequest "https://download.lfd.uci.edu/pythonlibs/w4tscw6k/PyAudio-0.2.11-cp37-cp37m-win_amd64.whl" -OutFile "PyAudio-0.2.11-cp37-cp37m-win_amd64.whl"

python -m pip install PyAudio-0.2.11-cp37-cp37m-win_amd64.whl

python -m pip install -U askbob[interactive]

python -m spacy download en_core_web_md

mkdir -Force data

Invoke-WebRequest "https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.pbmm" -OutFile "data/deepspeech-0.9.1-models.pbmm"
Invoke-WebRequest "https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.scorer" -OutFile "data/deepspeech-0.9.1-models.scorer"

python -m askbob --setup
