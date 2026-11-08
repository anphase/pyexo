import base64
import os
import subprocess
import sys

import pytest

from exo.auth import Credentials
from exo.exceptions import ExoIncompleteAuthorisation


def test_headers_use_plain_base64_basic_auth():
    headers = Credentials("demo", "secret", "key-123", "token-456").auth_headers
    token = headers["Authorization"].removeprefix("Basic ")
    assert base64.b64decode(token) == b"demo:secret"
    assert "b'" not in headers["Authorization"]
    assert headers["x-myobapi-key"] == "key-123"
    assert headers["x-myobapi-exotoken"] == "token-456"


def test_credentials_fall_back_to_environment(monkeypatch):
    for name, value in {
        "EXO_USERNAME": "envuser",
        "EXO_PASSWORD": "envpass",
        "EXO_API_KEY": "envkey",
        "EXO_TOKEN": "envtoken",
    }.items():
        monkeypatch.setenv(name, value)
    headers = Credentials().auth_headers
    assert base64.b64decode(headers["Authorization"][6:]) == b"envuser:envpass"
    assert headers["x-myobapi-key"] == "envkey"
    assert headers["x-myobapi-exotoken"] == "envtoken"


def test_incomplete_credentials_raise_a_helpful_error(monkeypatch):
    for name in ("EXO_USERNAME", "EXO_PASSWORD", "EXO_API_KEY", "EXO_TOKEN"):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(ExoIncompleteAuthorisation) as info:
        Credentials("demo", "secret")
    assert "EXO_API_KEY" in str(info.value)
    assert "EXO_TOKEN" in str(info.value)


def test_importing_the_package_needs_no_configuration(tmp_path):
    result = subprocess.run(
        [sys.executable, "-c", "import exo, exo.api"],
        cwd=tmp_path,
        env={"PATH": os.environ.get("PATH", ""), "PYTHONPATH": os.pathsep.join(sys.path)},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
