
python -m pip install -U pip setuptools wheel askbob[voice]

python -m spacy download en_core_web_md

mkdir -Force data

Invoke-WebRequest "https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.pbmm" -OutFile "data/deepspeech-0.9.1-models.pbmm"
Invoke-WebRequest "https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.scorer" -OutFile "data/deepspeech-0.9.1-models.scorer"

python -m askbob --setup
