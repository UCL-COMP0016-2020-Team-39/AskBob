from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import askbob.plugin
import requests


@askbob.plugin.action("weather", "fetch_weather")
class ActionFetchWeather(Action):
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            gpe = next(tracker.get_latest_entity_values("GPE"), None)
            if gpe is None:
                raise RuntimeError("No GPE provided!")
        except:
            dispatcher.utter_message(
                text="I'm sorry - I don't know where that is!")
            return []

        r = requests.get(url="https://api.openweathermap.org/data/2.5/weather", params={
            "q": gpe,
            "units": "metric",
            "appid": "b6bea28b4b8e3d4ecf0355e92f30a217"
        }).json()

        try:
            dispatcher.utter_message(text="It's {0} degrees Celsius with {1} in {2}.".format(
                r['main']['temp'], r['weather'][0]['description'], r['name']))
        except:
            dispatcher.utter_message(
                text="Appologies - weather data is incomplete at the minute.")

        return []
