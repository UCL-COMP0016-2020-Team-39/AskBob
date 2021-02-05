from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import askbob.plugin
import requests


@askbob.plugin.action("puns", "fetch_joke")
class ActionFetchJoke(Action):

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="One joke, coming right up!")

        r = requests.get(url="https://icanhazdadjoke.com/",
                         headers={"Accept": "application/json"}).json()

        dispatcher.utter_message(text=r['joke'])

        return []
