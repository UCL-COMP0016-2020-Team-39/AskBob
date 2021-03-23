apt update && apt install -y build-essential git wget

python -m pip install -U pip setuptools wheel askbob
python -m spacy download en_core_web_md

mkdir -p data

python -m askbob --setup
