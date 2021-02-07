FROM python:3.7-slim

ARG DEBIAN_FRONTEND=noninteractive
ARG ASKBOB_SETUP_CONFIG=.

WORKDIR /askbob

COPY ./askbob askbob
COPY ./plugins plugins
COPY ./requirements requirements
COPY ./config.ini .
COPY ./*.json .

RUN python -m pip install -U pip setuptools wheel

RUN python -m pip install --no-cache-dir -r requirements/common.txt
RUN python -m spacy download en_core_web_md
RUN python -m spacy link en_core_web_md en

RUN python -m askbob --setup $ASKBOB_SETUP_CONFIG

ENTRYPOINT python -m askbob -s

EXPOSE 8000
