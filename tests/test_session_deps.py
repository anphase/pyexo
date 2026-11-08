import tomllib
from pathlib import Path

PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"


def test_dependencies_cover_the_urllib3_2_api_the_session_module_imports():
    deps = tomllib.loads(PYPROJECT.read_text())["project"]["dependencies"]
    assert "requests>=2.32" in deps
    assert "urllib3>=2" in deps
