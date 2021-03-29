@echo off

python -m pip install -U pip setuptools wheel askbob

python -m spacy download en_core_web_md

python -m askbob --setup
