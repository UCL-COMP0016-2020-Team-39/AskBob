import os
import shutil


class ModelGenerator:

    def __init__(self):
        pass

    def get_intent(self, intent: str, plugin: str):
        if plugin == "main":
            return intent
        else:
            return '{}_{}'.format(intent, plugin)

    def get_action(self, action: str, plugin: str):
        if action.startswith('utter_') or action.startswith('validate_'):
            return '{}_{}'.format(action, plugin)
        else:
            return 'action_{}_{}'.format(action, plugin)

    def generate_config_yml(self, location: str):
        with open(location + '/config.yml', 'w') as f:
            f.write("""language: en
pipeline:
  - name: SpacyNLP
    model: "en_core_web_md"
    case_sensitive: False
  - name: SpacyTokenizer
  - name: SpacyFeaturizer
  - name: RegexFeaturizer
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
  url: "http://localhost:5002/api""")

    def generate_endpoints_yml(self, location):
        with open(location + '/credentials.yml', 'w') as f:
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
                f.writelines(['  - {}\n'.format(entity)
                              for entity in config['entities']])
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

            # Rules
            if 'rules' in config or 'skills' in config:
                f.write('\nrules:\n')

                if 'skills' in config:
                    for skill in config['skills']:
                        f.write('  - rule: {}\n    steps:\n      - intent: {}\n'.format(
                            skill['description'] if 'description' in skill else '', self.get_intent(skill['intent'], plugin)))
                        f.writelines(['      - action: {}\n'.format(self.get_action(action, plugin))
                                      for action in skill['actions']])
                        f.write('\n')

                # Rules
                if 'rules' in config:
                    for rule in config['rules']:
                        f.write('  - rule: ' +
                                (rule['description'] if 'description' in rule else '')+'\n    steps:\n')
                        f.writelines(['      - ' + step['type'] + ': ' + step['value'] + '\n'
                                      for step in rule['steps']])
                        f.write('\n')

            # Stories
            """ if 'stories' in config:
                f.write('\nstories:\n')
                for rule in config['stories']:
                    f.write('  - story: ' +
                            (rule['description'] if 'description' in rule else '')+'\n    steps:\n')
                    f.writelines(['      - ' + step['type'] + ': ' + step['step_id'] + '\n'
                                  for step in rule['steps']])
                    f.write('\n') """

    def generate(self, configs, config_location, output_location):
        if os.path.exists(config_location):
            shutil.rmtree(config_location)

        os.makedirs(config_location)

        if not os.path.exists(output_location):
            os.makedirs(output_location)

        self.generate_config_yml(config_location)
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

        for config in configs:
            plugin = config['plugin'] if 'plugin' in config else 'main'
            self.generate_domain(config, domain_path, plugin)
            self.generate_training_data(config, training_path, plugin)

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
