import json
from pathlib import Path
from typing import Any

import pytest

from exo.auth import Credentials

FIXTURES = Path(__file__).parent / "fixtures"
BASE_URL = "http://exo.test:8888"


def load_fixture(name: str) -> Any:
    return json.loads((FIXTURES / name).read_text())


@pytest.fixture
def credentials() -> Credentials:
    return Credentials("demo", "secret", "key-123", "token-456")


@pytest.fixture
def base_url() -> str:
    return BASE_URL
