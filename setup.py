from setuptools import setup, find_packages
from os import path

# README
with open(path.join(path.abspath(path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='askbob',
      version='0.0.2',
      description='A customisable, federated, privacy-safe voice assistant deployable on low-power devices.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/UCL-COMP0016-2020-Team-39/AskBob',
      author='Jeremy Lo Ying Ping',
      author_email='jeremylo2001@googlemail.com',
      packages=find_packages(),
      install_requires=[
          "numpy~=1.17.0",
          "spacy~=2.2.4",
          "rasa[spacy]~=2.2.9",
          "sanic~=20.9.0",
          "coloredlogs~=10.0"
      ],
      extras_require={
          "docs": [
              "sphinx~=3.4.3",
              "recommonmark~=0.7.1",
              "sphinx-rtd-theme~=0.5.1"
          ],
          "voice": [
              "deepspeech~=0.9.3",
              "halo~=0.0.18",
              "scipy>=1.1.0",
              "pyaudio~=0.2.11",
              "pyttsx3~=2.90",
              "webrtcvad~=2.0.10"
          ],
          "test": [
              "pytest~=6.2.1",
              "pytest-cov~=2.11.1"
          ]
      },
      include_package_data=True,
      zip_safe=False)
