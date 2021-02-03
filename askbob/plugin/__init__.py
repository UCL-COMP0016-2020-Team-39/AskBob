from typing import Text


def action(plugin, name):
    def wrapper(action):
        def name_method(self) -> Text:
            return "action_{}_{}".format(plugin, name)

        setattr(action, "name", name_method)
        return action

    return wrapper
