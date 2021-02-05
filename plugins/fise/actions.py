from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import askbob.plugin


@askbob.plugin.action("fise", "change_background")
class ActionChangeBackground(Action):
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_custom_json({
            "type": "change_background"
        })

        return []


@askbob.plugin.action("fise", "call")
class ActionCallUser(Action):
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        callee = next(tracker.get_latest_entity_values("PERSON"), None)

        if not callee:
            dispatcher.utter_message("This person could not be called.")
            return []

        dispatcher.utter_message(f"Calling {callee}.")
        dispatcher.utter_custom_json({
            "type": "call_user",
            "callee": callee
        })

        return []
