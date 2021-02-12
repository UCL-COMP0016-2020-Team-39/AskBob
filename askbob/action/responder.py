from typing import Any, Dict, Text
from rasa.utils.endpoints import EndpointConfig
from rasa.core.agent import Agent
import requests


class ResponseService:
    """An interface for a response service, which produces responses for text queries."""

    def is_ready(self) -> bool:
        """Returns whether the response service is ready to accept queries.

        Returns:
            bool: Whether or not the response server is ready to accept queries.
        """
        return True

    async def handle(self, query: str, sender: str = "askbob"):
        """Handles a queries and produces a response.

        Args:
            query (str): The user's query.
            sender (str, optional): A unique sender identifier. Defaults to "askbob".

        Raises:
            NotImplementedError: This is just an interface - please use a concrete implementation!
        """

        raise NotImplementedError(
            "The response service has not been implemented.")


def yielder(m: Dict[Text, Any]) -> Dict[Text, Any]:
    """A helper function to generate correct message responses shared between ResponseService implementations.

    Args:
        m (Dict[Text, Any]): The message returned by Rasa.

    Returns:
        Dict[Text, Any]: An AskBob-formatted response.
    """

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
    """A ResponseService that uses Rasa running locally to respond to queries."""

    agent: Agent

    def __init__(self, model_dir: str = "data/rasa/models", plugins_location="plugins", plugins_port=5055) -> None:
        """Initialises the RasaResponseService.

        The Rasa actions server required for custom actions to function is automatically started when this class is initialised.

        Args:
            model_dir (str, optional): The location of the Rasa model to load. Defaults to "data/rasa/models".
        """

        # Action Server
        import sys
        import subprocess
        self.action_server = subprocess.Popen(
            [sys.executable, "-m", "askbob.action.server", plugins_location, str(plugins_port)])

        # Main Rasa Model
        from rasa.model import get_latest_model
        model_path = get_latest_model(model_dir)
        endpoint = EndpointConfig("http://localhost:5055/webhook")
        self.agent = Agent.load(model_path, action_endpoint=endpoint)

    def __del__(self):
        """Terminates the Rasa action service when this object is destroyed as it is no longer needed."""
        self.action_server.terminate()

    def is_ready(self) -> bool:
        return self.agent.is_ready()

    async def handle(self, query: str, sender: str = "askbob"):
        for m in await self.agent.handle_text(text_message=query, sender_id=sender):
            yield yielder(m)


class HTTPResponseService(ResponseService):
    """A ResponseService that uses Rasa's HTTP webhook to respond to queries."""

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
