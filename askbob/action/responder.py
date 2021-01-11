import requests


class ResponseService:

    def __init__(self, endpoint_base):
        self.endpoint = endpoint_base + "/webhooks/rest/webhook"

    def respond(self, query):
        r = requests.post(self.endpoint, json={
            "sender": "askbob",
            "message": query
        }).json()

        for m in r:
            if "text" in m:
                yield m["text"]

            if "image" in m:
                yield "[Image] " + m["image"]
