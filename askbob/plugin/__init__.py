from typing import Text


def action(plugin: str, name: str):
    """A decorator for Ask Bob plugin actions (implementing the rasa_sdk.Action class).

    Args:
        plugin (str): The plugin name.
        name (str): The action name.
    """

    def wrapper(action):
        def name_method(self) -> Text:
            if name.startswith("validate_"):
                return "{}_{}".format(name, plugin)
            else:
                return "action_{}_{}".format(name, plugin)

        setattr(action, "name", name_method)
        return action

    return wrapper
