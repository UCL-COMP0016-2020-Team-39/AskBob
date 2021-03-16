import os
import shutil
import logging


class ModelGenerator:

    uses_stories: bool = False

    def __init__(self):
        pass

    def get_intent(self, intent: str, plugin: str):
        if plugin == "main":
            return intent
        else:
            return f'{intent}_{plugin}'

    def get_action(self, action: str, plugin: str):
        if action.startswith('utter_') or action.startswith('validate_'):
            return f'{action}_{plugin}'
        else:
            return f'action_{action}_{plugin}'

    def generate_config_yml(self, location: str, rasa_language: str, spacy_model: str):
        with open(location + '/config.yml', 'w') as f:
            f.write(f"""language: {rasa_language}
pipeline:
  - name: SpacyNLP
    model: "{spacy_model}"
    case_sensitive: False
  - name: SpacyTokenizer
  - name: SpacyFeaturizer
  - name: RegexFeaturizer
    case_sensitive: False
  - name: LexicalSyntacticFeaturizer
  - name: CountVectorsFeaturizer
  - name: CountVectorsFeaturizer
    analyzer: char_wb
    min_ngram: 1
    max_ngram: 4
  - name: DIETClassifier
    epochs: 100
  - name: EntitySynonymMapper
  - name: SpacyEntityExtractor
  - name: RegexEntityExtractor
    case_sensitive: False
    use_lookup_tables: True
    use_regexes: True
    "use_word_boundaries": True
  - name: ResponseSelector
    epochs: 100
  - name: FallbackClassifier
    threshold: 0.75
    ambiguity_threshold: 0.1

policies:
  - name: AugmentedMemoizationPolicy
#  - name: TEDPolicy
#    max_history: 5
#    epochs: 100
  - name: RulePolicy

""")

    def generate_credentials_yml(self, location):
        with open(location + '/credentials.yml', 'w') as f:
            f.write("""rasa:
  url: "http://localhost:5002/api\"""")

    def generate_endpoints_yml(self, location):
        with open(location + '/endpoints.yml', 'w') as f:
            f.write("""action_endpoint:
  url: "http://localhost:5055/webhook\"""")

    def generate_domain(self, config, location, plugin):
        with open(os.path.join(location, plugin + '.yml'), 'w') as f:
            f.write('version: "2.0"\n')

            # Intents
            if 'intents' not in config:
                raise RuntimeError("No intents have been registered.")

            f.write('\nintents:\n')
            f.writelines(['  - {}\n'.format(self.get_intent(intent['intent_id'], plugin))
                          for intent in config['intents']])
            f.write('\n')

            if 'entities' in config:
                f.write('\nentities:\n')
                f.writelines([f'  - {entity}\n'
                              for entity in config['entities']])
                f.write('\n')

            if 'slots' in config:
                f.write('\nslots:\n')
                for slot in config['slots']:
                    if 'slot_id' not in slot:
                        raise RuntimeError(
                            "Each slot definition must contain a 'slot_id' field.")

                    if 'type' not in slot:
                        raise RuntimeError(
                            "Each slot definition must contain a 'type' field.")

                    if slot['type'] not in ['text', 'bool', 'categorical', 'float', 'list', 'any']:
                        raise RuntimeError(
                            f"Unknown slot type '{slot['type']}'.")

                    f.write(f"  {slot['slot_id']}:\n")
                    f.write(f"    type: {slot['type']}\n")

                    if 'influence_conversation' in slot:
                        f.write(
                            f"    influence_conversation: {slot['influence_conversation']}\n")

                    if slot['type'] == 'float':
                        if 'min_value' in slot:
                            f.write(f"    min_value: {slot['min_value']}")

                        if 'max_value' in slot:
                            f.write(f"    max_value: {slot['max_value']}")

                    if slot['type'] == 'categorical':
                        if 'values' not in slot or not isinstance(slot['values'], list):
                            raise RuntimeError(
                                "Slot of type 'categorical' must have a 'values' list of acceptable slot values.")

                        f.writelines(
                            [f"      - {value}" for value in slot['values']])

                f.write('\n')

            if 'actions' in config:
                f.write('\nactions:\n')
                f.writelines(['  - {}\n'.format(self.get_action(action, plugin))
                              for action in config['actions']])
                f.write('\n\n')

                # Responses
            if 'responses' in config:
                f.write('\nresponses:\n')
                for response in config['responses']:
                    if 'text' not in response:
                        raise RuntimeError(
                            "There is no 'text' field defined for a response.")

                    f.write('  {}: \n'.format(self.get_action(
                        response['response_id'], plugin)))
                    f.writelines(['    - text: "' + text +
                                  '"\n' for text in response['text']])
                    f.write('\n')

            # Session config
            f.write("""
session_config:
  session_expiration_time: 20
  carry_over_slots_to_new_session: false
""")

    def generate_training_data(self, config, location, plugin):
        with open(os.path.join(location, plugin + '.yml'), 'w') as f:
            f.write('version: "2.0"\n')

            if 'intents' not in config:
                raise RuntimeError("Configurations must have intents.")

            # NLU
            f.write('\nnlu:\n')
            for intent in config['intents']:
                if 'intent_id' not in intent or 'examples' not in intent:
                    raise RuntimeError("Intents must have an id and examples.")

                f.write('  - intent: {}\n    examples: |\n'.format(
                    self.get_intent(intent['intent_id'], plugin)))
                f.writelines(
                    ['      - ' + example + '\n' for example in intent['examples']])
                f.write('\n')

            if 'synonyms' in config:
                for synonym in config['synonyms']:
                    if 'synonym_id' not in synonym or 'examples' not in synonym:
                        raise RuntimeError(
                            "A synonym must have both a 'synonym_id' field and a list of examples under 'examples'.")

                    f.write(
                        '  - synonym: {}\n    examples: |\n'.format(synonym['synonym_id']))
                    f.writelines(
                        ['      - ' + example + '\n' for example in synonym['examples']])
                    f.write('\n')

            if 'regexes' in config:
                for regex in config['regexes']:
                    if 'regex_id' not in regex or 'examples' not in regex:
                        raise RuntimeError(
                            "A regex must have both a 'regex_id' field and a list of examples under 'examples'.")

                    f.write('  - regex: {}\n    examples: |\n'.format(
                        regex['regex_id']))
                    f.writelines(
                        ['      - ' + example + '\n' for example in regex['examples']])
                    f.write('\n')

            if 'lookups' in config:
                for lookup in config['lookups']:
                    if 'lookup_id' not in lookup or 'examples' not in lookup:
                        raise RuntimeError(
                            "A lookup must have both a 'lookup_id' field and a list of examples under 'examples'.")

                    f.write('  - lookup: {}\n    examples: |\n'.format(
                        lookup['lookup_id']))
                    f.writelines(
                        ['      - ' + example + '\n' for example in lookup['examples']])
                    f.write('\n')

            # Rules
            if 'rules' in config or 'skills' in config:
                f.write('\nrules:\n')

                if 'skills' in config:
                    for skill in config['skills']:
                        f.write("  - rule: {}\n    steps:\n      - intent: {}\n".format(
                                skill.get('description', ''), self.get_intent(skill['intent'], plugin)))
                        f.writelines(['      - action: {}\n'.format(self.get_action(action, plugin))
                                      for action in skill['actions']])
                        f.write('\n')

                # Rules
                if 'rules' in config:
                    for rule in config['rules']:
                        f.write(
                            f"  - rule: {rule.get('description', '')}\n    steps:\n")
                        f.writelines([f"      - {step['type']}: {step['value']}\n"
                                      for step in rule['steps']])
                        f.write('\n')

            # Stories
            if 'stories' in config:
                self.uses_stories = True
                f.write('\nstories:\n')
                for story in config['stories']:
                    f.write(
                        '  - story: {}\n    steps:\n'.format(story.get('description', '')))
                    f.writelines(['      - ' + step['type'] + ': ' + step['step_id'] + '\n'
                                  for step in story['steps']])
                    f.write('\n')

    def generate(self, configs, config_location, output_location, rasa_language, spacy_model):
        if os.path.exists(config_location):
            shutil.rmtree(config_location)

        os.makedirs(config_location)

        if not os.path.exists(output_location):
            os.makedirs(output_location)

        self.generate_config_yml(config_location, rasa_language, spacy_model)
        self.generate_credentials_yml(config_location)
        self.generate_endpoints_yml(config_location)

        domain_path = os.path.join(config_location, 'domain')
        if os.path.exists(domain_path):
            shutil.rmtree(domain_path)
        os.makedirs(domain_path)

        training_path = os.path.join(config_location, 'training')
        if os.path.exists(training_path):
            shutil.rmtree(training_path)
        os.makedirs(training_path)

        try:
            for config in configs:
                plugin = config['plugin'] if 'plugin' in config else 'main'
                self.generate_domain(config, domain_path, plugin)
                self.generate_training_data(config, training_path, plugin)
        except Exception as e:
            logging.error(str(e))
            #raise e
            return None

        from rasa import train

        result = train(
            domain=config_location + '/domain',
            config=config_location + '/config.yml',
            training_files=config_location + '/training',
            output=output_location
        )

        if result.code != 0:
            raise RuntimeError("Training could not be completed.")

        return result
