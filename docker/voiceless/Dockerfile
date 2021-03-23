FROM python:3.7-slim

ARG DEBIAN_FRONTEND=noninteractive
ARG ASKBOB_SETUP_CONFIG=.

RUN apt update && apt install -y build-essential git

WORKDIR /askbob/installation
COPY ./askbob /askbob/installation/askbob
COPY ./README.md .
COPY ./MANIFEST.in .
COPY ./setup.py .

RUN python -m pip install -U pip setuptools wheel
RUN python -m pip install -e .
RUN python -m spacy download en_core_web_md

WORKDIR /askbob/build

RUN mkdir data

COPY ./plugins plugins
COPY ./config.ini config.ini
COPY ./*.json ./
COPY ./data data

RUN python -m askbob --setup $ASKBOB_SETUP_CONFIG

ENTRYPOINT python -m askbob -s

EXPOSE 8000
