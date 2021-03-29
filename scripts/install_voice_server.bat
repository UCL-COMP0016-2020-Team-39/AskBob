@echo off

python -m pip install -U pip setuptools wheel askbob[voice]

python -m spacy download en_core_web_md

if not exist "data" mkdir "data"

python -m askbob --setup
