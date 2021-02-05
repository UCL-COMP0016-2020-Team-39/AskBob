from rasa.utils.endpoints import EndpointConfig
from rasa.core.agent import Agent
import requests


class ResponseService:

    def is_ready(self) -> bool:
        return True

    async def handle(self, query: str, sender: str = "askbob"):
        raise NotImplementedError(
            "The response service has not been implemented.")


class RasaResponseService(ResponseService):

    agent: Agent

    def __init__(self, model_dir: str = "data/rasa/models") -> None:
        # Action Server
        import sys
        import subprocess
        subprocess.Popen([sys.executable, "-m", "askbob.action.server"])

        # Main Rasa Model
        from rasa.model import get_latest_model
        model_path = get_latest_model(model_dir)
        endpoint = EndpointConfig("http://localhost:5055/webhook")
        self.agent = Agent.load(model_path, action_endpoint=endpoint)

    def is_ready(self) -> bool:
        return self.agent.is_ready()

    async def handle(self, query: str, sender: str = "askbob"):
        for m in await self.agent.handle_text(text_message=query, sender_id=sender):
            if "text" in m:
                yield m["text"]
            elif "image" in m:
                yield "[Image] " + m["image"]
            else:
                yield "[Media]"


class HTTPResponseService(ResponseService):

    def __init__(self, endpoint_base):
        self.endpoint = endpoint_base + "/webhooks/rest/webhook"

    async def handle(self, query, sender="askbob"):
        r = requests.post(self.endpoint, json={
            "sender": sender,
            "message": query
        }).json()

        for m in r:
            if "text" in m:
                yield m["text"]

            if "image" in m:
                yield "[Image] " + m["image"]
