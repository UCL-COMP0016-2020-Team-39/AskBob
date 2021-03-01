FROM python:3.7-slim

ARG DEBIAN_FRONTEND=noninteractive
ARG ASKBOB_SETUP_CONFIG=.

RUN apt update && apt install -y build-essential

WORKDIR /askbob

RUN mkdir data

COPY ./askbob askbob
COPY ./plugins plugins
COPY ./*.ini .
COPY ./*.json .
COPY ./README.md .
COPY ./MANIFEST.in .
COPY ./setup.py .
COPY ./data/*.pbmm data
COPY ./data/*.scorer data

RUN python -m pip install -U pip setuptools wheel

RUN python -m pip install -e .[voice]
RUN python -m spacy download en_core_web_md

RUN python -m askbob --setup $ASKBOB_SETUP_CONFIG

ENTRYPOINT python -m askbob -s -v

EXPOSE 8000
