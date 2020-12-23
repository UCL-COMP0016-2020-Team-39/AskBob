class Action:

    def __init__(self):
        pass

    text = ""

    def execute(self):
        return self.text


class UnknownAction(Action):
    def execute(self):
        return "I'm sorry; I'm not quite sure what you mean by that."
