import pytest
import configparser

from askbob.server import make_app
from askbob.action.responder import ResponseService
from askbob.server.routes import get_intent_examples
from askbob.server.voice import voice_routes
from sanic import Sanic


class FixedResponseService(ResponseService):
    async def handle(self, query: str, sender: str = "askbob"):
        yield {
            "text": "Hello"
        }


def test_get_intent_examples():
    plugin_config = {
        "intents": [
            {
                "intent_id": "ask_hello",
                "examples": [
                    "Hello",
                    "Hi",
                    "Hey",
                    "Howdy",
                    "Howdy, partner"
                ]
            },
            {
                "intent_id": "ask_goodbye",
                "examples": [
                    "Goodbye",
                    "Good bye",
                    "Bye",
                    "Bye bye",
                    "See you",
                    "See you later",
                    "In a bit!",
                    "Catch you later!"
                ]
            }
        ]
    }

    assert get_intent_examples(plugin_config, "ask_hello") == [
        "Hello",
        "Hi",
        "Hey",
        "Howdy",
        "Howdy, partner"
    ]


def test_get_intent_examples_empty():
    assert get_intent_examples({
        "intents": []
    }, "") == []


def test_voice_routes_missing_listener():
    config = configparser.ConfigParser()

    with pytest.raises(RuntimeError):
        voice_routes(None, FixedResponseService(), config)


def test_voice_routes_missing_model():
    config = configparser.ConfigParser()
    config["Listener"] = {"foo": "bar"}

    with pytest.raises(RuntimeError):
        voice_routes(None, FixedResponseService(), config)


def test_voice_routes_invalid_model():
    config = configparser.ConfigParser()
    config["Listener"] = {"model": "foo"}

    with pytest.raises(RuntimeError):
        voice_routes(None, FixedResponseService(), config)


@pytest.yield_fixture
def app():
    config = configparser.ConfigParser()
    config["Plugins"] = {
        "Summary": "tests/files/summary.json"
    }

    config["Server"] = {
        "cors_origins": "*"
    }

    config["Listener"] = {
        "model": "data/deepspeech-0.9.1-models.pbmm",
        "scorer": "data/deepspeech-0.9.1-models.scorer"
    }

    yield make_app(FixedResponseService(), config, True)


@pytest.fixture
def test_cli(loop, app, sanic_client):
    return loop.run_until_complete(sanic_client(app, timeout=20))


async def test_server_homepage(test_cli):
    res = await test_cli.get('/')
    assert res.status_code == 200


async def test_server_skills(test_cli):
    res = await test_cli.get('/skills')
    assert res.status_code == 200

    res_json = res.json()
    assert "plugins" in res_json
    assert "skills" in res_json


async def test_server_post_query_no_sender_or_message(test_cli):
    res = await test_cli.post('/query')
    assert res.status_code == 200

    res_json = res.json()
    assert "error" in res_json


async def test_server_post_query_no_sender(test_cli):
    res = await test_cli.post('/query', data={
        "message": "hello"
    })
    assert res.status_code == 200

    res_json = res.json()
    assert "error" in res_json


async def test_server_post_query_no_message(test_cli):
    res = await test_cli.post('/query', data={
        "sender": "tester"
    })
    assert res.status_code == 200

    res_json = res.json()
    assert "error" in res_json


async def test_server_post_query_non_printable_message(test_cli):
    res = await test_cli.post('/query', data={
        "sender": "tester",
        "message": "\r"
    })
    assert res.status_code == 200

    res_json = res.json()
    assert "error" in res_json


async def test_server_post_query_non_printable_sender(test_cli):
    res = await test_cli.post('/query', data={
        "sender": "\r",
        "message": "hello"
    })
    assert res.status_code == 200

    res_json = res.json()
    assert "error" in res_json


async def test_server_post_query(test_cli):
    res = await test_cli.post('/query', data={
        "sender": "tester",
        "message": "hello"
    })
    assert res.status_code == 200

    res_json = res.json()
    assert "messages" in res_json
    assert res_json["messages"] == [{
        "text": "Hello"
    }]


async def test_server_get_query(test_cli):
    res = await test_cli.get('/query?sender=tester&message=hello')
    assert res.status_code == 200

    res_json = res.json()
    assert "messages" in res_json
    assert res_json["messages"] == [{
        "text": "Hello"
    }]


async def test_server_voice_query_no_sender(test_cli):
    res = await test_cli.post('/voicequery')
    assert res.status_code == 200

    res_json = res.json()
    assert "error" in res_json


async def test_server_voice_query_non_printable_sender(test_cli):
    res = await test_cli.post('/voicequery', data={
        "sender": "\r"
    })
    assert res.status_code == 200

    res_json = res.json()
    assert "error" in res_json


async def test_server_voice_query_no_speech_file(test_cli):
    res = await test_cli.post('/voicequery', data={
        "sender": "tester"
    })
    assert res.status_code == 200

    res_json = res.json()
    assert "error" in res_json


async def test_server_voice_query(test_cli):
    res = await test_cli.post('/voicequery', data={
        "sender": "tester"
    }, files={
        "speech": open('tests/this is a test.wav', 'rb')
    })
    assert res.status_code == 200

    res_json = res.json()
    assert "messages" in res_json
    assert res_json["messages"] == [{
        "text": "Hello"
    }]


async def test_server_voice_query_error_empty(test_cli):
    res = await test_cli.post('/voicequery', data={
        "sender": "tester"
    }, files={
        "speech": open('tests/empty.wav', 'rb')
    })
    assert res.status_code == 200

    res_json = res.json()
    assert "error" in res_json


async def test_server_voice_query_empty_response(test_cli):
    res = await test_cli.post('/voicequery', data={
        "sender": "tester"
    }, files={
        "speech": open('tests/radumono.wav', 'rb')
    })
    assert res.status_code == 200

    res_json = res.json()
    assert "messages" in res_json
    assert res_json["messages"] == []


async def test_server_voice_query_too_many(test_cli):
    res = await test_cli.post('/voicequery', data={
        "sender": "tester"
    }, files=[
        ('speech', open('tests/this is a test.wav', 'rb')),
        ('speech', open('tests/this is a test.wav', 'rb'))
    ])
    assert res.status_code == 200

    res_json = res.json()
    assert "error" in res_json


async def test_server_voice_query_bad_wav_channels(test_cli):
    res = await test_cli.post('/voicequery', data={
        "sender": "tester"
    }, files={
        "speech": open('tests/dualchannel.wav', 'rb')
    })
    assert res.status_code == 200

    res_json = res.json()
    assert "error" in res_json


async def test_server_voice_query_bad_wav_wrong_filetype(test_cli):
    res = await test_cli.post('/voicequery', data={
        "sender": "tester"
    }, files={
        "speech": open('tests/dualchannel.mp3', 'rb')
    })
    assert res.status_code == 200

    res_json = res.json()
    assert "error" in res_json


async def test_server_voice_query_bad_wav_too_long(test_cli):
    res = await test_cli.post('/voicequery', data={
        "sender": "tester"
    }, files={
        "speech": open('tests/long.wav', 'rb')
    })
    assert res.status_code == 200

    res_json = res.json()
    assert "error" in res_json
