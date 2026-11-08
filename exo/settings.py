"""Configuration for the EXO client.

Each value is looked up in the process environment first, then in a ``.env`` file
in the current working directory. (Constructor arguments, handled by the callers,
take precedence over both.) Nothing is read until one of the functions below is
called, so importing ``exo`` never requires configuration.

The ``.env`` file uses the usual ``KEY=VALUE`` lines. The INI-style file that
pyexo 0.1 and 0.2 read (``[DEFAULT]`` and ``[AUTH]`` sections) is still understood
for now but is deprecated.
"""

from __future__ import annotations

import configparser
import os
import re
import sys
import warnings
from pathlib import Path

AUTH_VARS = ("EXO_USERNAME", "EXO_PASSWORD", "EXO_API_KEY", "EXO_TOKEN")

_SECTION = re.compile(r"^\s*\[[^\]]+\]\s*$", re.MULTILINE)
_QUOTED = re.compile(r"""^(["'])(.*)\1\s*(?:\s#.*)?$""")
_INLINE_COMMENT = re.compile(r"\s+#.*$")


def _warn_deprecated(message: str) -> None:
    """Warn at the first stack frame outside this package.

    A fixed ``stacklevel`` would land inside ``exo`` (the depth varies with the caller:
    ``Credentials()``, ``Exo()``, ``Manager()``), and ``DeprecationWarning`` is hidden by
    default unless it is attributed to ``__main__``.
    """
    package = str(Path(__file__).parent)
    frame = sys._getframe()
    level = 1
    while frame.f_back is not None and frame.f_code.co_filename.startswith(package):
        frame = frame.f_back
        level += 1
    warnings.warn(message, DeprecationWarning, stacklevel=level)


def _parse_dotenv(text: str) -> dict[str, str]:
    """Parse ``KEY=VALUE`` lines: ``#`` comments, ``export`` prefix, quoted values."""
    values: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip().removeprefix("export ").strip()
        value = value.strip()
        quoted = _QUOTED.match(value)
        values[key] = quoted.group(2) if quoted else _INLINE_COMMENT.sub("", value)
    return values


def _parse_legacy_ini(text: str) -> dict[str, str]:
    # interpolation=None: passwords and tokens may legitimately contain "%".
    config = configparser.ConfigParser(interpolation=None)
    config.read_string(text)
    values = {key.upper(): value for key, value in config.defaults().items()}
    for section in config.sections():
        values.update({key.upper(): value for key, value in config[section].items()})
    return values


def _read_env_file() -> dict[str, str]:
    path = Path.cwd() / ".env"
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError:
        return {}
    if _SECTION.search(text):
        _warn_deprecated(
            f"{path} uses the INI-style format with [DEFAULT]/[AUTH] sections, which is "
            "deprecated; use plain KEY=VALUE lines instead"
        )
        return _parse_legacy_ini(text)
    return _parse_dotenv(text)


def _lookup(names: tuple[str, ...]) -> dict[str, str | None]:
    """Map each name to its environment value, else its ``.env`` value, else None."""
    file_values = _read_env_file()
    return {name: os.environ.get(name, file_values.get(name)) for name in names}


def get_auth() -> dict[str, str | None]:
    """Return the four authentication values, or None where unset."""
    return _lookup(AUTH_VARS)


def get_base_url() -> str:
    """Return the API base URL: ``EXO_BASE_URL``, else ``http://EXO_IP:EXO_PORT``."""
    names = ("EXO_BASE_URL", "EXO_IP", "EXO_PORT")
    base_url, ip_address, port = _lookup(names).values()
    if base_url:
        return base_url
    if not (ip_address and port):
        raise ValueError(
            "no base URL is configured; set EXO_BASE_URL (or EXO_IP and EXO_PORT) in the "
            "environment or a .env file, or pass base_url explicitly"
        )
    return f"http://{ip_address}:{port}"
