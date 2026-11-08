"""Configuration for the EXO client.

Values come from a ``.env`` file (INI format) in the current working directory,
falling back to environment variables for the authentication values. Nothing is
read until one of the functions below is called, so importing ``exo`` never
requires configuration.
"""

from __future__ import annotations

import configparser
import os

AUTH_VARS = ("EXO_USERNAME", "EXO_PASSWORD", "EXO_API_KEY", "EXO_TOKEN")


def _load_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.abspath(""), ".env"))
    return config


def get_auth() -> dict[str, str | None]:
    """Return the four authentication values, or None where unset."""
    config = _load_config()
    return {
        name: config.get("AUTH", name, fallback=None) or os.environ.get(name) for name in AUTH_VARS
    }


def get_base_url() -> str:
    """Return the on-premise API base URL built from ``EXO_IP`` and ``EXO_PORT``."""
    config = _load_config()
    try:
        ip_address = config["DEFAULT"]["EXO_IP"]
        port = config["DEFAULT"]["EXO_PORT"]
    except KeyError as missing:
        raise ValueError(
            f"{missing.args[0]} is not set; add EXO_IP and EXO_PORT to the [DEFAULT] "
            "section of a .env file, or pass base_url explicitly"
        ) from None
    return f"http://{ip_address}:{port}"


def get_logs_directory() -> str:
    return _load_config().get("DEFAULT", "LOGS", fallback="logs")


def get_cache_directory() -> str:
    return _load_config().get("DEFAULT", "CACHE", fallback="caching")
