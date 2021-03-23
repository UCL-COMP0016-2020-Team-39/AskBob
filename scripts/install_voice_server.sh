apt update && apt install -y build-essential git wget

python -m pip install -U pip setuptools wheel askbob[voice]
python -m spacy download en_core_web_md

mkdir -p data

wget -O data/deepspeech-0.9.1-models.pbmm https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.pbmm
wget -O data/deepspeech-0.9.1-models.scorer https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.scorer

python -m askbob --setup
