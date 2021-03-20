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
