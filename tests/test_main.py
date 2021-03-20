import sys
from unittest.mock import patch
from askbob.__main__ import main


def test_main_config_parser_fail():
    with patch.object(sys, 'argv', [sys.argv[0]] + ['-c', 'non_existent_config_file.ini']):
        assert main() == False


def test_main_config_missing_rasa(tmp_path):
    f = tmp_path / "test_main_config.ini"
    f.write_text("")

    with patch.object(sys, 'argv', [sys.argv[0]] + ['-c', str(f)]):
        assert main() == False


def test_main_config_missing_rasa_model(tmp_path):
    f = tmp_path / "test_main_config.ini"
    f.write_text("""
[Rasa]
foo = bar
""")

    with patch.object(sys, 'argv', [sys.argv[0]] + ['-c', str(f)]):
        assert main() == False


def test_main_config_voice_and_not_serve(tmp_path):
    f = tmp_path / "test_main_config.ini"
    f.write_text("""
[Rasa]
model = foo
""")

    with patch.object(sys, 'argv', [sys.argv[0]] + ['-c', str(f), '-v']):
        assert main() == False


def test_main_config_missing_server(tmp_path):
    f = tmp_path / "test_main_config.ini"
    f.write_text("""
[Rasa]
model = tests/files/models
""")

    with patch.object(sys, 'argv', [sys.argv[0]] + ['-c', str(f), '-s', '-v']):
        assert main() == False
