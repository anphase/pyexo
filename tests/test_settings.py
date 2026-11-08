import re
from pathlib import Path

import pytest

from exo import settings

README = (Path(__file__).resolve().parent.parent / "README.md").read_text()


def test_documented_variables_are_the_ones_settings_reads():
    documented = set(re.findall(r"\b(?:MYOB_)?EXO_[A-Z_]+\b", README))
    assert set(settings.AUTH_VARS) <= documented
    assert not any(name.startswith("MYOB_") for name in documented)
    assert {"EXO_IP", "EXO_PORT"} <= documented


@pytest.mark.parametrize("name", settings.AUTH_VARS)
def test_each_documented_variable_is_read_from_the_environment(name, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv(name, "from-env")
    assert settings.get_auth()[name] == "from-env"


def test_env_file_takes_precedence_over_environment(monkeypatch, tmp_path):
    (tmp_path / ".env").write_text("[AUTH]\nEXO_USERNAME = from-file\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("EXO_USERNAME", "from-env")
    assert settings.get_auth()["EXO_USERNAME"] == "from-file"


def test_missing_values_are_none(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("EXO_TOKEN", raising=False)
    assert settings.get_auth()["EXO_TOKEN"] is None


def test_base_url_from_env_file(monkeypatch, tmp_path):
    (tmp_path / ".env").write_text("[DEFAULT]\nEXO_IP = 10.0.0.1\nEXO_PORT = 8888\n")
    monkeypatch.chdir(tmp_path)
    assert settings.get_base_url() == "http://10.0.0.1:8888"


def test_base_url_requires_configuration(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="EXO_IP"):
        settings.get_base_url()


def test_directories_default_and_override(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    assert settings.get_logs_directory() == "logs"
    assert settings.get_cache_directory() == "caching"
    (tmp_path / ".env").write_text("[DEFAULT]\nLOGS = mylogs\nCACHE = mycache\n")
    assert settings.get_logs_directory() == "mylogs"
    assert settings.get_cache_directory() == "mycache"


def test_percent_signs_in_values_are_not_interpolated(monkeypatch, tmp_path):
    (tmp_path / ".env").write_text("[AUTH]\nEXO_TOKEN = 123AA*%\n")
    monkeypatch.chdir(tmp_path)
    assert settings.get_auth()["EXO_TOKEN"] == "123AA*%"
