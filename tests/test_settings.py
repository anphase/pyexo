import re
from pathlib import Path

import pytest

from exo import settings

README = (Path(__file__).resolve().parent.parent / "README.md").read_text()


def test_documented_variables_are_the_ones_settings_reads():
    documented = set(re.findall(r"\b(?:MYOB_)?EXO_[A-Z_]+\b", README))
    assert set(settings.AUTH_VARS) <= documented
    assert not any(name.startswith("MYOB_") for name in documented)
    assert {"EXO_BASE_URL", "EXO_IP", "EXO_PORT"} <= documented


@pytest.mark.parametrize("name", settings.AUTH_VARS)
def test_each_documented_variable_is_read_from_the_environment(name, monkeypatch):
    monkeypatch.setenv(name, "from-env")
    assert settings.get_auth()[name] == "from-env"


def test_environment_takes_precedence_over_env_file(monkeypatch, tmp_path):
    (tmp_path / ".env").write_text("EXO_USERNAME=from-file\nEXO_TOKEN=file-token\n")
    monkeypatch.setenv("EXO_USERNAME", "from-env")
    auth = settings.get_auth()
    assert auth["EXO_USERNAME"] == "from-env"
    assert auth["EXO_TOKEN"] == "file-token"


def test_empty_environment_value_does_not_hide_the_env_file(monkeypatch, tmp_path):
    (tmp_path / ".env").write_text("EXO_PASSWORD=from-file\n")
    monkeypatch.setenv("EXO_PASSWORD", "")
    monkeypatch.setenv("EXO_TOKEN", "")
    auth = settings.get_auth()
    assert auth["EXO_PASSWORD"] == "from-file"
    assert auth["EXO_TOKEN"] == ""


def test_missing_values_are_none():
    assert settings.get_auth()["EXO_TOKEN"] is None


def test_dotenv_syntax(tmp_path):
    (tmp_path / ".env").write_text(
        "# a comment\n"
        "\n"
        "not a setting\n"
        "EXO_USERNAME = demo\n"
        "export EXO_PASSWORD='pa ss#word'\n"
        'EXO_API_KEY="key" # trailing comment\n'
        "EXO_TOKEN=123AA*% # comment\n"
    )
    assert settings.get_auth() == {
        "EXO_USERNAME": "demo",
        "EXO_PASSWORD": "pa ss#word",
        "EXO_API_KEY": "key",
        "EXO_TOKEN": "123AA*%",
    }


def test_percent_signs_in_values_are_kept(tmp_path):
    (tmp_path / ".env").write_text("EXO_TOKEN=123AA*%\n")
    assert settings.get_auth()["EXO_TOKEN"] == "123AA*%"


def test_base_url_precedence(monkeypatch, tmp_path):
    (tmp_path / ".env").write_text("EXO_IP=10.0.0.1\nEXO_PORT=8888\n")
    assert settings.get_base_url() == "http://10.0.0.1:8888"
    (tmp_path / ".env").write_text(
        "EXO_IP=10.0.0.1\nEXO_PORT=8888\nEXO_BASE_URL=https://file.test\n"
    )
    assert settings.get_base_url() == "https://file.test"
    monkeypatch.setenv("EXO_BASE_URL", "https://exo.api.myob.com")
    assert settings.get_base_url() == "https://exo.api.myob.com"


def test_base_url_requires_configuration(monkeypatch):
    with pytest.raises(ValueError, match="EXO_BASE_URL"):
        settings.get_base_url()
    monkeypatch.setenv("EXO_IP", "10.0.0.1")
    with pytest.raises(ValueError, match="EXO_IP"):
        settings.get_base_url()


def test_legacy_ini_file_still_works_with_a_deprecation_warning(tmp_path):
    (tmp_path / ".env").write_text(
        "[DEFAULT]\nEXO_IP = 10.0.0.1\nEXO_PORT = 8888\nLOGS = logs\n"
        "[AUTH]\nexo_username = demo\nEXO_TOKEN = 123AA*%\n"
    )
    with pytest.warns(DeprecationWarning, match="INI-style"):
        auth = settings.get_auth()
    assert auth["EXO_USERNAME"] == "demo"
    assert auth["EXO_TOKEN"] == "123AA*%"
    with pytest.warns(DeprecationWarning):
        assert settings.get_base_url() == "http://10.0.0.1:8888"


def test_unreadable_env_file_is_ignored(tmp_path):
    (tmp_path / ".env").mkdir()
    assert settings.get_auth()["EXO_USERNAME"] is None


def test_legacy_ini_warning_is_attributed_to_the_caller(tmp_path):
    (tmp_path / ".env").write_text("[DEFAULT]\nEXO_IP = 10.0.0.1\nEXO_PORT = 8888\n")
    with pytest.warns(DeprecationWarning) as record:
        settings.get_base_url()
    assert record[0].filename == __file__
