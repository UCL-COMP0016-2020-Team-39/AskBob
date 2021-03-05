from askbob.plugin import action


@action("plugin", "action_name")
class A:
    pass


def test_plugin_decorator_A():
    assert A().name() == 'action_action_name_plugin'


@action("plugin", "validate_action_name")
class B:
    pass


def test_plugin_decorator_validate():
    assert B().name() == 'validate_action_name_plugin'
