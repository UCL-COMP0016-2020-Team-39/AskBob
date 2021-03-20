from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import askbob.plugin


@askbob.plugin.action("time", "fetch_time")
class ActionFetchTime(Action):

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        from datetime import datetime

        dispatcher.utter_message(text="The time is {0}.".format(
            datetime.now().strftime("%H:%M")))

        return []
