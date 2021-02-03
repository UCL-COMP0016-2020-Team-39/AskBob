from typing import Text


def action(plugin, name):
    def wrapper(action):
        def name_method(self) -> Text:
            return "action_{}_{}".format(name, plugin)

        setattr(action, "name", name_method)
        return action

    return wrapper
