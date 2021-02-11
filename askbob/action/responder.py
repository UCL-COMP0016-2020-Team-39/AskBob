from typing import Any, Dict, Text
from rasa.utils.endpoints import EndpointConfig
from rasa.core.agent import Agent
import requests


class ResponseService:
    """An interface for a response service, which produces responses for text queries."""

    def is_ready(self) -> bool:
        return True

    async def handle(self, query: str, sender: str = "askbob"):
        raise NotImplementedError(
            "The response service has not been implemented.")


def yielder(m) -> Dict[Text, Any]:
    if "text" in m:
        return {"text": m["text"]}
    elif "image" in m:
        return {"image": m["image"]}
    elif "custom" in m:
        return {"custom": m["custom"]}
    else:
        return {"other": m}
        # NOTE: buttons are not supported


class RasaResponseService(ResponseService):

    agent: Agent

    def __init__(self, model_dir: str = "data/rasa/models") -> None:
        # Action Server
        import sys
        import subprocess
        self.action_server = subprocess.Popen(
            [sys.executable, "-m", "askbob.action.server"])

        # Main Rasa Model
        from rasa.model import get_latest_model
        model_path = get_latest_model(model_dir)
        endpoint = EndpointConfig("http://localhost:5055/webhook")
        self.agent = Agent.load(model_path, action_endpoint=endpoint)

    def __del__(self):
        self.action_server.terminate()

    def is_ready(self) -> bool:
        return self.agent.is_ready()

    async def handle(self, query: str, sender: str = "askbob"):
        for m in await self.agent.handle_text(text_message=query, sender_id=sender):
            yield yielder(m)


class HTTPResponseService(ResponseService):

    endpoint: str

    def __init__(self, endpoint_base) -> None:
        self.endpoint = endpoint_base + "/webhooks/rest/webhook"

    async def handle(self, query, sender="askbob"):
        r = requests.post(self.endpoint, json={
            "sender": sender,
            "message": query
        }).json()

        for m in r:
            yield yielder(m)
