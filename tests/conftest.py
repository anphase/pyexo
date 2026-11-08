import json
from pathlib import Path
from typing import Any

import pytest

from exo.auth import Credentials

FIXTURES = Path(__file__).parent / "fixtures"
BASE_URL = "http://exo.test:8888"


def load_fixture(name: str) -> Any:
    return json.loads((FIXTURES / name).read_text())


@pytest.fixture(autouse=True)
def isolated_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Keep a developer's .env file and EXO_* variables out of every test."""
    monkeypatch.chdir(tmp_path)
    for name in ("EXO_USERNAME", "EXO_PASSWORD", "EXO_API_KEY", "EXO_TOKEN"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def credentials() -> Credentials:
    return Credentials("demo", "secret", "key-123", "token-456")


@pytest.fixture
def base_url() -> str:
    return BASE_URL
