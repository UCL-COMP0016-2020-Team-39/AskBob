import pytest

from askbob.plugin.config import ModelGenerator

mg = ModelGenerator(dry_run=True)


def test_model_generator_get_intent():
    assert mg.get_intent(intent='foo', plugin='bar') == 'foo_bar'


def test_model_generator_get_intent_main():
    assert mg.get_intent(intent='foo', plugin='main') == 'foo'


def test_model_generator_get_action():
    assert mg.get_action(action='foo', plugin='bar') == 'action_foo_bar'


def test_model_generator_get_action_utter():
    assert mg.get_action(action='utter_foo', plugin='bar') == 'utter_foo_bar'


def test_model_generator_get_action_validate():
    assert mg.get_action(action='validate_foo',
                         plugin='bar') == 'validate_foo_bar'


def test_model_generator_generate_config(tmp_path):
    location = str(tmp_path)
    mg.generate_config_yml(location, 'en', 'en_core_web_md')
    content = (tmp_path / 'config.yml').read_text()
    assert 'language: en' in content
    assert 'en_core_web_md' in content


def test_model_generator_generate_credentials(tmp_path):
    location = str(tmp_path)
    mg.generate_credentials_yml(location)
    content = (tmp_path / 'credentials.yml').read_text()
    assert 'url:' in content


def test_model_generator_generate_endpoints(tmp_path):
    location = str(tmp_path)
    mg.generate_endpoints_yml(location)
    content = (tmp_path / 'endpoints.yml').read_text()
    assert 'action_endpoint:' in content
    assert 'url:' in content


def test_model_generator_domain_no_intents(tmp_path):
    location = str(tmp_path)
    with pytest.raises(RuntimeError):
        mg.generate_domain({}, location, 'plugin')


def test_model_generator_domain_only_intents(tmp_path):
    location = str(tmp_path)
    mg.generate_domain({
        "intents": [
            {
                "intent_id": "greeting",
                "examples": ["foo", "bar", "baz"]
            }
        ]
    }, location, 'plugin')

    content = (tmp_path / 'plugin.yml').read_text()
    assert "intents" in content
    assert "greeting_plugin" in content


def test_model_generator_domain_entities(tmp_path):
    location = str(tmp_path)
    mg.generate_domain({
        "intents": [
            {
                "intent_id": "greeting",
                "examples": ["foo", "bar", "baz"]
            }
        ],
        "entities": ["entity_foo", "entity_bar", "entity_baz"]
    }, location, 'plugin')

    content = (tmp_path / 'plugin.yml').read_text()
    assert "entities:" in content
    assert "entity_foo" in content
    assert "entity_bar" in content
    assert "entity_baz" in content


def test_model_generator_domain_slots_no_id(tmp_path):
    location = str(tmp_path)
    with pytest.raises(RuntimeError):
        mg.generate_domain({
            "intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}],
            "slots": [{}]
        }, location, 'plugin')


def test_model_generator_domain_slots_no_type(tmp_path):
    location = str(tmp_path)
    with pytest.raises(RuntimeError):
        mg.generate_domain({
            "intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}],
            "slots": [{"slot_id": "foo"}]
        }, location, 'plugin')


def test_model_generator_domain_slots_invalid_type(tmp_path):
    location = str(tmp_path)
    with pytest.raises(RuntimeError):
        mg.generate_domain({
            "intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}],
            "slots": [{"slot_id": "foo", "type": "bar"}]
        }, location, 'plugin')


def test_model_generator_domain_slots_text(tmp_path):
    location = str(tmp_path)
    mg.generate_domain({
        "intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}],
        "slots": [{"slot_id": "foo", "type": "text", "influence_conversation": "false"}]
    }, location, 'plugin')

    content = (tmp_path / 'plugin.yml').read_text()
    assert 'influence_conversation: false' in content


def test_model_generator_domain_slots_float(tmp_path):
    location = str(tmp_path)
    mg.generate_domain({
        "intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}],
        "slots": [{"slot_id": "foo", "type": "float", "min_value": "0.0", "max_value": "1.0", "influence_conversation": "true"}]
    }, location, 'plugin')

    content = (tmp_path / 'plugin.yml').read_text()
    assert 'influence_conversation: true' in content
    assert 'min_value: 0.0' in content
    assert 'max_value: 1.0' in content


def test_model_generator_domain_slots_float_no_min_max(tmp_path):
    location = str(tmp_path)
    mg.generate_domain({
        "intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}],
        "slots": [{"slot_id": "foo", "type": "float", "influence_conversation": "true"}]
    }, location, 'plugin')

    content = (tmp_path / 'plugin.yml').read_text()
    assert 'type: float' in content
    assert 'influence_conversation: true' in content


def test_model_generator_domain_slots_float_no_min_max_float(tmp_path):
    location = str(tmp_path)
    mg.generate_domain({
        "intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}],
        "slots": [{"slot_id": "foo", "type": "float"}]
    }, location, 'plugin')

    content = (tmp_path / 'plugin.yml').read_text()
    assert 'type: float' in content


def test_model_generator_domain_slots_categorical(tmp_path):
    location = str(tmp_path)
    mg.generate_domain({
        "intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}],
        "slots": [{"slot_id": "foo", "type": "categorical", "values": ["qwerty", "uiop"], "influence_conversation": "true"}]
    }, location, 'plugin')

    content = (tmp_path / 'plugin.yml').read_text()
    assert 'influence_conversation: true' in content
    assert '- qwerty' in content
    assert '- uiop' in content


def test_model_generator_domain_slots_categorical_missing_values(tmp_path):
    location = str(tmp_path)
    with pytest.raises(RuntimeError):
        mg.generate_domain({
            "intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}],
            "slots": [{"slot_id": "foo", "type": "categorical", "influence_conversation": "true"}]
        }, location, 'plugin')


def test_model_generator_domain_actions(tmp_path):
    location = str(tmp_path)
    mg.generate_domain({
        "intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}],
        "actions": ["fetch_foo", "fetch_bar"]
    }, location, 'plugin')

    content = (tmp_path / 'plugin.yml').read_text()
    assert '- action_fetch_foo_plugin' in content
    assert '- action_fetch_bar_plugin' in content


def test_model_generator_domain_responses(tmp_path):
    location = str(tmp_path)
    mg.generate_domain({
        "intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}],
        "responses": [{"response_id": "utter_foo", "text": ["foo"]}]
    }, location, 'plugin')

    content = (tmp_path / 'plugin.yml').read_text()
    assert '- text: "foo"' in content


def test_model_generator_domain_responses_missing_text(tmp_path):
    location = str(tmp_path)
    with pytest.raises(RuntimeError):
        mg.generate_domain({
            "intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}],
            "responses": [{"response_id": "utter_foo"}]
        }, location, 'plugin')


def test_model_generator_training_data_no_intents(tmp_path):
    location = str(tmp_path)
    with pytest.raises(RuntimeError):
        mg.generate_training_data({}, location, 'plugin')


def test_model_generator_training_data_no_intent_id(tmp_path):
    location = str(tmp_path)
    with pytest.raises(RuntimeError):
        mg.generate_training_data({
            "intents": [{}]
        }, location, 'plugin')


def test_model_generator_training_data_no_intent_examples(tmp_path):
    location = str(tmp_path)
    with pytest.raises(RuntimeError):
        mg.generate_training_data({
            "intents": [{"intent_id": "foo"}]
        }, location, 'plugin')


def test_model_generator_training_data_intents(tmp_path):
    location = str(tmp_path)
    mg.generate_training_data({
        "intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}]
    }, location, 'plugin')

    content = (tmp_path / 'plugin.yml').read_text()
    assert 'greeting_plugin' in content
    assert 'foo' in content
    assert 'bar' in content
    assert 'baz' in content


def test_model_generator_training_data_synonyms_no_id(tmp_path):
    location = str(tmp_path)
    with pytest.raises(RuntimeError):
        mg.generate_training_data({
            "intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}],
            "synonyms": [{}]
        }, location, 'plugin')


def test_model_generator_training_data_synonyms_no_examples(tmp_path):
    location = str(tmp_path)
    with pytest.raises(RuntimeError):
        mg.generate_training_data({
            "intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}],
            "synonyms": [{"synonym_id": "foo"}]
        }, location, 'plugin')


def test_model_generator_training_data_synonyms(tmp_path):
    location = str(tmp_path)
    mg.generate_training_data({
        "intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}],
        "synonyms": [{"synonym_id": "id", "examples": ["qwerty", "uiop"]}]
    }, location, 'plugin')

    content = (tmp_path / 'plugin.yml').read_text()
    assert '- synonym: id' in content
    assert 'qwerty' in content
    assert 'uiop' in content
    assert 'examples:' in content


def test_model_generator_training_data_regexes_no_id(tmp_path):
    location = str(tmp_path)
    with pytest.raises(RuntimeError):
        mg.generate_training_data({
            "intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}],
            "regexes": [{}]
        }, location, 'plugin')


def test_model_generator_training_data_regexes_no_examples(tmp_path):
    location = str(tmp_path)
    with pytest.raises(RuntimeError):
        mg.generate_training_data({
            "intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}],
            "regexes": [{"regex_id": "foo"}]
        }, location, 'plugin')


def test_model_generator_training_data_regexes(tmp_path):
    location = str(tmp_path)
    mg.generate_training_data({
        "intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}],
        "regexes": [{"regex_id": "id", "examples": ["qwerty", "uiop"]}]
    }, location, 'plugin')

    content = (tmp_path / 'plugin.yml').read_text()
    assert '- regex: id' in content
    assert 'qwerty' in content
    assert 'uiop' in content
    assert 'examples:' in content


def test_model_generator_training_data_lookups_no_id(tmp_path):
    location = str(tmp_path)
    with pytest.raises(RuntimeError):
        mg.generate_training_data({
            "intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}],
            "lookups": [{}]
        }, location, 'plugin')


def test_model_generator_training_data_lookups_no_examples(tmp_path):
    location = str(tmp_path)
    with pytest.raises(RuntimeError):
        mg.generate_training_data({
            "intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}],
            "lookups": [{"lookup_id": "foo"}]
        }, location, 'plugin')


def test_model_generator_training_data_lookups(tmp_path):
    location = str(tmp_path)
    mg.generate_training_data({
        "intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}],
        "lookups": [{"lookup_id": "id", "examples": ["qwerty", "uiop"]}]
    }, location, 'plugin')

    content = (tmp_path / 'plugin.yml').read_text()
    assert '- lookup: id' in content
    assert 'qwerty' in content
    assert 'uiop' in content
    assert 'examples:' in content


def test_model_generator_training_data_skills(tmp_path):
    location = str(tmp_path)
    mg.generate_training_data({
        "intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}],
        "skills": [{"intent": "greeting", "actions": ["utter_foo"]}]
    }, location, 'plugin')

    content = (tmp_path / 'plugin.yml').read_text()
    assert 'intent: greeting_plugin' in content
    assert 'utter_foo_plugin' in content


def test_model_generator_training_data_rules(tmp_path):
    location = str(tmp_path)
    mg.generate_training_data({
        "intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}],
        "rules": [{"description": "description", "steps": [
            {"type": "intent", "value": "greeting"},
            {"type": "action", "value": "utter_foo"}
        ]}]
    }, location, 'plugin')

    content = (tmp_path / 'plugin.yml').read_text()
    assert 'intent: greeting_plugin' in content
    assert 'utter_foo_plugin' in content


def test_model_generator_training_data_stories(tmp_path):
    location = str(tmp_path)
    mg.generate_training_data({
        "intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}],
        "stories": [{"description": "description", "steps": [
            {"type": "intent", "step_id": "greeting"},
            {"type": "action", "step_id": "utter_foo"}
        ]}]
    }, location, 'plugin')

    content = (tmp_path / 'plugin.yml').read_text()
    assert 'intent: greeting_plugin' in content
    assert 'utter_foo_plugin' in content


def test_model_generator_generate(tmp_path):
    config_location = tmp_path / 'config'
    config_location.mkdir()

    output_location = tmp_path / 'models'
    output_location.mkdir()

    mg.generate([{"intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}]}],
                str(config_location), str(output_location), 'en', 'en_core_web_md')


def test_model_generator_generate_nonexistent_directories(tmp_path):
    config_location = tmp_path / 'config'
    output_location = tmp_path / 'models'

    mg.generate([{"intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}]}],
                str(config_location), str(output_location), 'en', 'en_core_web_md')


def test_model_generator_generate_preexisting_domain_and_training(tmp_path):
    config_location = tmp_path / 'config'
    config_location.mkdir()
    (config_location / 'domain').mkdir()
    (config_location / 'domain' / 'foo.yml').write_text("qwerty")
    (config_location / 'training').mkdir()
    (config_location / 'training' / 'foo.yml').write_text("qwerty")
    output_location = tmp_path / 'models'

    mg.generate([{"intents": [{"intent_id": "greeting", "examples": ["foo", "bar", "baz"]}]}],
                str(config_location), str(output_location), 'en', 'en_core_web_md')


def test_model_generator_generate_error(tmp_path):
    config_location = tmp_path / 'config'
    output_location = tmp_path / 'models'

    assert mg.generate([{}], str(config_location), str(
        output_location), 'en', 'en_core_web_md') is None


@pytest.mark.filterwarnings("ignore:.*")
def test_model_generator_generate_rasa_model(tmp_path):
    config_location = tmp_path / 'config'
    output_location = tmp_path / 'models'

    model_generator = ModelGenerator()
    assert model_generator.generate([{
        "intents": [
            {
                "intent_id": "ask_hello",
                "examples": [
                    "Hello",
                    "Hi",
                    "Hey",
                    "Howdy",
                    "Howdy, partner"
                ]
            },
            {
                "intent_id": "ask_goodbye",
                "examples": [
                    "Goodbye",
                    "Good bye",
                    "Bye",
                    "Bye bye",
                    "See you",
                    "See you later",
                    "In a bit!",
                    "Catch you later!"
                ]
            }
        ],
        "responses": [
            {
                "response_id": "utter_greeting",
                "text": [
                    "Hi there!",
                    "Hey - nice to meet you!",
                    "Hey there!"
                ]
            },
            {
                "response_id": "utter_goodbye",
                "text": [
                    "See you later!",
                    "Bye!",
                    "In a while, crocodile!"
                ]
            }
        ],
        "skills": [
            {
                "description": "Greet the user",
                "intent": "ask_hello",
                "actions": [
                    "utter_greeting"
                ]
            },
            {
                "description": "Say goodbye to the user.",
                "intent": "ask_goodbye",
                "actions": [
                    "utter_goodbye"
                ]
            }
        ]
    }
    ], str(config_location), str(
        output_location), 'en', 'en_core_web_md').code == 0
