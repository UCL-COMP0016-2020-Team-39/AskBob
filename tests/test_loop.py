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
async def test_error_missing_listener(caplog):
    config = configparser.ConfigParser()
    config.read('tests/files/config.ini')
    del config['Listener']

    await interactive_loop(args, config, responder)

    assert "ERROR" in [record.levelname for record in caplog.records]


@pytest.mark.asyncio
async def test_error_missing_model(caplog):
    config = configparser.ConfigParser()
    config.read('tests/files/config.ini')
    del config['Listener']['model']

    await interactive_loop(args, config, responder)

    assert "ERROR" in [record.levelname for record in caplog.records]


@pytest.mark.asyncio
async def test_error_missing_tts(caplog):
    config = configparser.ConfigParser()
    config.read('tests/files/config.ini')
    del config['TTS']

    await interactive_loop(args, config, responder)

    assert "ERROR" in [record.levelname for record in caplog.records]


@pytest.mark.asyncio
async def test_error_missing_voice_id(caplog):
    config = configparser.ConfigParser()
    config.read('tests/files/config.ini')
    del config['TTS']

    await interactive_loop(args, config, responder)

    assert "ERROR" in [record.levelname for record in caplog.records]


@pytest.mark.asyncio
async def test_error_transcriber_creation(caplog):
    args = make_argument_parser().parse_args(['-f', 'nonexistent file.wav'])

    await interactive_loop(args, config, responder)

    assert "ERROR" in [record.levelname for record in caplog.records]


@pytest.mark.asyncio
async def test_one(capsys):
    await interactive_loop(args, config, responder)

    captured = capsys.readouterr()
    assert captured.out.splitlines()[0:2] == [
        "Listening (press Ctrl-C to exit).", "== this is a test"]


@pytest.mark.asyncio
async def test_loop_concierge(capsys):
    from askbob.action.responder import ResponseService

    class ConciergeResponseService(ResponseService):
        async def handle(self, query: str, sender: str = "askbob"):
            yield {
                "custom": {
                    "Response": "concierge",
                    "Steps": [
                        "foo",
                        "bar"
                    ]
                }
            }

    responder = ConciergeResponseService()
    await interactive_loop(args, config, responder)

    captured = capsys.readouterr()
    assert captured.out.splitlines() == ["Listening (press Ctrl-C to exit).", "== this is a test",
                                         "=> concierge", "===> foo", "===> bar"]
