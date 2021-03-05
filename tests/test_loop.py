import configparser

import pytest
from askbob.action.responder import RasaResponseService
from askbob.loop import interactive_loop

from askbob.util import make_argument_parser
parser = make_argument_parser()
args = parser.parse_args(['-f', 'tests/this is a test.wav'])

config = configparser.ConfigParser()
config.read('tests/files/config.ini')

responder = RasaResponseService(
    'tests/files/models', 'tests.files.plugins', 5055)


@pytest.mark.asyncio
async def test_error_missing_listener():
    config = configparser.ConfigParser()
    config.read('tests/files/config.ini')
    del config['Listener']

    await interactive_loop(args, config, responder)


@pytest.mark.asyncio
async def test_error_missing_model():
    config = configparser.ConfigParser()
    config.read('tests/files/config.ini')
    del config['Listener']['model']

    await interactive_loop(args, config, responder)


@pytest.mark.asyncio
async def test_error_missing_tts():
    config = configparser.ConfigParser()
    config.read('tests/files/config.ini')
    del config['TTS']

    await interactive_loop(args, config, responder)


@pytest.mark.asyncio
async def test_error_missing_voice_id():
    config = configparser.ConfigParser()
    config.read('tests/files/config.ini')
    del config['TTS']

    await interactive_loop(args, config, responder)


@pytest.mark.asyncio
async def test_error_transcriber_creation():
    args = make_argument_parser().parse_args(['-f', 'nonexistent file.wav'])

    await interactive_loop(args, config, responder)


@pytest.mark.asyncio
async def test_one():
    await interactive_loop(args, config, responder)
