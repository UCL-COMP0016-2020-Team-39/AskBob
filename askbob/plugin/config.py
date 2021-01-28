import os
import shutil


class ModelGenerator:

    def __init__(self):
        pass

    def generate_config_yml(self, location):
        with open(location + '/config.yml', 'w') as f:
            f.write("""language: en
pipeline:
  - name: SpacyNLP
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
    threshold: 0.6
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
        domain_path = location + '/domain'

        if os.path.exists(domain_path):
            shutil.rmtree(domain_path)

        os.makedirs(domain_path)

        with open(location + '/domain/{}.yml'.format(plugin), 'w') as f:
            f.write('version: "2.0"\n')

            # Intents
            if 'intents' not in config:
                raise RuntimeError("No intents have been registered.")

            f.write('\nintents:\n')
            f.writelines(['  - ' + intent['id'] +
                          '\n' for intent in config['intents']])

            # Responses
            f.write('\nresponses:\n')
            for response in config['responses']:
                f.write('  ' + response['id'] + ': \n')
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
        if os.path.exists(location + '/training'):
            shutil.rmtree(location + '/training')

        os.makedirs(location + '/training')

        with open(location + '/training/{}.yml'.format(plugin), 'w') as f:
            f.write('version: "2.0"\n')

            # NLU
            f.write('\nnlu:\n')
            for intent in config['intents']:
                if 'id' not in intent or 'examples' not in intent:
                    raise RuntimeError("Intents must have an id and examples.")

                f.write('  - intent: ' + intent['id'] + '\n    examples: |\n')
                f.writelines(
                    ['      - ' + example + '\n' for example in intent['examples']])
                f.write('\n')

            # Rules
            if 'rules' in config or 'skills' in config:
                f.write('\nrules:\n')

                if 'skills' in config:
                    for skill in config['skills']:
                        f.write('  - rule: ' +
                                (skill['description'] if 'description' in skill else '')+'\n    steps:\n')
                        f.write('      - intent: ' + skill['intent'] + '\n')

                        f.writelines(['      - action: ' + action + '\n'
                                      for action in skill['actions']])
                        f.write('\n')

                # Rules
                if 'rules' in config:
                    for rule in config['rules']:
                        f.write('  - rule: ' +
                                (rule['description'] if 'description' in rule else '')+'\n    steps:\n')
                        f.writelines(['      - ' + step['type'] + ': ' + step['id'] + '\n'
                                      for step in rule['steps']])
                        f.write('\n')

            # Stories
            if 'stories' in config:
                f.write('\nstories:\n')
                for rule in config['stories']:
                    f.write('  - story: ' +
                            (rule['description'] if 'description' in rule else '')+'\n    steps:\n')
                    f.writelines(['      - ' + step['type'] + ': ' + step['id'] + '\n'
                                  for step in rule['steps']])
                    f.write('\n')

    def generate(self, configs, location, plugin="main"):
        config_location = location + '/config'
        output_location = location + '/models'

        if not os.path.exists(location):
            os.makedirs(location)

        if os.path.exists(config_location):
            shutil.rmtree(config_location)

        os.makedirs(config_location)

        if not os.path.exists(output_location):
            os.makedirs(output_location)

        self.generate_config_yml(config_location)
        self.generate_credentials_yml(config_location)
        self.generate_endpoints_yml(config_location)

        for config in configs:
            self.generate_domain(config, config_location, plugin)
            self.generate_training_data(config, config_location, plugin)

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


if __name__ == '__main__':
    import json
    config = json.load(open('config.json', 'r'))

    mg = ModelGenerator()
    mg.generate([config], "data/rasa")
