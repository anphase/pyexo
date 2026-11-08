import importlib
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SETTINGS_SRC = (ROOT / "exo" / "settings.py").read_text()
README = (ROOT / "README.md").read_text()

AUTH_VARS = ("EXO_USERNAME", "EXO_PASSWORD", "EXO_API_KEY", "EXO_TOKEN")


def test_settings_reads_the_documented_environment_variables():
    read_by_settings = set(re.findall(r"os\.environ\.get\('([A-Z_]+)'\)", SETTINGS_SRC))
    assert read_by_settings == set(AUTH_VARS)
    documented = set(re.findall(r"\b(?:MYOB_)?EXO_[A-Z_]+\b", README))
    assert read_by_settings <= documented
    assert not any(name.startswith("MYOB_") for name in documented)


def test_environment_values_are_picked_up(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text("[DEFAULT]\nEXO_IP = 10.0.0.1\nEXO_PORT = 8888\n")
    monkeypatch.chdir(tmp_path)
    for name in AUTH_VARS:
        monkeypatch.setenv(name, "value-" + name)
    sys.modules.pop("exo.settings", None)
    settings = importlib.import_module("exo.settings")
    assert settings.EXO_USERNAME == "value-EXO_USERNAME"
    assert settings.EXO_PASSWORD == "value-EXO_PASSWORD"
    assert settings.EXO_API_KEY == "value-EXO_API_KEY"
    assert settings.EXO_TOKEN == "value-EXO_TOKEN"
    assert settings.EXO_URL == "http://10.0.0.1:8888"


@pytest.fixture(autouse=True)
def _forget_settings():
    yield
    sys.modules.pop("exo.settings", None)
