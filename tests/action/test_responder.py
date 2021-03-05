
from askbob.action.responder import RasaResponseService, ResponseService, yielder
import pytest

# Loads the askbob-plugin-skeleton puns model
responder = RasaResponseService(
    'tests/files/models', 'tests.files.plugins', 5055)


def test_yielder_text():
    response = yielder({
        "text": "foobar"
    })

    assert "text" in response
    assert response["text"] == "foobar"


def test_yielder_image():
    response = yielder({
        "image": "foobar"
    })

    assert "image" in response
    assert response["image"] == "foobar"


def test_yielder_custom():
    response = yielder({
        "custom": {
            "foo": "bar"
        }
    })

    assert "custom" in response
    assert response["custom"] == {
        "foo": "bar"
    }


def test_yielder_other():
    response = yielder({
        "unknown response": {
            "foo": "bar"
        }
    })

    assert "other" in response
    assert response["other"] == {
        "unknown response": {
            "foo": "bar"
        }
    }


@pytest.mark.asyncio
async def test_response_service_interface():
    responder = ResponseService()
    assert responder.is_ready()
    with pytest.raises(NotImplementedError):
        await responder.handle("test", "askbob_tester")


@pytest.mark.asyncio
async def test_rasa_ready():
    assert responder.is_ready()


@pytest.mark.asyncio
async def test_rasa_hello():

    for message in [
        "Hello",
        "Hi",
        "Hey",
        "Howdy",
        "Howdy, partner"
    ]:
        i = 0
        async for response in responder.handle(message, "askbob_tester"):
            assert "text" in response
            assert response["text"] in [
                "Hi there!",
                "Hey - nice to meet you!",
                "Hey there!"
            ]
            i += 1

        assert i == 1


@pytest.mark.asyncio
async def test_rasa_bye():

    for message in [
        "Goodbye",
        "Good bye",
        "Bye",
        "Bye bye",
        "See you",
        "See you later",
        "In a bit!",
        "Catch you later!"
    ]:
        i = 0
        async for response in responder.handle(message, "askbob_tester"):
            assert "text" in response
            assert response["text"] in [
                "See you later!",
                "Bye!",
                "In a while, crocodile!"
            ]
            i += 1

        assert i == 1


@pytest.mark.asyncio
async def test_rasa_termination():
    responder.__del__()
