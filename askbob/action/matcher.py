import spacy

from askbob.action.action import Action


class Matcher:

    action_hooks = [""]

    def __init__(self):
        self.nlp = spacy.load('en_core_web_md')

    def match(self, text: str):
        doc = self.nlp(text)

        # NLP

        action = Action()
        action.text = ' '.join(t.text for t in doc)
        return action
