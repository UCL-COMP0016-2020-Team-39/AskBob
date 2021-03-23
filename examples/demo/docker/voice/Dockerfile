FROM python:3.7-slim

ARG DEBIAN_FRONTEND=noninteractive
ARG ASKBOB_SETUP_CONFIG=.

RUN apt update && apt install -y build-essential git

WORKDIR /askbob

RUN python -m pip install -U pip setuptools wheel askbob[voice]
RUN python -m spacy download en_core_web_md

RUN mkdir data

COPY ./plugins plugins
COPY ./*.ini .
COPY ./*.json .
COPY ./data data

RUN python -m askbob --setup $ASKBOB_SETUP_CONFIG

ENTRYPOINT python -m askbob -s -v

EXPOSE 8000
